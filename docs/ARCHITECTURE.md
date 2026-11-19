# 🏗️ Kiến trúc

Trang này không có server. Mọi thứ là file tĩnh sinh ra bởi GitHub Actions rồi commit lại vào repo.

```
 GitHub API ──┐
              ├─▶ svgkit (Python) ──▶ assets/*.svg ──▶ commit ──▶ README hiển thị
   giờ hệ thống ┘
```

Ba câu để nhớ:

1. **Không phụ thuộc dịch vụ ngoài** — không badge server nào có thể trả 503.
2. **Lỗi thì giữ ảnh cũ** — không bao giờ ghi đè bằng thẻ rỗng.
3. **Hoạt ảnh nằm trong file** — ảnh đứng yên vẫn đẹp, trình duyệt thì thấy nó chạy.

## Luồng dữ liệu

```
api.collect_user(login, token)
   ├── /users/{login}            → name, followers, following, public_repos
   ├── /users/{login}/repos      → stars, forks, ngôn ngữ từng repo
   └── /search/commits           → tổng commit
        ↓
   dict phẳng: {name, stars, forks, repos, followers, following, commits, langs{}}
        ↓
   stats_card(...) / langs_card(...)   ← chỉ nhận dict, không biết gì về HTTP
        ↓
   write("stats.svg", nội dung, vân_tay)
```

Nhờ vậy `cards.py` test được bằng dữ liệu giả, và `api.py` thay được bằng bản khác mà không sửa gì phần vẽ.

## Vì sao chỉ dùng thư viện chuẩn

- `pip install` trong CI là chỗ hay hỏng nhất (wheel thiếu, mạng chậm, version xung đột).
- SVG chỉ là văn bản — không cần thư viện đồ hoạ nào để ghép chuỗi.
- Máy nào có Python 3.8+ là chạy được, kể cả máy của bạn cùng lớp không có mạng.

Đổi lại: phải tự viết `esc()`, tự tính toạ độ, tự quản lý màu. Đó là cái giá đã trả và đã có test.

## Ranh giới module

| Module | Được biết | Không được biết |
| :-- | :-- | :-- |
| `api.py` | HTTP, JSON, token | không biết SVG |
| `cards.py`, `hero.py`, `clock.py`, `activity.py`, `divider.py` | `palette`, `i18n`, `primitives` | không biết HTTP, không đọc file |
| `primitives.py` | chuỗi, số | không biết dữ liệu GitHub |
| `palette.py` | mã màu | không biết gì khác |
| `i18n.py` | chuỗi | không biết gì khác |
| `generate_cards.py` | tất cả | là nơi duy nhất đọc/ghi file |

Chỉ `generate_cards.py` chạm vào đĩa. Đó là lý do toàn bộ phần vẽ test được mà không cần thư mục tạm.

## Token màu

`Palette.as_tokens()` sinh bảng thay thế:

```
@BGTOP@ @BGBOT@ @PANEL@ @STROKE@ @TITLE@ @TEXT@ @LABEL@ @DIM@
@ACCENT@ @ACCENT2@ @ACCENT3@ @DEEP@ @FONT@ @MONO@
```

`css_block(pal)` và `defs_block(pal)` thay toàn bộ `@…@` trong `CSS`/`DEFS` bằng màu thật. Vì vậy **không có mã màu nào hard-code** trong phần vẽ — đổi theme là đổi cả 7 ảnh.

## i18n

- `STRINGS["vi"]` và `STRINGS["en"]` phải cùng bộ khoá; test so sánh hai tập khoá.
- `Translator.__call__(key, **kw)` thay `{tên}`; khoá thiếu trả lại chính tên khoá để lỗi hiện ra trong ảnh thay vì làm sập workflow.
- Tên thứ trong tuần là dữ liệu (`WEEKDAYS`), không phải chuỗi ghép tay.

