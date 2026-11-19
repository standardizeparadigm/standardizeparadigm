# 🤝 Đóng góp cho Standardize Paradigm

Cảm ơn bạn đã quan tâm đến trang cá nhân này! Mình là học sinh lớp 7 tự học code — mọi đóng góp, dù nhỏ, đều rất đáng giá.

## 🚀 Cách bắt đầu

1. **Fork** repo này về tài khoản của bạn.
2. **Clone** repo đã fork:
   ```bash
   git clone https://github.com/<username-cua-ban>/standardizeparadigm.git
   cd standardizeparadigm
   ```
3. Tạo **branch** mới cho công việc của bạn:
   ```bash
   git checkout -b feat/ten-ban-than
   ```
4. Sửa, commit và push:
   ```bash
   git add .
   git commit -m "feat: mô tả ngắn gọn thay đổi"
   git push origin feat/ten-ban-than
   ```
5. Mở **Pull Request** trên GitHub và mô tả thay đổi.

## 📝 Quy ước commit

Dùng tiền tố tiếng Anh theo kiểu conventional commits (phần mô tả viết tiếng Việt cũng được):

| Tiền tố | Ý nghĩa | Ví dụ |
| :-- | :-- | :-- |
| `feat:` | Tính năng mới / mục mới | `feat: thêm mục câu hỏi thường gặp` |
| `fix:` | Sửa lỗi | `fix: sửa liên kết sai ở mục liên hệ` |
| `docs:` | Thay đổi tài liệu | `docs: cập nhật hướng dẫn đóng góp` |
| `style:` | Định dạng, khoảng trắng, mã màu | `style: chỉnh màu badge` |
| `chore:` | Việc vặt, bảo trì | `chore: cập nhật con dấu cập nhật` |

## 🧪 Trước khi mở Pull Request

Chạy bộ kiểm tra ngay trên máy bạn (không cần cài gì):

```bash
python3 scripts/check_repo.py                          # sức khỏe repo
python3 -m unittest discover -s scripts/tests -t scripts   # hơn 600 unit test
```

Chúng chỉ ra ký tự lỗi encoding, SVG hỏng, link chết, workflow sai — đúng những gì CI của repo kiểm tra.

`check_repo.py` còn kiểm tra **vệ sinh file**: BOM UTF-8, xuống dòng CRLF, ký tự
điều khiển dưới U+0020, file không phải UTF-8 hợp lệ, khoảng trắng thừa cuối dòng
(mức cảnh báo). Editor nào tự thêm BOM thì tắt đi — CI sẽ đỏ.

**Sửa ảnh thì sửa code, đừng sửa tay file SVG.** Toàn bộ `assets/*.svg` do
`scripts/generate_cards.py` + `scripts/svgkit/` sinh ra; chạm tay vào SVG là
lượt workflow kế tiếp sẽ ghi đè.

## 🧩 Thêm một workflow mới

Ba chỗ, đừng bỏ chỗ nào:

1. `.github/workflows/ten-moi.yml`
2. `WORKFLOWS` trong `scripts/svgkit/status.py` — thiếu chỗ này thì dải trạng
   thái lặng lẽ bỏ sót workflow của bạn (đã có test bắt lỗi).
3. Bảng lịch chạy trong `README.md` và `docs/WORKFLOWS.md`

Nhớ thêm `workflow_dispatch` nếu muốn chạy tay — nút đó chỉ hiện khi file đã có
trên nhánh mặc định.

## 🐛 Báo lỗi & yêu cầu tính năng

- Mở issue theo mẫu có sẵn trong `.github/ISSUE_TEMPLATE/`.
- Mô tả rõ, kèm ảnh chụp màn hình nếu là lỗi giao diện.

## 📜 Quy tắc nhỏ

- Không spam, không phân biệt đối xử.
- Nếu bạn là bạn cùng tuổi và muốn làm project chung, hãy nhắn mình qua issue hoặc Discord — mình rất mong được làm quen!

## 📄 Giấy phép

Dự án này dùng giấy phép MIT — xem file `LICENSE`.
