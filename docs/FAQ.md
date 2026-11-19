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

