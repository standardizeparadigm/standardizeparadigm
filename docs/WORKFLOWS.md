# ⚙️ Các workflow tự động

Tài liệu mô tả các GitHub Actions đang chạy trong repo `standardizeparadigm/standardizeparadigm`.

**Nguyên tắc chung:** mọi hình đều do workflow vẽ và **commit ngay vào repo** — không gọi server bên thứ ba, không bao giờ bị rate-limit hay lỗi 503. Tất cả action đều ghim phiên bản (`@vN`) và có `permissions` tối thiểu.

## Bảng lịch chạy

| Workflow | Lịch (UTC) | Giờ Việt Nam | Việc làm |
| :-- | :-- | :-- | :-- |
| `live-clock.yml` | `*/5 * * * *` | mỗi 5 phút | `assets/live-clock.svg` |
| `profile-3d.yml` | `8-59/10 * * * *` + cổng 24h | mỗi 10 phút kiểm tra | `profile-3d-contrib/*.svg` khi có push mới |
| `profile-cards.yml` | `13 * * * *` | 24 lần/ngày | `stats`, `top-langs`, `hero`, `activity` (chỉ ghi khi đổi) |
| `readme-tend.yml` | `23 */3 * * *` | 8 lần/ngày | con dấu `TENDED_AT` |
| `status.yml` | `2-59/5 * * * *` + `workflow_run` | phút 2,7,12 … 57 | `assets/status.svg` |
| `health.yml` | push/PR + `3 23 * * *` | 06:03 hằng ngày | test + kiểm tra repo |
| `welcome.yml` | theo sự kiện | — | chào issue/PR mới |

### Chọn nhịp thế nào

Một câu hỏi duy nhất quyết định nhịp: **ảnh này đổi nhanh đến đâu?**

| Loại dữ liệu | Đổi khi nào | Nhịp hợp lý |
| :-- | :-- | :-- |
| Giờ, lời chào, tiến độ ngày | mỗi phút | `*/5` (sàn của GitHub) — số phút tự nhảy bằng CSS |
| Số contribution, biểu đồ 3D | khi bạn push hoặc sang ngày mới | 30 phút + cổng 24h |
| Star, fork, ngôn ngữ | vài ngày một lần | 3 giờ |
| Trạng thái workflow | mỗi khi có lượt chạy xong | 10 phút + `workflow_run` |

Hai workflow ghi file cùng lúc sẽ giành nhau `git push`, nên mỗi job được
một phút riêng trong giờ — không job nào chạm phút của job khác:

| Phút | Job | Vì sao đúng phút đó |
| :-- | :-- | :-- |
| :00 :05 :10 … :55 | `live-clock` | nhịp 5 phút, sàn của GitHub |
| :02 :12 :22 :32 :42 :52 | `status` | lệch 2 phút để không đứng sau đồng hồ |
| :07 :37 | `profile-3d` | không phải bội số của 5 nên không chạm đồng hồ |
| :13 (mỗi 3 giờ) | `profile-cards` | chen giữa :10 và :15 của đồng hồ |
| :23 (mỗi 3 giờ) | `readme-tend` | ngay sau `status` (:22) |
| 23:03 UTC | `health` | 06:03 giờ Việt Nam, sau lượt đồng hồ :00 |

`check_repo.py` cảnh báo nếu sau này ai thêm lịch mà chạm phút của job khác.
Cơ chế push có sẵn vòng thử lại 3 lần, nhưng phòng tránh từ đầu vẫn rẻ hơn.

> GitHub Actions **không hỗ trợ cron mỗi phút** — chu kỳ ngắn nhất là `*/5`. Vì vậy phần "chạy liên tục" được lo bằng hoạt ảnh ngay trong SVG (CSS/SMIL), còn workflow chỉ vẽ lại để ảnh không bị lệch số liệu.

---

## 1. GitHub Profile 3D Contrib — `profile-3d.yml`

Biểu đồ contribution dạng khối 3D, lưu vào `profile-3d-contrib/`.

- **File ảnh:** `profile-3d-contrib/profile-night-rainbow.svg` (và 9 giao diện khác)
- **Chạy:** `8-59/10 * * * *` (mỗi 10 phút, phút :08 :18 :28 :38 :48 :58) · `workflow_dispatch` · khi sửa chính file workflow
  hoặc `scripts/fetch_contributions.py`.
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

- **Chạy:** `13 * * * *` (mỗi giờ, phút :13) · `workflow_dispatch` · khi `scripts/**` thay đổi.
- **`--smart`:** mỗi ảnh mang một dấu `<!-- data:… -->` là vân tay của dữ liệu đã dùng. Lượt sau, nếu vân tay không đổi thì **không ghi file, không commit** — trang vẫn được kiểm tra 8 lần/ngày mà lịch sử git không đầy commit rỗng. Ảnh thiết kế (`hero`, `divider`, `footer`) gộp theo khoá giờ `%Y-%m-%dT%H`, nên chúng chỉ vẽ lại khi sang giờ mới — với nhịp 8 lượt/ngày thì thực tế là mỗi lượt.
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
- **Con số giờ:phút cũng tự nhảy mỗi phút**: nó là 24 ô giờ + 60 ô phút xếp
  chồng, mỗi ô chỉ hiện trong đúng phút của nó (xem
  [docs/ARCHITECTURE.md](./ARCHITECTURE.md#thời-gian-trong-một-file-tĩnh)).
  Vì vậy cron 5 phút **không** làm con số đứng yên — nó chỉ làm phần thứ/ngày
  và vòng cung tiến độ ngày được vẽ lại.
- **Vòng cung ngoài cùng** = hôm nay đã trôi bao nhiêu: một vòng mỗi 24 giờ.
- Muốn xem ảnh ở một khung giờ khác (đêm, sáng sớm) mà không phải chờ:
  `python3 scripts/generate_cards.py --clock --at 2026-11-19T23:50 --out /tmp/thu`.

## 4. README Garden — `readme-tend.yml`

- Cập nhật con dấu `<!-- TENDED_AT: ... -->` ở cuối README (ngày **và giờ phút**, giờ Việt Nam).
- Kiểm tra `assets/` và `profile-3d-contrib/` còn đủ file.
- **Chạy:** `0 */3 * * *` (mỗi 3 giờ) · `workflow_dispatch` · khi README thay đổi. Con dấu vì thế không bao giờ cũ quá 3 giờ mà chỉ tốn 8 lượt/ngày.

> `health.yml` bỏ qua **cả thư mục** `assets/` và `profile-3d-contrib/` khi có
> push: hai thư mục đó do bot vẽ lại liên tục, nên liệt kê từng file là cách
> chắc chắn để file mới sinh ra lọt lưới.

## 5. Repo Health — `health.yml` + `scripts/check_repo.py`

Chạy tay trên máy: `python3 scripts/check_repo.py`. Có lỗi vệ sinh kiểu BOM/CRLF/khoảng
trắng thì thêm `--fix` để nó tự sửa — cờ này chỉ đụng thứ vô hình với người đọc, không
đổi một ký tự nội dung nào.

"Bác sĩ" của repo, chạy mỗi lần push/PR và 06:00 mỗi ngày:

- Chạy **hơn 800 unit test** (`python3 -m unittest discover -s scripts/tests -t scripts`)
- Thử vẽ lại toàn bộ SVG với **6 bảng màu × 2 ngôn ngữ** rồi parse XML từng file
- Chữ có lỗi encoding (ký tự hỏng, chữ Hán/Hàn lạc vào, mojibake)
- URL có `%`-escape sai hoặc giải mã ra UTF-8 không hợp lệ
- Anchor `#mục` và đường dẫn `./...` trong Markdown có tồn tại
- Workflow YAML parse được, cron đủ 5 trường, action có phiên bản
- Quy ước an toàn workflow: `permissions`, `concurrency`, `timeout-minutes`,
  cổng chặn bot khi có `git push`
- Tài liệu khớp máy: bảng lịch chạy đúng cron, workflow nào cũng có dòng,
  `workflow_run` khớp tên thật, câu "hơn N unit test" còn đúng
- Vệ sinh file: BOM, CRLF, ký tự điều khiển, UTF-8 hỏng, khoảng trắng thừa,
  dấu merge còn sót
- Ảnh: XML hợp lệ, có `<title>`, dưới 40 KB, không có ảnh chết trong `assets/`
- Ảnh (tiếp): mọi `<text>` có `class`, `id` không trùng, không có `None`/`NaN`
  lọt vào chữ, không gọi URL ngoài, không mang `<script>` hay thuộc tính `on*`
- Tài liệu: không mồ côi, README dưới 360 dòng, Markdown đúng hình thức —
  tiêu đề không nhảy cấp, bảng thẳng cột, mỗi tài liệu mở bằng một `#`
- Địa danh: không còn tên tỉnh/thành cũ của chủ repo ở bất kỳ file nào
  (chuỗi cấm nằm trong `STALE_PLACES` của `check_repo.py`)
- Code: không còn `TODO`/`FIXME`, mọi workflow có `workflow_dispatch`, không
  dùng badge trạng thái của shields, cron không dày hơn 5 phút
- Mọi file Python biên dịch được và mở đầu bằng docstring

Chạy tay: `python3 scripts/check_repo.py`

## 6. Welcome New Contributors — `welcome.yml`

Tự bình luận chào mừng khi có issue/PR mới. Bỏ qua tài khoản bot, chỉ chào **một lần** cho mỗi issue/PR.

---

## 7. Workflow Status — `status.yml`

Vẽ `assets/status.svg`: một dải 7 viên thuốc, mỗi viên một workflow, màu
theo lần chạy gần nhất (xanh = đạt, đỏ = lỗi, hổ phách = đang chạy, xám =
chưa chạy, xanh dương = chờ merge).

Vì sao không dùng badge shields.io ở đây:

- shields chỉ đọc được workflow **nằm trên nhánh mặc định**. Workflow mới
  tạo ở nhánh khác → badge trả `repo or workflow not found`.
- Workflow chưa từng chạy xong → badge trả `no status` (ô xám).
- Trang nạp thêm 6 ảnh từ server ngoài, mỗi ảnh có thể chậm hoặc chết.

Dải này thì: đọc Actions API bằng chính token của repo, vẽ SVG, commit —
nằm cùng repo, cùng CDN với các ảnh khác, không bao giờ "not found".

- **Chạy:** phút 2, 12, 22, 32, 42, 52 (lệch 2 phút so với đồng hồ), và ngay
  khi có workflow khác vừa xong (`workflow_run`).
- **Không đọc được API** → giữ nguyên ảnh cũ, không ghi thẻ rỗng.
- **Chân dải** có hai thông tin: dấu `cập nhật HH:MM` (dải này vẽ lúc nào) và
  `4/7 workflow ổn` (tình hình chung). "Đang chạy" được tính là ổn.
- Thêm workflow mới: thêm một dòng vào `WORKFLOWS` trong `scripts/svgkit/status.py`
  — dải tự giãn bề rộng.

> [!NOTE]
> `workflow_dispatch` chỉ chạy được khi file workflow **đã có trên nhánh mặc
> định**. Đó cũng là lý do badge lẫn nút "Run workflow" cùng "mất tích" với
> một workflow còn nằm ở nhánh khác.

## Ai `git push` lúc nào

Sáu workflow đều ghi vào cùng một nhánh, nên lịch chạy được xếp so le —
không phải cho đẹp bảng, mà để hai lượt chạy không cùng push một lúc:

| Phút trong giờ | Workflow | Ghi gì |
| :-- | :-- | :-- |
| 0, 5, 10, … (mọi phút chia hết cho 5) | `live-clock.yml` | `assets/live-clock.svg` |
| 2, 12, 22, 32, 42, 52 | `status.yml` | `assets/status.svg` |
| 0 và 30 | `profile-3d.yml` | `profile-3d-contrib/*.svg` (khi cổng cho qua) |
| phút 15 (0h, 3h, 6h…) | `profile-cards.yml` | bốn thẻ + hero |
| phút 45 (0h, 3h, 6h…) | `readme-tend.yml` | con dấu `TENDED_AT` |
| 23:00 UTC | `health.yml` | không ghi, chỉ kiểm tra |

Ba lớp bảo hiểm khi vẫn trùng giờ:

1. **`concurrency`** riêng cho từng workflow — một workflow không bao giờ
   chạy hai lượt cùng lúc, nhưng *hai workflow khác nhau* thì vẫn có thể.
2. Mỗi lượt `git pull --rebase` trước khi push, nên bên tới sau vẫn đẩy
   được thay vì bị từ chối.
3. `status.yml` là thứ duy nhất cần tươi theo phút, nên nó đứng sau cùng:
   nếu một lượt trạng thái thất bại, nó chỉ cũ hơn 10 phút — không mất gì.

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
| Đồng hồ lệch đúng 7 tiếng | Mốc thời gian chưa quy về UTC+7 | Kiểm `api.to_vn()` và `test_api_time.py` |
| `profile-3d` "không chạy" | Cổng thông minh bỏ qua vì chưa có push mới | Bình thường; `Run workflow` để ép vẽ |
| Workflow đỏ ở bước API | Token thiếu quyền hoặc hết quota | Kiểm tra `permissions: contents: write`, chạy lại sau vài phút |
| Ảnh không hiện | Thiếu file trong `assets/` | Chạy `health.yml` để xem lỗi cụ thể |
| Push thất bại | Hai workflow commit cùng lúc | Workflow đã tự thử lại 3 lần; nếu vẫn lỗi thì chạy lại |
| Badge shields báo `repo or workflow not found` | Workflow chưa nằm trên nhánh mặc định | Merge, hoặc dùng `assets/status.svg` (mục 7) |
| Badge shields báo `no status` | Workflow có nhưng chưa chạy xong lần nào | Chạy một lần, hoặc dùng `assets/status.svg` |
| Bấm `Run workflow` không thấy workflow | File chỉ có ở nhánh khác | Merge vào nhánh mặc định trước |
| Dải trạng thái ghi `24 ngày trước` | Workflow chưa chạy trên nhánh mặc định | Merge, hoặc bỏ qua — đó là sự thật, không phải lỗi |
| Dải trạng thái ghi `CHỜ MERGE` | Workflow chưa có trên nhánh mặc định | Merge; lượt chạy sau tự đổi sang `ĐẠT` |

## Tham khảo

- [README.md](../README.md) — trang cá nhân
- [scripts/generate_cards.py](../scripts/generate_cards.py) — sinh toàn bộ SVG
- [scripts/svgkit/](../scripts/svgkit) — thư viện vẽ (palette, i18n, primitives…)
- [scripts/tests/](../scripts/tests) — hơn 800 unit test
- [scripts/check_repo.py](../scripts/check_repo.py) — kiểm tra sức khỏe repo
- [docs/ANIMATIONS.md](./ANIMATIONS.md) — từng hoạt ảnh trong mỗi tấm ảnh
- [docs/THEMES.md](./THEMES.md) — 6 bảng màu và cách thêm bảng màu mới
- [scripts/svgkit/README.md](../scripts/svgkit/README.md) — bản đồ thư viện vẽ
- [docs/ARCHITECTURE.md](./ARCHITECTURE.md) — luồng dữ liệu và ranh giới module
- [docs/TESTING.md](./TESTING.md) — bộ test và cách viết test mới
- [docs/FAQ.md](./FAQ.md) — ảnh không đổi, số liệu lệch, tốn bao nhiêu runner…
- [CHANGELOG.md](../CHANGELOG.md) — vì sao mỗi thay đổi được làm
