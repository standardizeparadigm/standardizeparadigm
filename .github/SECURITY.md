# Báo lỗi bảo mật

Trang này là một trang cá nhân tĩnh: HTML/SVG + GitHub Actions. Không có server,
không có cơ sở dữ liệu, không có tài khoản người dùng.

## Có gì đáng lo

- **Token bị lộ**: mọi workflow dùng `secrets.GITHUB_TOKEN` có sẵn của repo, không có token nào nằm trong file. Nếu bạn thấy token thật trong repo, đó là lỗi nghiêm trọng — báo ngay.
- **Nội dung SVG chèn từ ngoài**: mọi chuỗi lấy từ GitHub API đều đi qua `svgkit.primitives.esc()` trước khi vào file. Nếu tìm được chỗ nào chưa escape, đó là lỗi thật.
- **Workflow chạy mã lạ**: action bên thứ ba duy nhất là `yoshi389111/github-profile-3d-contrib`, đã ghim phiên bản `v0.9.3`.

## Cách báo

1. Mở **Security → Report a vulnerability** (báo riêng tư), hoặc
2. Nếu không nhạy cảm: mở issue bình thường.

Mình sẽ trả lời trong vài ngày. Cảm ơn bạn đã dành thời gian
