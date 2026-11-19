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

