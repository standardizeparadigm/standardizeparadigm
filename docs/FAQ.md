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

- **Lớp ảnh**: workflow kiểm tra mỗi 5 phút (đồng hồ, 3D) hoặc 10 phút (thẻ số liệu, có `--smart` để không commit rỗng).
- **Lớp hoạt ảnh**: CSS/SMIL trong file SVG làm ảnh **luôn chuyển động** giữa hai lần cập nhật. Kim đồng hồ quay liên tục, không cần workflow nào cả.

## Tốn bao nhiêu phút runner mỗi ngày?

| Workflow | Lượt/ngày | Thời gian mỗi lượt | Tổng |
| :-- | --: | --: | --: |
| `live-clock` | 288 | ~15 giây | ~72 phút |
| `profile-3d` | 288 (phần lớn bị cổng chặn) | ~8 giây khi bị chặn | ~40 phút + vài lượt vẽ thật |
| `profile-cards` | 144 (phần lớn `--smart` bỏ qua) | ~20 giây | ~48 phút |
| `readme-tend` | 8 | ~12 giây | ~2 phút |
| `health` | 1 + mỗi push | ~40 giây | ~1 phút |

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

