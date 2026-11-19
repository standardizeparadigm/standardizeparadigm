# 🧪 Kiểm thử

Bộ test chạy bằng `unittest` của Python — không cần `pytest`, không cần mạng, không cần token. Toàn bộ dữ liệu GitHub trong test là dữ liệu giả dựng sẵn.

```bash
python3 -m unittest discover -s scripts/tests -t scripts        # chạy hết
python3 -m unittest discover -s scripts/tests -t scripts -v     # in tên từng test
python3 -m unittest tests.test_clock -v                          # chỉ một file
python3 -m unittest tests.test_status.TestPillGeometry -v        # chỉ một lớp
python3 -m unittest tests.test_clock.TestSunMoon.test_six_pm_is_already_moon
```

Thứ tự tham số quan trọng: `-t scripts` để `sys.path` có `scripts/`, nhờ vậy
test import được `svgkit.*` mà không cần cài gì.

Hiện có **792 test** trên 17 file, chạy xong trong chưa tới 1,5 giây.

Con số này được kiểm tự động: `test_docs.py` đếm lại toàn bộ bộ test và so
với chữ trong file bạn đang đọc, nên nó không thể lệch âm thầm.

## Bản đồ

| File | Kiểm tra điều gì |
| :-- | :-- |
| `test_palette.py` | 6 theme, token, màu ngôn ngữ, cách tính rank |
| `test_i18n.py` | đủ khoá vi/en, thứ trong tuần, dự phòng khi thiếu khoá |
| `test_primitives.py` | escape XML, `human()`/`num()`, icon, khung thẻ, giảm chuyển động, vệt sáng mép trên |
| `test_api_time.py` | quy đổi múi giờ (`to_vn`), `now_vn()` |
| `test_hero.py` | kích thước, tiêu đề, chip, hạt bụi, vòng lan toả |
| `test_cards.py` | thẻ stats, top-langs, chú giải, a11y, mốc thời gian theo UTC+7 |
| `test_clock.py` | góc kim, thứ/ngày, tiến độ ngày, vành, dấu "cập nhật" |
| `test_activity.py` | 14 cột, chuỗi ngày, đường trung bình, nhãn cao nhất, vòng thở hôm nay |
| `test_divider.py` | tia sáng, sóng, bong bóng |
| `test_check_repo.py` | mojibake, URL hỏng, ảnh chết, BOM/CRLF, luật workflow, tài liệu khớp cron |
| `test_cli.py` | cờ CLI, `--smart`, `--dry-run`, chạy như script con |
| `test_status.py` | bố cục dải trạng thái, màu/nhãn từng trạng thái, nhãn tuổi, a11y |
| `test_workflow_states.py` | đọc trạng thái workflow từ API (không gọi mạng), `age_minutes()` |
| `test_workflow_gate.py` | cổng thông minh của `profile-3d.yml` |
| `test_repo_workflows.py` | chạy chính các luật workflow trên repo thật |
| `test_docs.py` | quy ước Markdown, đếm test, mục lục tài liệu |
| `test_repo_assets.py` | ảnh đã commit: XML, viewBox, ngân sách, dấu dữ liệu, giảm chuyển động |

## Kiểm tra vệ sinh repo

Bộ test không kiểm được mọi thứ — BOM, CRLF, link chết, bảng lịch chạy lệch
cron thì `scripts/check_repo.py` lo. Hai lớp này bổ sung cho nhau và cùng chạy
trong `health.yml`:

```
python3 scripts/check_repo.py          # chỉ báo lỗi
python3 scripts/check_repo.py --fix    # tự sửa lỗi vô hình rồi báo lỗi còn lại
```

`test_repo_workflows.py` chạy lại các luật đó **trên repo thật**, nên sai quy
ước là đỏ ngay khi chạy test trên máy chứ không phải đợi CI.

### Những luật chỉ máy thấy

Mỗi luật ở đây ra đời từ một lỗi đã xảy ra thật, và đều thuộc loại **không
công cụ nào báo**: trình duyệt vẫn vẽ, GitHub vẫn hiện, chỉ có người đọc mới
chịu.

| Luật | Lỗi đã xảy ra |
| :-- | :-- |
| Địa danh cũ | ảnh bìa vẫn ghi chỗ ở cũ sau khi đã chuyển nhà |
| Chuỗi 'en' còn tiếng Việt | dải trạng thái hiện `CHỜ MERGE` với người chọn tiếng Anh |
| Chữ SVG thiếu `class` | một nhãn rơi về Times New Roman 16px giữa thẻ |
| `id` trùng trong một ảnh | nửa số hình dùng sai gradient, trông vẫn "có vẻ đúng" |
| Dòng chữ quá dài | chân thẻ đồng hồ bị cắt thành "mỗi 5 p…" |
| Tiêu đề nhảy cấp | mục lục GitHub lệch bậc cả một nhánh tài liệu |
| Cron dày hơn 5 phút | `* * * * *` chỉ chạy mỗi 5 phút, không ai báo |
| Action không ghim | `@main` chạy code khác mỗi ngày |
| Job thiếu `timeout-minutes` | một bước treo giữ runner 6 tiếng |
| Badge shields workflow | ô đỏ "repo or workflow not found" trên trang chủ |
| Rác Python trong ảnh | chữ `None` hay `NaN` in giữa thẻ khi khoá thiếu |
| Bảng Markdown lệch cột | bảng "gãy" trên GitHub, không có lỗi cú pháp |
| Ảnh gọi ra ngoài | ảnh README gọi một URL có thể chết bất cứ lúc nào |

## `helpers.py`

Hai file test không tự thêm `scripts/` vào `sys.path` được — `tests/__init__.py` làm việc đó, còn `helpers.py` là nơi ở chung:

- `SCRIPTS`: đường dẫn tuyệt đối tới `scripts/`.
- `parse(svg)` — `minidom.parseString` bọc lại, ném lỗi nếu XML hỏng.
- `assert_valid_svg(testcase, svg, label)` — kiểm tra 4 thứ tối thiểu: có `<svg`, có `</svg>`, có `xmlns`, gốc là `svg`.
- `render_demo_all()` — vẽ cả 7 thẻ ở chế độ demo ra thư mục tạm rồi trả về `{tên: nội dung}`.

## `test_palette.py` và `test_i18n.py`

Palette:

- Tên theme lạ (`"khong-co"`) rơi về `sky`, không ném lỗi.
- Mọi theme có đủ 14 trường và `as_tokens()` phủ hết các token `@…@` dùng trong CSS.
- `lang_color()` trả đúng màu chính thức cho ngôn ngữ đã biết, ngôn ngữ lạ lấy từ `RAMP`.
- `grade()` trả chữ cái hợp lệ và phần trăm trong `[0, 100]`.

i18n:

- Hai ngôn ngữ có **cùng bộ khoá** — thiếu một khoá là fail ngay.
- Khoá lạ trả về chính tên khoá (để thấy được trong ảnh) chứ không ném `KeyError`.
- `{pct}` được thay đúng; `weekday(0..6)` trả đúng tên.

## `test_primitives.py` (26 test)

Phần lớn test nằm ở đây vì `primitives` là nền của mọi thẻ:

- `esc()`: `&`, `<`, `>`, `"` đều được thoát; chữ Việt **không** bị đổi; chuỗi đã escape vẫn parse được thành XML.
- `human()`: 0 → `0`, 999 → `999`, 1000 → `1k`, 3476 → `3.5k`, 1200000 → `1.2M`.
- `num()`: bỏ `.0` thừa, giữ một chữ số thập phân.
- `icon()`: mọi tên icon trong `ICONS` vẽ ra được path hợp lệ; tên lạ trả chuỗi rỗng chứ không crash.
- `open_svg()`: luôn có `clipPath#cardBody`, viền gradient, `aria-label`, `<title>`.
- `prefers-reduced-motion`: mọi class có `animation` đều xuất hiện trong khối tắt hoạt ảnh.

## `test_hero.py`

- SVG hợp lệ, đúng 1000×280.
- Tên hiển thị xuất hiện trong tiêu đề, đã escape.
- Ba chip `PY` / `JS` / `TS` nằm trong lề phải, không tràn khỏi `viewBox`.
- 14 hạt bụi có `class="dust"` và **không** rơi vào vùng chữ (kiểm tra toạ độ).
- Hai vòng lan toả quanh lõi có chu kỳ 5.2s.
- Bản tiếng Anh không còn chuỗi tiếng Việt nào.

## `test_cards.py`

- Thẻ stats hiện đúng số liệu đầu vào (`2 stars`, `3 followers`…).
- Vòng rank có `stroke-dasharray` và phần trăm đúng với `grade()`.
- Thiếu commits thì hiện `—` chứ không hiện `0` gây hiểu nhầm.
- Top-langs: phần trăm cộng lại ≈ 100, sắp xếp giảm dần, tên dài bị cắt bằng `…`.
- Dữ liệu rỗng vẫn ra thẻ hợp lệ (fallback `Python`).
- A11y: `<title>` khớp `aria-label`, có `<desc>` (trừ divider).

## `test_clock.py`

- 15:04 hiện đúng `15:04` và `Thứ Năm · 19/11/2026`.
- Góc kim tính từ giờ/phút/giây: kiểm tra bằng cách so `transform="rotate(...)"`.
- `animation-delay` âm đúng số giây đã trôi — kim không nhảy sau khi commit.
- Tiến độ ngày: 12:00 → 50%, 00:00 → 0%, 23:59 → ~100%.
- Đủ 60 vạch phút; vành có vệt sáng quét 18 giây/vòng; kim giây có đối trọng.

## `test_activity.py`

- Chỉ lấy 14 ngày cuối, đúng thứ tự cũ → mới.
- Ba ô số: tổng năm, chuỗi hiện tại, chuỗi dài nhất khớp dữ liệu.
- Hôm nay chưa có contribution → chuỗi hiện tại = 0 (không phải 1).
- Ngày 0 vẫn vẽ vạch mờ, không biến mất.
- Đường trung bình chỉ hiện khi dữ liệu lệch; nhãn `cao nhất` ẩn khi hôm nay là cao nhất.
- `contrib is None` → trả `None` để CLI giữ ảnh cũ.

## `test_divider.py` và `test_check_repo.py`

Divider/footer:

- `role="presentation"` (trang trí thuần), không có `aria-label`.
- Hai tia sáng chạy ngược chiều; sóng nằm trong `clip-path`; sáu bong bóng.

`check_repo`:

- URL có `%`-escape sai hoặc giải mã không ra UTF-8 → báo lỗi.
- Mojibake (dấu tiếng Việt bị tách thành hai ký tự Latin, hàm `looks_like_orphan_escape`)
  và chữ Hán/Hàn lạc vào văn bản Việt → báo lỗi.
- Mã màu `#1A2B3C` **không** bị nhầm là escape hỏng.
- Tham chiếu `./assets/khong-co.svg` → báo lỗi; `#anchor` thì bỏ qua.

## `test_cli.py` (39 test)

File lớn nhất, vì CLI là nơi mọi thứ gặp nhau:

- `--demo --all` ghi đủ 7 file SVG, mỗi file parse được.
- `--clock`, `--cards`, `--hero` chỉ ghi đúng nhóm của mình.
- `--theme ocean --lang en` đổi màu và chữ thật.
- Thiếu `GH_USER` → không crash, in hướng dẫn ra stderr.
- `--smart`: lượt hai không đổi `mtime`; không có `--smart` thì luôn ghi.
- `--dry-run`: không tạo file nào nhưng vẫn chạy hết logic.
- `--quiet`: stdout rỗng.
- `--check`: 7/7 hợp lệ; file hỏng → mã thoát 1; thư mục rỗng → mã thoát 1.
- Chạy như **tiến trình con** (`subprocess`) để bắt lỗi thứ tự khai báo hàm.

## `test_workflow_gate.py`

Cổng thông minh của `profile-3d.yml` là shell nằm trong YAML — loại code dễ hỏng mà không ai thấy. Test này:

1. Đọc `.github/workflows/profile-3d.yml` bằng PyYAML, lấy step có `id: gate`.
2. Tạo một `gh` giả trong thư mục tạm, trả về `created_at` và số PushEvent cho trước.
3. Chạy đoạn shell với 5 tình huống: chưa từng chạy, có push mới, không có gì mới, quá 24 giờ, số đếm rác.

Nếu PyYAML không có, 5 test này tự skip chứ không làm đỏ bộ test — CI thì luôn cài PyYAML.

## Viết test mới

1. Chọn file theo bảng ở trên; chưa có thì tạo `test_<module>.py`.
2. `from helpers import SCRIPTS, parse, assert_valid_svg`.
3. Dựng dữ liệu giả **trong test** — không gọi mạng.
4. Gọi hàm vẽ, rồi khẳng định trên **chuỗi SVG** (dễ đọc hơn so sánh cả file).
5. Chạy `python3 -m unittest discover -s scripts/tests -t scripts -v`.

Quy ước: mỗi test một hành vi; tên test nói rõ hành vi đó; không test phần trang trí mà không có lý do (ví dụ: toạ độ hạt bụi thì có lý do — để không đè chữ).

## CI chạy gì

`health.yml` chạy đúng ba bước liên quan tới test:

```bash
python3 -m unittest discover -s scripts/tests -t scripts -v     # tất cả test
python3 scripts/generate_cards.py --demo --all --theme <t> --lang <l>   # 6 theme × 2 ngôn ngữ
python3 scripts/check_repo.py                                    # mojibake, link, YAML, .py
```

Nghĩa là một bảng màu mới hay một ngôn ngữ mới đều được vẽ thử và parse XML trước khi ai đó nhìn thấy nó trên trang chủ.

## `test_status.py`

Dải trạng thái là chỗ dễ sai âm thầm nhất: sai màu thì người xem hiểu ngược
ý nghĩa, sai bề rộng thì viên thuốc cuối bị cắt mất.

- Bề rộng tính đúng theo số workflow; `viewBox` khớp với bề rộng đó.
- Không có hàng nào → vẫn vẽ được một viên dự phòng, không vỡ XML.
- Nhãn lấy từ `i18n`: `ĐẠT` (vi) và `PASSING` (en) không lẫn vào nhau.
- Trạng thái lạ rơi về "không rõ" chứ không crash.
- Vòng nhấp nháy chỉ có ở trạng thái "đang sống"; chấm đỏ lỗi đứng yên.
- Mọi trạng thái trong `STATE_STYLE` phải có khoá i18n ở **cả hai** ngôn ngữ.
- Vẽ hợp lệ với 6 theme × 2 ngôn ngữ.
