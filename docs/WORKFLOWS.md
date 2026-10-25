# ⚙️ Các workflow tự động

Tài liệu này mô tả các GitHub Actions đang chạy trong repo `standardizeparadigm/standardizeparadigm`. Tất cả đều lưu ảnh ngay trong repo — không gọi server bên thứ ba, không bị rate-limit.

## 1. GitHub Profile 3D Contrib (`.github/workflows/profile-3d.yml`)

**Chức năng:** Tạo biểu đồ contribution dạng khối 3D, gradient đổi màu mượt mà, lưu vào `profile-3d-contrib/`.

- **File ảnh mặc định:** `profile-night-rainbow.svg`
- **Số giao diện:** 10 giao diện màu sắc (xem bảng trong README section 05)
- **Kích hoạt:**
  - Lúc 01:00 mỗi ngày (giờ Việt Nam, UTC+7)
  - Thủ động: tab Actions → **Run workflow**
  - Mỗi khi push nhánh `main`

## 2. Profile Stats Cards (LTS) (`.github/workflows/profile-cards.yml` + `scripts/generate_cards.py`)

**Chức năng:** Sinh hai thẻ SVG động bằng Python thuần (không cần cài thư viện):

- `assets/stats.svg` — stars, forks, repositories, followers, following, commits, rank
- `assets/top-langs.svg` — ngôn ngữ dùng nhiều nhất, thanh进度 hiện từng cột

Điểm mạnh: dùng `GITHUB_TOKEN` riêng của repo nên quota API không bị chia sẻ với hàng ngàn repo khác — không bao giờ 503.

- **Kích hoạt:** 08:00 mỗi ngày, thủ động, và khi file script thay đổi.
- **Chế độStrict:** Nếu API lỗi, ảnh cũ được giữ nguyên, không ghi đè ảnh trống.

## 3. README Garden — Tự nuôi dưỡng (`.github/workflows/readme-tend.yml`)

**Chức năng:** Cập nhật con dấu "lần cập nhật gần nhất" (`<!-- TENDED_AT -->`) ở cuối README và kiểm tra xem các thư mục ảnh còn intact không.

- **Kích hoạt:** 14:00 mỗi Chủ nhật (giờ Việt Nam), thủ động.

## 4. Welcome new contributors (`.github/workflows/welcome.yml`)

**Chức năng:** Bot tự bình luận chào mừng khi có issue hoặc pull request mới được mở.

- **Kích hoạt:** khi có issue/PR mới.

## 5. Dependabot (`.github/dependabot.yml`)

Cập nhật phiên bản các action GitHub hàng tháng.

## Cách chạy lại workflow ngay

1. Vào repo trên GitHub → tab **Actions**.
2. Chọn workflow muốn chạy ở thanh bên trái.
3. Nhấn nút **Run workflow** (màu xanh) → chọn nhánh → **Run workflow**.
4. Đợi xong, refresh trang chủ là thấy ảnh mới.

## Khắc phục sự cố thường gặp

| Triệu chứng | Nguyên nhân có thể | Cách xử lý |
| :-- | :-- | :-- |
| Ảnh stats cũ không đổi | GitHub cache ảnh | Đợi 1–5 phút, nhấn Ctrl+F5 |
| Workflow báo lỗi HTTP 401 | GITHUB_TOKEN không được truyền | Kiểm tra quyền `contents: write` của workflow |
| Thiếu file ảnh | Repo clone thiếu thư mục | Kiểm tra `assets/` và `profile-3d-contrib/` đã được commit |

## Tham khảo

- [README.md](./../README.md) — trang cá nhân chính
- [scripts/generate_cards.py](./../scripts/generate_cards.py) — script sinh thẻ thống kê
