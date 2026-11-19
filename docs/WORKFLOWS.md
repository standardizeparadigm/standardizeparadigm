# ⚙️ Các workflow tự động

Tài liệu này mô tả các GitHub Actions đang chạy trong repo `standardizeparadigm/standardizeparadigm`.

**Nguyên tắc chung:** mọi hình đều do workflow vẽ và **commit ngay vào repo** — không gọi server bên thứ ba, không bao giờ bị rate-limit hay lỗi 503. Tất cả workflow đều ghim phiên bản action (`@vN`) và có `permissions` tối thiểu.

---

## 1. GitHub Profile 3D Contrib — `profile-3d.yml`

Tạo biểu đồ contribution dạng khối 3D, lưu vào `profile-3d-contrib/`.

- **File ảnh:** `profile-3d-contrib/profile-night-rainbow.svg` (và 9 giao diện khác)
- **Chạy:** 01:00 mỗi ngày (giờ Việt Nam) · `workflow_dispatch` · khi sửa chính file workflow
- **Chống lỗi:** kiểm tra ảnh sinh ra có phải XML hợp lệ trước khi commit; bỏ qua commit của bot để không lặp vô hạn.

## 2. Profile Cards (LTS) — `profile-cards.yml` + `scripts/generate_cards.py`

Vẽ bằng Python thuần (không cần cài thư viện):

| File | Nội dung |
| :-- | :-- |
| `assets/stats.svg` | stars, forks, repos, followers, following, commits + vòng rank |
| `assets/top-langs.svg` | ngôn ngữ dùng nhiều nhất, thanh xếp chồng + thanh tiến độ từng ngôn ngữ |
| `assets/hero.svg` | ảnh bìa động (gradient, quỹ đạo, hiệu ứng gõ chữ) |
| `assets/divider.svg` | đường kẻ động dùng giữa các mục |

- **Chạy:** 08:00 mỗi ngày (giờ Việt Nam) · `workflow_dispatch` · khi `scripts/generate_cards.py` thay đổi
- **Dữ liệu:** `GITHUB_TOKEN` có sẵn của repo → quota riêng, không chia sẻ với hàng nghìn repo khác.
- **Chế độ `--strict`:** API lỗi là workflow báo đỏ ngay, không âm thầm giữ ảnh cũ.
- **An toàn:** ghi file kiểu *atomic* (file tạm rồi `os.replace`), nên mất mạng giữa chừng thì ảnh cũ vẫn nguyên vẹn.

## 3. Live Clock — `live-clock.yml` (cập nhật theo phút)

Vẽ lại `assets/live-clock.svg`: đồng hồ Việt Nam (UTC+7), lời chào theo giờ, tiến độ trong ngày.

- **Chạy:** `*/5 * * * *` — **mỗi 5 phút**, là chu kỳ ngắn nhất GitHub Actions hỗ trợ. GitHub **không** cho cron mỗi phút, và các lượt chạy theo lịch có thể bị trễ vài phút khi hệ thống tải cao.
- **Không gọi API** → mỗi lượt chỉ vài giây, không tốn quota.
- Muốn thưa hơn: đổi `"*/5 * * * *"` thành `"*/15 * * * *"` hoặc `"0 * * * *"`.
- Kim đồng hồ còn **tự quay** bằng CSS/SMIL giữa hai lần cập nhật, nên nhìn luôn "sống".

## 4. README Garden — `readme-tend.yml`

- Cập nhật con dấu `<!-- TENDED_AT: ... -->` ở cuối README (ngày **và giờ phút**, giờ Việt Nam).
- Kiểm tra `assets/` và `profile-3d-contrib/` còn đủ file.
- **Chạy:** 14:00 mỗi **Chủ nhật** (giờ Việt Nam) · `workflow_dispatch` · khi README thay đổi.

## 5. Repo Health — `health.yml` + `scripts/check_repo.py`

"Bác sĩ" của repo, chạy mỗi lần push/PR và 06:00 mỗi ngày:

- SVG có phải XML hợp lệ
- Chữ có lỗi encoding (ký tự hỏng, chữ Hán/Hàn lạc vào, mojibake)
- URL có `%`-escape sai hoặc giải mã ra UTF-8 không hợp lệ
- Anchor `#mục` và đường dẫn ảnh tương đối có tồn tại
- Workflow YAML parse được, cron đủ 5 trường, action có phiên bản
- Script Python biên dịch được

Chạy tay: `python3 scripts/check_repo.py`

## 6. Welcome New Contributors — `welcome.yml`

Tự bình luận chào mừng khi có issue/PR mới. Bỏ qua tài khoản bot, chỉ chào **một lần** cho mỗi issue/PR (kiểm tra bình luận cũ trước khi gửi).

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
| Workflow đỏ ở bước API | Token thiếu quyền hoặc hết quota | Kiểm tra `permissions: contents: write`, chạy lại sau vài phút |
| Ảnh không hiện | Thiếu file trong `assets/` | Chạy `health.yml` để xem lỗi cụ thể |
| Push thất bại | Hai workflow commit cùng lúc | Workflow đã tự thử lại 3 lần; nếu vẫn lỗi thì chạy lại |

## Tham khảo

- [README.md](../README.md) — trang cá nhân
- [scripts/generate_cards.py](../scripts/generate_cards.py) — sinh toàn bộ SVG
- [scripts/check_repo.py](../scripts/check_repo.py) — kiểm tra sức khỏe repo
