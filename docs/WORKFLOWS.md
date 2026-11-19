# ⚙️ Các workflow tự động

Tài liệu mô tả các GitHub Actions đang chạy trong repo `standardizeparadigm/standardizeparadigm`.

**Nguyên tắc chung:** mọi hình đều do workflow vẽ và **commit ngay vào repo** — không gọi server bên thứ ba, không bao giờ bị rate-limit hay lỗi 503. Tất cả action đều ghim phiên bản (`@vN`) và có `permissions` tối thiểu.

## Bảng lịch chạy

| Workflow | Lịch (UTC) | Giờ Việt Nam | Việc làm |
| :-- | :-- | :-- | :-- |
| `live-clock.yml` | `*/5 * * * *` | mỗi 5 phút | `assets/live-clock.svg` |
| `profile-3d.yml` | `*/30 * * * *` + cổng 24h | mỗi 30 phút kiểm tra | `profile-3d-contrib/*.svg` khi có push mới |
| `profile-cards.yml` | `15 */3 * * *` | 8 lần/ngày | `stats`, `top-langs`, `hero`, `activity` (chỉ ghi khi đổi) |
| `readme-tend.yml` | `45 */3 * * *` | 8 lần/ngày | con dấu `TENDED_AT` |
| `status.yml` | `*/15 * * * *` + `workflow_run` | mỗi 15 phút | `assets/status.svg` |
| `health.yml` | push/PR + `0 23 * * *` | 06:00 hằng ngày | test + kiểm tra repo |
| `welcome.yml` | theo sự kiện | — | chào issue/PR mới |

### Chọn nhịp thế nào

Một câu hỏi duy nhất quyết định nhịp: **ảnh này đổi nhanh đến đâu?**

| Loại dữ liệu | Đổi khi nào | Nhịp hợp lý |
| :-- | :-- | :-- |
| Giờ, lời chào, tiến độ ngày | mỗi phút | `*/5` (sàn của GitHub) |
| Số contribution, biểu đồ 3D | khi bạn push hoặc sang ngày mới | 30 phút + cổng 24h |
| Star, fork, ngôn ngữ | vài ngày một lần | 3 giờ |
| Trạng thái workflow | mỗi khi có lượt chạy xong | 15 phút + `workflow_run` |

Hai workflow ghi file cùng lúc sẽ giành nhau `git push`, nên các nhịp được
**lệch phút**: thẻ số liệu ở phút 15, README ở phút 45. Cơ chế push có sẵn
vòng thử lại 3 lần, nhưng phòng tránh từ đầu vẫn rẻ hơn.

> GitHub Actions **không hỗ trợ cron mỗi phút** — chu kỳ ngắn nhất là `*/5`. Vì vậy phần "chạy liên tục" được lo bằng hoạt ảnh ngay trong SVG (CSS/SMIL), còn workflow chỉ vẽ lại để ảnh không bị lệch số liệu.

---

## 1. GitHub Profile 3D Contrib — `profile-3d.yml`

Biểu đồ contribution dạng khối 3D, lưu vào `profile-3d-contrib/`.

- **File ảnh:** `profile-3d-contrib/profile-night-rainbow.svg` (và 9 giao diện khác)
- **Chạy:** `*/5 * * * *` (mỗi 5 phút) · `workflow_dispatch` · khi sửa chính file workflow.
- **Cổng thông minh:** mỗi lượt, một bước shell so *lần ảnh 3D thật sự đổi* (`git log -1 -- profile-3d-contrib`) với *PushEvent* trên GitHub. Có push mới, hoặc đã quá 24 giờ → vẽ lại; còn lại → thoát trong vài giây để không đốt hàng giờ runner mỗi ngày.
- Vì sao không so theo "lần chạy gần nhất": một lượt bị cổng bỏ qua **vẫn tính là chạy thành công**, nên mốc 24 giờ sẽ không bao giờ tới và ảnh sẽ đứng im mãi. So theo `git log` là đo đúng thứ cần đo.
- **Chống lỗi:** SVG sinh ra được parse XML trước khi commit; bỏ qua commit của bot để không lặp vô hạn.

## 2. Profile Cards (LTS) — `profile-cards.yml` + `scripts/generate_cards.py`

Vẽ bằng Python thuần, không cần thư viện ngoài:

| File | Nội dung |
| :-- | :-- |
| `assets/stats.svg` | stars, forks, repos, followers, following, commits + vòng rank |
| `assets/top-langs.svg` | ngôn ngữ dùng nhiều nhất, thanh xếp chồng + thanh tiến độ |
| `assets/hero.svg` | ảnh bìa động: gradient, quỹ đạo, hiệu ứng gõ chữ |
| `assets/activity.svg` | 14 ngày gần nhất, chuỗi ngày, tổng contribution |
| `assets/divider.svg` | đường kẻ động dùng giữa các mục |
| `assets/footer.svg` | dải sóng cuối trang |
| `assets/status.svg` | dải trạng thái 7 workflow (do `status.yml` vẽ) |

- **Chạy:** `*/10 * * * *` (mỗi 10 phút) · `workflow_dispatch` · khi `scripts/**` thay đổi.
- **`--smart`:** mỗi ảnh mang một dấu `<!-- data:… -->` là vân tay của dữ liệu đã dùng. Lượt sau, nếu vân tay không đổi thì **không ghi file, không commit** — trang vẫn được kiểm tra mỗi 10 phút mà lịch sử git không đầy commit rỗng. Ảnh thiết kế (`hero`, `divider`, `footer`) vẽ lại mỗi giờ một lần.
- **Dữ liệu:** `GITHUB_TOKEN` có sẵn của repo → quota riêng, không chia sẻ với hàng nghìn repo khác. Thẻ `activity` dùng GraphQL; thiếu dữ liệu thì giữ ảnh cũ chứ không làm đỏ workflow.
- **Chế độ `--strict`:** API lỗi là workflow báo đỏ ngay, không âm thầm giữ ảnh cũ.
- **An toàn:** ghi file kiểu *atomic* (file tạm rồi `os.replace`), nên mất mạng giữa chừng thì ảnh cũ vẫn nguyên vẹn.

Cờ hữu ích của `scripts/generate_cards.py`:

```bash
python3 scripts/generate_cards.py --demo --all            # ảnh mẫu, không gọi API
python3 scripts/generate_cards.py --cards --strict        # stats + langs, lỗi là exit 1
python3 scripts/generate_cards.py --theme ocean --lang en # đổi bảng màu / ngôn ngữ
python3 scripts/generate_cards.py --list-themes           # 6 bảng màu có sẵn
```

## 3. Live Clock — `live-clock.yml`

Vẽ lại `assets/live-clock.svg`: đồng hồ Việt Nam (UTC+7), lời chào theo giờ, thứ + ngày, tiến độ trong ngày.

- **Chạy:** `*/5 * * * *` — chu kỳ ngắn nhất GitHub Actions hỗ trợ. Các lượt theo lịch có thể trễ vài phút khi hệ thống tải cao.
- **Không gọi API** → mỗi lượt chỉ vài giây, không tốn quota.
- Kim đồng hồ **tự quay bằng CSS/SMIL** giữa hai lần cập nhật, nên nhìn luôn "sống".

## 4. README Garden — `readme-tend.yml`

- Cập nhật con dấu `<!-- TENDED_AT: ... -->` ở cuối README (ngày **và giờ phút**, giờ Việt Nam).
- Kiểm tra `assets/` và `profile-3d-contrib/` còn đủ file.
- **Chạy:** `0 */3 * * *` (mỗi 3 giờ) · `workflow_dispatch` · khi README thay đổi. Con dấu vì thế không bao giờ cũ quá 3 giờ mà chỉ tốn 8 lượt/ngày.

## 5. Repo Health — `health.yml` + `scripts/check_repo.py`

"Bác sĩ" của repo, chạy mỗi lần push/PR và 06:00 mỗi ngày:

- Chạy **hơn 100 unit test** (`python3 -m unittest discover -s scripts/tests -t scripts`)
- Thử vẽ lại toàn bộ SVG với **6 bảng màu × 2 ngôn ngữ** rồi parse XML từng file
- Chữ có lỗi encoding (ký tự hỏng, chữ Hán/Hàn lạc vào, mojibake)
- URL có `%`-escape sai hoặc giải mã ra UTF-8 không hợp lệ
- Anchor `#mục` và đường dẫn `./...` trong Markdown có tồn tại
- Workflow YAML parse được, cron đủ 5 trường, action có phiên bản
- Mọi file Python biên dịch được

Chạy tay: `python3 scripts/check_repo.py`

## 6. Welcome New Contributors — `welcome.yml`

Tự bình luận chào mừng khi có issue/PR mới. Bỏ qua tài khoản bot, chỉ chào **một lần** cho mỗi issue/PR.

---

## Chạy lại ngay

1. Vào repo → tab **Actions**.
2. Chọn workflow ở thanh bên trái.
3. **Run workflow** → chọn nhánh → **Run workflow**.
4. Đợi xong, tải lại trang chủ là thấy ảnh mới.

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
| :-- | :-- | :-- |
| Ảnh cũ không đổi | GitHub cache ảnh (camo/CDN) | Đợi 1–5 phút, Ctrl+F5 |
| Đồng hồ chậm vài phút | Lượt chạy theo lịch bị trễ | Bình thường, xem mục 3 |
| `profile-3d` "không chạy" | Cổng thông minh bỏ qua vì chưa có push mới | Bình thường; `Run workflow` để ép vẽ |
| Workflow đỏ ở bước API | Token thiếu quyền hoặc hết quota | Kiểm tra `permissions: contents: write`, chạy lại sau vài phút |
| Ảnh không hiện | Thiếu file trong `assets/` | Chạy `health.yml` để xem lỗi cụ thể |
| Push thất bại | Hai workflow commit cùng lúc | Workflow đã tự thử lại 3 lần; nếu vẫn lỗi thì chạy lại |

## Tham khảo

- [README.md](../README.md) — trang cá nhân
- [scripts/generate_cards.py](../scripts/generate_cards.py) — sinh toàn bộ SVG
- [scripts/svgkit/](../scripts/svgkit) — thư viện vẽ (palette, i18n, primitives…)
- [scripts/tests/](../scripts/tests) — hơn 100 unit test
- [scripts/check_repo.py](../scripts/check_repo.py) — kiểm tra sức khỏe repo
- [docs/ANIMATIONS.md](./ANIMATIONS.md) — từng hoạt ảnh trong mỗi tấm ảnh
- [docs/THEMES.md](./THEMES.md) — 6 bảng màu và cách thêm bảng màu mới
- [scripts/svgkit/README.md](../scripts/svgkit/README.md) — bản đồ thư viện vẽ
- [docs/ARCHITECTURE.md](./ARCHITECTURE.md) — luồng dữ liệu và ranh giới module
- [docs/TESTING.md](./TESTING.md) — bộ test và cách viết test mới
- [docs/FAQ.md](./FAQ.md) — ảnh không đổi, số liệu lệch, tốn bao nhiêu runner…
- [CHANGELOG.md](../CHANGELOG.md) — vì sao mỗi thay đổi được làm
