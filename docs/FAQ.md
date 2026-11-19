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

