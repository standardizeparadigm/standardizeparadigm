# 🎞️ Kiểm kê hoạt ảnh

Mỗi hình trong `assets/` đều có chuyển động riêng, tất cả đều viết bằng **CSS keyframes** hoặc **SMIL** ngay trong file SVG — không JavaScript, không thư viện, không request nào thêm.

| Hình | Hoạt ảnh chính |
| :-- | :-- |
| `hero.svg` | quỹ đạo xoay, sao nhấp nháy, chip bồng bềnh, vệt sáng quét chữ, gõ chữ |
| `divider.svg` | tia sáng chạy dọc đường kẻ |
| `footer.svg` | hai lớp sóng trôi ngược chiều |
| `stats.svg` | vòng rank tự vẽ, số đếm lên, vệt sáng |
| `top-langs.svg` | thanh xếp chồng lớn dần, chú giải hiện lần lượt |
| `live-clock.svg` | ba kim quay, chấm nhấp nháy, thanh tiến độ ngày |
| `activity.svg` | cột mọc lên, điểm hôm nay nhấp nháy |

## Hero — lớp nền

- **Lưới mờ**: tĩnh, làm nền cho phần chữ.
- **Ba quầng sáng** (`driftA` 16s, `driftB` 21s, `driftC` 26s): trôi chậm theo các hướng khác nhau để nền không bao giờ "đứng hình".
- **Sao** (`twinkle` 4s, độ trễ so le): mờ 12% rồi sáng 85%, giống sao thật.
- **Dải quét** (`scan` 7.5s): một vệt sáng mảnh chạy từ trên xuống; đặt `opacity="0"` để khung hình tĩnh vẫn sạch.

