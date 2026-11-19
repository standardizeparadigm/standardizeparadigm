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

