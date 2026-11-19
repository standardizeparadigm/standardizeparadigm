# ❓ Hỏi nhanh đáp gọn

Những câu hay gặp khi xem (hoặc fork) trang này.

## Ảnh vừa cập nhật mà trang vẫn hiện ảnh cũ?

**Cache.** GitHub phục vụ ảnh qua CDN, giữ bản cũ vài phút. Cách kiểm tra:

1. Mở thẳng file: `https://github.com/standardizeparadigm/standardizeparadigm/blob/main/assets/stats.svg` — nếu số liệu ở đây đúng thì ảnh đã cập nhật.
2. Quay lại trang chủ, `Ctrl + F5` (hoặc `Cmd + Shift + R`).

Thường 1–5 phút là hết.

## Vì sao không chạy mỗi phút một lần?

GitHub Actions **không hỗ trợ** cron mỗi phút; chu kỳ ngắn nhất là `*/5`. Ngoài ra lượt chạy theo lịch có thể bị trễ vài phút khi hệ thống tải cao.

Nên trang này làm hai lớp:

- **Lớp ảnh**: đồng hồ kiểm tra mỗi 5 phút, biểu đồ 3D mỗi 30 phút (có cổng 24h), thẻ số liệu và README mỗi 3 giờ, dải trạng thái mỗi 15 phút. Chỗ nào có `--smart` thì chỉ commit khi số liệu thật sự đổi.
- **Lớp hoạt ảnh**: CSS/SMIL trong file SVG làm ảnh **luôn chuyển động** giữa hai lần cập nhật. Kim đồng hồ quay liên tục, không cần workflow nào cả.

## Tốn bao nhiêu phút runner mỗi ngày?

| Workflow | Lượt/ngày | Thời gian mỗi lượt | Tổng |
| :-- | --: | --: | --: |
| `live-clock` | 288 | ~15 giây | ~72 phút |
| `status` | 96 (+ mỗi lượt chạy xong) | ~10 giây | ~16 phút |
| `profile-3d` | 48 (phần lớn bị cổng chặn) | ~8 giây khi bị chặn | ~7 phút + vài lượt vẽ thật |
| `profile-cards` | 8 (phần lớn `--smart` bỏ qua) | ~25 giây | ~4 phút |
| `readme-tend` | 8 | ~12 giây | ~2 phút |
| `health` | 1 + mỗi push | ~60 giây | ~2 phút |

Với repo công khai, phút runner miễn phí — nhưng vẫn giữ ở mức này để không bị coi là lạm dụng.

## Vì sao là SVG mà không phải PNG?

- **Nhẹ**: thẻ 640×258 chỉ ~16 KB, PNG cùng kích thước dễ vượt 100 KB.
- **Nét**: phóng to bao nhiêu cũng sắc, hợp màn hình Retina.
- **Động**: chứa được CSS/SMIL — PNG thì không.
- **Chữ chọn được**: người xem có thể bôi đen số liệu, trình đọc màn hình đọc được.

Đổi lại: SVG cần trình duyệt để render, và một số nơi (email, một số trình xem markdown) chặn hoạt ảnh — nên mọi khung hình đầu tiên đều được vẽ đẹp sẵn.

## Số liệu trên thẻ khác số trên GitHub?

Có ba lý do chính đáng:

1. **Thời điểm**: thẻ được vẽ lúc workflow chạy, GitHub hiện tại có thể mới hơn vài phút.
2. **Phạm vi**: `stars` và `langs` chỉ tính repo **công khai**; repo private không được tính.
3. **Ngôn ngữ**: tính theo **byte code** (GitHub Linguist), không theo số file hay số dòng.

Nếu lệch cả tháng, có thể `GITHUB_TOKEN` hết quyền — xem log của workflow `Profile Cards`.

## Muốn đổi tên hiển thị hoặc bảng màu?

Không sửa file SVG. Sửa chỗ sinh ra nó:

- Tên: biến `DISPLAY_NAME` trong `.github/workflows/profile-cards.yml`.
- Bảng màu: thêm `--theme ocean` vào lệnh trong workflow (hoặc đổi `DEFAULT_THEME` trong `scripts/svgkit/palette.py`).
- Ngôn ngữ: `--lang en`.

Sau đó vào tab **Actions → Profile Cards → Run workflow**.

## Dùng lại code này cho trang của mình?

Được — giấy phép MIT. Gọn nhất là:

1. Fork repo.
2. Sửa `GH_USER` (workflow đã tự lấy `github.repository_owner`, thường không cần sửa).
3. Bật Actions, chạy `Profile Cards` một lần để có ảnh thật.
4. Xoá bớt mục bạn không cần trong `README.md`.

Nhớ đổi tên, tiểu sử và liên hệ — đừng để hai trang giống hệt nhau.


## Ảnh 3D đứng im dù workflow vẫn chạy xanh?

Đúng thiết kế: cổng thông minh bỏ qua lượt chạy khi chưa có push mới và ảnh chưa quá 24 giờ. Muốn vẽ ngay: **Actions → GitHub Profile 3D Contrib → Run workflow** — `workflow_dispatch` luôn đi qua cổng ở trạng thái "chưa có mốc", nên vẽ lại ngay.


## Badge trên trang báo `repo or workflow not found`?

Badge shields.io đọc trạng thái qua API `.../actions/workflows/<file>`, và
API đó **chỉ thấy workflow nằm trên nhánh mặc định**. Workflow còn ở nhánh
khác thì badge trả `repo or workflow not found`; workflow có trên nhánh
mặc định nhưng chưa chạy xong lần nào thì trả `no status`.

Cách chắc chắn nhất: dùng `assets/status.svg` — repo tự vẽ dải trạng thái
bằng token của chính nó, nên không có khái niệm "không tìm thấy".

## Đã thêm workflow mới, sao không chạy tay được?

`workflow_dispatch` chỉ xuất hiện khi file workflow **đã có trên nhánh mặc
định**. Đây là quy định của GitHub, không phải lỗi cấu hình: `gh workflow
run` trên một workflow chỉ có ở nhánh phụ sẽ trả HTTP 404.

Merge trước, chạy sau.
