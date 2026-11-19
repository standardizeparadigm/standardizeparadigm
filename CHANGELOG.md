# 📝 Nhật ký thay đổi

Những thay đổi đáng kể của trang cá nhân này, mới nhất ở trên cùng.
Mỗi mục ghi lại *vì sao* thay đổi, không chỉ *cái gì* đã đổi.

## 2026-11-19 — Thẻ: cập nhật mỗi 30 phút

- `profile-cards.yml` chạy `*/30 * * * *`, thêm bước vẽ `activity.svg` (lỗi thì bỏ qua, không làm đỏ build).

## 2026-11-19 — 3D contrib: kiểm tra mỗi 5 phút

- Lịch `*/5 * * * *` cộng **cổng thông minh**: chỉ vẽ lại khi có PushEvent mới hoặc đã quá 24 giờ.
- Ảnh vẫn tươi theo phút mà không đốt hàng giờ runner mỗi ngày.

## 2026-11-19 — check_repo kiểm tra tham chiếu ảnh

- Mọi `./…` trong Markdown phải trỏ tới file có thật — đổi tên ảnh mà quên sửa README là bắt được ngay.
- Có 4 test riêng cho phần này.

## 2026-11-19 — check_repo quét mọi file Python

- Trước chỉ biên dịch `scripts/*.py`, giờ đi cả cây `scripts/` gồm `svgkit/` và `tests/`.
- Thiếu `__init__.py` trong thư mục con cũng bị cảnh báo.

## 2026-11-19 — Song ngữ Việt / Anh

- `--lang vi|en`. Mọi chuỗi nằm trong `scripts/svgkit/i18n.py`, không rải rác trong code vẽ.

## 2026-11-19 — Sáu bảng màu

- `--theme sky|emerald|violet|sunset|ocean|mono`, mỗi bảng màu là một bộ token `@ACCENT@`… thay vào CSS.
- `--list-themes` in ra danh sách kèm mã màu.

## 2026-11-19 — Activity: bỏ tổng Σ

- Góc phải hiện `Σ 2.7k` trùng ý với ô `CẢ NĂM 2.8k` bên trên.
- Thay bằng `HÔM NAY +0` — thông tin mới, không lặp.

## 2026-11-19 — Activity: cột 0 vẫn nhìn thấy

- Ngày không có contribution trước đây vẽ bằng màu nền nên mất hút.
- Đổi sang màu viền mờ 70% — nhìn được nhịp nghỉ, không phải lỗi render.

## 2026-11-19 — Stats: phần trăm rank theo i18n

- Chuỗi `74% tiến độ` trước đây hard-code `%d%%`, giờ đi qua khoá dịch `stats.progress`.

## 2026-11-19 — Đồng hồ: kim quay bằng CSS

- Ba kim dùng `animation-delay` âm để khớp giờ thật ngay sau khi commit, không cần chờ.
- Giữa hai lần workflow cập nhật, kim vẫn chạy — nhìn là biết trang còn sống.

## 2026-11-19 — Đồng hồ: thêm thứ và ngày

- Thẻ đồng hồ có thêm dòng `Thứ Năm · 19/11/2026` lấy từ `Translator.weekday()`.
- Icon mặt trời / mặt trăng đổi theo giờ, canh cạnh pill lời chào.

## 2026-11-19 — Footer: nâng chữ khỏi sóng

- Dòng “Làm bằng Python…” nằm đúng ngọn sóng nên chìm vào nền.
- Khối chữ nâng lên 14px, hai lớp sóng hạ xuống — chữ luôn nổi.

## 2026-11-19 — Hero: dấu nhắc vẽ bằng path

- Ký tự `›` phụ thuộc font, máy thiếu font sẽ ra ô vuông.
- Thay bằng một path chevron 2 nét — hiển thị giống nhau ở mọi nơi.

## 2026-11-19 — Hero: vệt sáng chuyển sang SMIL

- Vệt sáng quét qua tiêu đề trước đây dùng `clip-path` + CSS: trình xem nào đứng yên ở khung đầu sẽ thấy một mảng trắng đè nửa tiêu đề.
- Đổi sang `<animate attributeName="x">` — khung đầu nằm ngoài màn hình nên luôn sạch.

## 2026-11-19 — Hero: bỏ chip thứ tư bị tràn

- Chip `AI` chen vào vùng chữ cuối trang nên đã bỏ; ba chip `PY` / `JS` / `TS` xếp so le.
- Ít hơn nhưng không đè chữ — ưu tiên đọc được hơn là nhiều.

## 2026-11-19 — Divider phát sáng

- `assets/divider.svg` vẽ lại bằng f-string thay cho `%`-format (chuỗi CSS có dấu `%` từng làm crash).
- Tia sáng chạy dọc đường kẻ, có quầng mờ hai đầu.

## 2026-11-19 — Ảnh chân trang dạng sóng

- `assets/footer.svg`: hai lớp sóng chuyển động ngược chiều, lời cảm ơn + khẩu hiệu.
- Sóng nằm trong `clip-path="url(#cardBody)"` nên không tràn ra ngoài góc bo tròn.

## 2026-11-19 — Thẻ hoạt động 14 ngày

- `assets/activity.svg`: 14 cột contribution thật từ GraphQL, kèm chuỗi ngày hiện tại và chuỗi dài nhất.
- Không lấy được dữ liệu thì trả `None` và giữ ảnh cũ, không làm đỏ workflow.

## 2026-11-19 — svgkit 2.0 — tách thư viện vẽ

- `scripts/generate_cards.py` từ 1 file dài thành gói `scripts/svgkit/`: palette, i18n, primitives, hero, divider, cards, clock, activity, api.
- Thêm thẻ mới giờ chỉ là thêm một module, không phải sửa file khổng lồ.

## 2026-11-19 — Bộ kiểm thử tự động đầu tiên

- 105 unit test phủ palette, i18n, từng thẻ SVG, CLI và `check_repo.py`.
- Chạy bằng `python3 -m unittest discover -s scripts/tests -t scripts`, không cần cài gì thêm.

