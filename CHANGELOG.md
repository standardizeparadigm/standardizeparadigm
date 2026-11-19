# 📝 Nhật ký thay đổi

Những thay đổi đáng kể của trang cá nhân này, mới nhất ở trên cùng.
Mỗi mục ghi lại *vì sao* thay đổi, không chỉ *cái gì* đã đổi.

## 2026-11-19 — Dải trạng thái workflow thay cho badge shields.io

- Ba badge trong ảnh chụp bị hỏng: `live-clock` và `health` trả *repo or
  workflow not found* (file chỉ có ở nhánh phụ), `welcome` trả *no status*
  (có workflow nhưng chưa chạy xong lần nào).
- `assets/status.svg` do chính repo vẽ từ Actions API: 7 viên thuốc, mỗi
  viên một workflow, màu theo lần chạy gần nhất. Không phụ thuộc server ngoài
  nên không có khái niệm "not found".

## 2026-11-19 — Năm trạng thái, không phải ba

- `passing` / `failing` / `running` / `none` / `unknown` ban đầu chỉ đủ cho
  badge. Khi đọc API thật mới thấy cần thêm `missing` (404 = workflow chưa
  nằm trên nhánh mặc định) — đúng lý do khiến shields báo đỏ.
- Màu cố định theo nghĩa (xanh/đỏ/hổ phách/xám/xanh dương) chứ không theo
  theme: "đỏ = lỗi" phải đúng ở cả 6 bảng màu.

## 2026-11-19 — Nhịp chạy: giãn chỗ thừa, giữ chỗ cần

- 3D: `*/5` → `*/30` (ảnh chỉ đổi khi có push hoặc sang ngày; push đã có
  trigger riêng nên lịch 5 phút chỉ tạo 288 lượt chạy rỗng/ngày).
- Thẻ số liệu: `*/10` → `15 */3 * * *` (star/fork/ngôn ngữ đổi vài ngày/lần).
- README Garden dời sang phút 45 để hai workflow không giành `git push`.
- Đồng hồ giữ `*/5` — đây là sàn của GitHub và cũng là thứ duy nhất thật sự
  cần tươi theo phút.

## 2026-11-19 — Workflow tự vẽ dải trạng thái

- `status.yml`: cron 15 phút **và** `workflow_run` — có workflow vừa xong là
  dải cập nhật ngay, không phải đợi lượt kế tiếp.
- Quyền `contents: write` + `actions: read`; kiểm tra XML trước khi commit;
  không đọc được API thì giữ ảnh cũ chứ không ghi thẻ rỗng.

## 2026-11-19 — Vệ sinh file trong check_repo

- Bốn loại lỗi vô hình: BOM UTF-8, xuống dòng CRLF, ký tự điều khiển dưới
  U+0020, và file không phải UTF-8 hợp lệ. Đều là mầm của "hỏng kí tự".
- Khoảng trắng thừa cuối dòng chỉ là cảnh báo để không chặn CI.
- Bỏ qua `.git`, `node_modules`, `.venv`, `__pycache__` và file nhị phân.

## 2026-11-19 — Hai lớp test bị che khuất

- `test_cli.py` có ba lớp cùng tên `TestInfoFlags`/`TestCheckFlag`;
  `test_cards.py` và `test_primitives.py` mỗi file hai lớp trùng tên. Python
  chỉ giữ lớp cuối, nên các bản trước **không bao giờ chạy**.
- Đã xoá hai bản sao trong `test_cli.py`, đổi tên hai lớp còn lại. Số test
  tăng từ 211 lên 214 dù không viết thêm test nào — đó là phần bị che.

## 2026-11-19 — Cổng 3D: sửa lỗi mốc 24 giờ không bao giờ tới

- Cổng so "lần chạy thành công gần nhất", nhưng lượt bị cổng bỏ qua **vẫn** là lượt thành công → mốc 24 giờ không bao giờ đạt được, ảnh chỉ đổi khi có push.
- Giờ so theo `git log -1 -- profile-3d-contrib` (lần ảnh đổi thật), cần `fetch-depth: 0`, và có 2 test dựng repo git tạm để khoá hành vi.

## 2026-11-19 — Icon lạ không còn để trống

- `icon()` rơi về `spark` thay vì trả chuỗi rỗng — không bao giờ có ô trống trong thẻ vì gõ sai tên icon.

## 2026-11-19 — Thẻ chờ có `<desc>`

- Trước đây thẻ tạm chỉ có `aria-label`; giờ có thêm mô tả nên trình đọc màn hình đọc được cả thẻ tạm.

## 2026-11-19 — Test tự soi mã nguồn

- Test mới quét `svgkit/*.py` để chắc mọi khoá `t("…")` đều có trong `STRINGS`, và mọi token `@…@` trong CSS đều có giá trị trong `Palette`.

## 2026-11-19 — docs/FAQ.md

- Tám câu hỏi hay gặp: cache ảnh, vì sao không chạy mỗi phút, tốn bao nhiêu phút runner, vì sao SVG, số liệu lệch, đổi theme, dùng lại code.

## 2026-11-19 — Mọi thứ đều tất định

- Sao, bụi sáng, dữ liệu demo đều dùng `random.Random(seed)` cố định — hai lần build cho ra file giống hệt (trừ thời gian), nên `--smart` đáng tin và test khẳng định được toạ độ chính xác.

## 2026-11-19 — docs/ANIMATIONS.md: bảng chu kỳ

- Một bảng gom toàn bộ chu kỳ hoạt ảnh (CSS và SMIL) để chỉnh nhịp cả trang ở một chỗ.

## 2026-11-19 — docs/TESTING.md

- Bản đồ 11 file test, mỗi file kiểm tra gì, cách viết test mới và CI chạy những gì.

## 2026-11-19 — docs/ARCHITECTURE.md

- Giải thích luồng dữ liệu, ranh giới module, vì sao chỉ dùng thư viện chuẩn, chiến lược hoạt ảnh, cách ghi file, xử lý lỗi và checklist thêm thẻ mới.

## 2026-11-19 — Hero: hai vòng lan toả quanh lõi

- Bán kính 26 → 86, mờ dần, chu kỳ 5.2 giây, lệch pha nửa chu kỳ — như nhịp thở của monogram.

## 2026-11-19 — Top languages: khoanh sáng ngôn ngữ đứng đầu

- Chấm màu của ngôn ngữ lớn nhất có thêm vòng mờ nhấp nháy — mắt bám vào đó trước.

## 2026-11-19 — Activity: nhãn ngày cao nhất

- Cột cao nhất có nhãn `cao nhất 1.1k`, ẩn đi khi hôm nay đã là ngày cao nhất (chỗ đó đã có chấm nhấp nháy).

## 2026-11-19 — `--dry-run` và `--quiet`

- `--dry-run` vẽ và kiểm tra nhưng không ghi file — xem trước mà không đụng ảnh thật.
- `--quiet` im lặng hoàn toàn khi mọi thứ ổn, chỉ còn lỗi trên stderr.

## 2026-11-19 — Bộ test lên 150

- Thêm test cho hạt bụi, cung rank, vành đồng hồ, đường trung bình, tia sáng và vân tay dữ liệu.

## 2026-11-19 — Footer: bong bóng sáng

- Sáu bong bóng bay từ đáy lên với chu kỳ 11 giây, lệch pha; thêm quầng sáng nhấp nháy sau tiêu đề.

## 2026-11-19 — Divider: tia sáng thứ hai

- Thêm một tia mảnh, mờ hơn, chạy ngược chiều 13 giây/lần — đường kẻ có chiều sâu hơn.

## 2026-11-19 — Activity: đường trung bình 14 ngày

- Đường nét đứt màu nhấn, kèm nhãn `TB 196` ở góc trái — chỉ hiện khi dữ liệu có chênh lệch thật.
- Mọi ngày bằng nhau thì ẩn đi, vì đường trung bình lúc đó chẳng nói gì.

## 2026-11-19 — Clock: đuôi kim giây

- Kim giây có thêm chấm đối trọng phía sau trục, đúng kiểu đồng hồ cơ.

## 2026-11-19 — Clock: vệt sáng quét quanh vành

- Một cung gradient `dasharray="70 320"` quay 18 giây/vòng, trên vành ngoài — vành cũng "thở" như kim.

## 2026-11-19 — Top languages: phần trăm tính trên toàn bộ byte code

- Trước đây tổng chỉ cộng 8 ngôn ngữ hiển thị, nên ngôn ngữ nhỏ bị "đội" phần trăm lên.
- Giờ tổng lấy từ mọi ngôn ngữ; phần còn lại hiện `+N ngôn ngữ khác · x%` ở góc phải.

## 2026-11-19 — Stats: chấm sáng ở đầu cung rank

- Điểm sáng đặt đúng toạ độ đầu cung (góc `-90 + 360×74%`), có quầng `glow` và nhịp `pulse`.
- Khung đầu tiên đã hiện sẵn — không dùng hiệu ứng mờ dần để trình xem tĩnh vẫn thấy.

## 2026-11-19 — Hero: bụi sáng bay lên

- 14 hạt sáng nhỏ dùng SMIL `animate` trên `cy` và `opacity`, chu kỳ 7–13 giây, lệch pha ngẫu nhiên nhưng cố định.
- Hạt bị đẩy ra khỏi vùng chữ, có test khoá lại.

## 2026-11-19 — `--smart`: kiểm tra mỗi 10 phút, commit khi có lý do

- Mỗi ảnh mang một dấu `<!-- data:… -->` là vân tay dữ liệu đã dùng để vẽ.
- Lượt sau, vân tay không đổi thì không ghi file và không commit — trang vẫn được kiểm tra mỗi 10 phút.

## 2026-11-19 — Bộ test vượt 130

- Thêm test cho `human()`, `esc()`, i18n dự phòng, tiêu đề/desc của từng thẻ và cổng workflow 3D.
- Test không cần mạng: mọi lời gọi API đều được thay bằng dữ liệu mẫu.

## 2026-11-19 — Cổng 3D không được chết im lặng

- `${GITHUB_REPOSITORY_OWNER}` chưa đặt + `set -u` → cổng thoát giữa đường và luôn bỏ qua lượt vẽ.
- Giờ có giá trị dự phòng, số đếm sai định dạng được đưa về 0, và 5 test dùng `gh` giả khoá lại hành vi.

## 2026-11-19 — `check_assets()` khai báo sai thứ tự

- Hàm nằm sau khối `if __name__ == "__main__"` nên khi chạy bằng script thì `NameError`.
- Đã chuyển lên trước `main()`, kèm 3 test chạy CLI qua `subprocess`.

## 2026-11-19 — Sửa lỗi `--check` chọn nhầm thư mục

- `--check` từng bỏ qua `--out` vì biến toàn cục `OUT_DIR` luôn khác rỗng — kiểm tra nhầm thư mục `assets/`.
- Test chạy CLI như tiến trình con đã bắt được lỗi này; trước đó test import module nên không thấy.

## 2026-11-19 — Ba cờ CLI mới

- `--version`, `--list-langs` và `--check` (parse mọi SVG trong thư mục ra rồi báo cáo).
- `--check` tiện cho người mới: vẽ xong, kiểm tra ngay, khỏi mở trình duyệt.

## 2026-11-19 — Tôn trọng `prefers-reduced-motion`

- Người bật “giảm chuyển động” trong hệ điều hành sẽ thấy ảnh tĩnh — không còn hoạt ảnh nào quay cuồng.
- Ảnh tĩnh vẫn đẹp vì khung đầu tiên đã được vẽ sẵn ở trạng thái cuối.

## 2026-11-19 — Mọi thẻ có `<title>` và `<desc>`

- Trước chỉ có `aria-label` — trình đọc màn hình đọc được nhưng công cụ tìm kiếm và chế độ đọc không thấy gì.
- Giờ mỗi tấm ảnh có tiêu đề trùng `aria-label` và một dòng mô tả riêng, đã dịch cả vi/en.

## 2026-11-19 — CONTRIBUTING: nhắc không sửa tay SVG

- `assets/*.svg` do máy sinh; sửa tay sẽ bị lượt workflow kế tiếp ghi đè.
- Thêm lệnh chạy bộ test ngay trên máy.

## 2026-11-19 — README ngắn hơn, nhiều hình hơn

- Thêm thẻ hoạt động và chân trang, nhưng số dòng vẫn giữ nguyên — chỗ mới lấy từ chỗ cũ rút gọn.

## 2026-11-19 — Health: thử vẽ cả 6 theme × 2 ngôn ngữ

- Mỗi lần push, CI vẽ lại toàn bộ SVG với mọi bảng màu và mọi ngôn ngữ rồi parse XML từng file.
- Bảng màu nào làm vỡ bố cục là biết ngay.

## 2026-11-19 — README Garden: mỗi 3 giờ

- Con dấu “lần cập nhật gần nhất” không cũ quá 3 giờ, chỉ tốn 8 lượt chạy mỗi ngày thay vì 1 lượt mỗi tuần.

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

- Hơn 100 unit test phủ palette, i18n, từng thẻ SVG, CLI và `check_repo.py`.
- Chạy bằng `python3 -m unittest discover -s scripts/tests -t scripts`, không cần cài gì thêm.

