# 🧪 Kiểm thử

Bộ test chạy bằng `unittest` của Python — không cần `pytest`, không cần mạng, không cần token. Toàn bộ dữ liệu GitHub trong test là dữ liệu giả dựng sẵn.

```bash
python3 -m unittest discover -s scripts/tests -t scripts        # chạy hết
python3 -m unittest discover -s scripts/tests -t scripts -v     # in tên từng test
python3 -m unittest tests.test_clock -v                          # chỉ một file
```

Hiện có **159 test** trên 11 file, chạy xong trong chưa tới 1 giây.

## Bản đồ

| File | Số test | Kiểm tra điều gì |
| :-- | --: | :-- |
| `test_palette.py` | 11 | 6 theme, token, màu ngôn ngữ, cách tính rank |
| `test_i18n.py` | 13 | đủ khoá vi/en, thứ trong tuần, dự phòng khi thiếu khoá |
| `test_primitives.py` | 26 | escape XML, `human()`/`num()`, icon, khung thẻ, giảm chuyển động |
| `test_hero.py` | 12 | kích thước, tiêu đề, chip, hạt bụi, vòng lan toả |
| `test_cards.py` | 15 | thẻ stats, top-langs, chú giải, a11y |
| `test_clock.py` | 10 | góc kim, thứ/ngày, tiến độ ngày, vành |
| `test_activity.py` | 13 | 14 cột, chuỗi ngày, đường trung bình, nhãn cao nhất |
| `test_divider.py` | 9 | tia sáng, sóng, bong bóng |
| `test_check_repo.py` | 16 | bắt mojibake, URL hỏng, tham chiếu ảnh chết |
| `test_cli.py` | 39 | cờ CLI, `--smart`, `--dry-run`, chạy như script con |
| `test_workflow_gate.py` | 5 | cổng thông minh của `profile-3d.yml` |

## `helpers.py`

Hai file test không tự thêm `scripts/` vào `sys.path` được — `tests/__init__.py` làm việc đó, còn `helpers.py` là nơi ở chung:

- `SCRIPTS`: đường dẫn tuyệt đối tới `scripts/`.
- `parse(svg)` — `minidom.parseString` bọc lại, ném lỗi nếu XML hỏng.
- `assert_valid_svg(testcase, svg, label)` — kiểm tra 4 thứ tối thiểu: có `<svg`, có `</svg>`, có `xmlns`, gốc là `svg`.
- `render_demo_all()` — vẽ cả 7 thẻ ở chế độ demo ra thư mục tạm rồi trả về `{tên: nội dung}`.

