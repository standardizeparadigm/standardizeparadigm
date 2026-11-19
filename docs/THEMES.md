# 🎨 Sáu bảng màu

Mọi hình trong `assets/` vẽ từ cùng một bộ token màu. Đổi một token là đổi cả trang.

```bash
python3 scripts/generate_cards.py --all --theme ocean   # vẽ lại toàn bộ theo bảng màu ocean
python3 scripts/generate_cards.py --list-themes        # xem danh sách + mã màu
```

| Theme | Nhấn chính | Cảm giác |
| :-- | :-- | :-- |
| `sky` | `#38BDF8` | mặc định, xanh trời, sáng và trung tính |
| `emerald` | `#34D399` | xanh ngọc, dịu mắt |
| `violet` | `#A78BFA` | tím, hợp giao diện tối |
| `sunset` | `#FB923C` | cam hoàng hôn, ấm |
| `ocean` | `#22D3EE` | xanh biển, lạnh và sắc |
| `mono` | `#E5E5E5` | đen trắng, in ra vẫn đẹp |

## `sky` — mặc định

- Nền `#0B1220 → #060A14`, nhấn `#38BDF8`, nhấn phụ `#0EA5E9`, nhấn nhạt `#7DD3FC`.
- Chọn làm mặc định vì tương phản chữ trắng trên nền đậm đạt ~12:1, đọc lâu không mỏi.
## `emerald`

- Nhấn `#34D399`, phụ `#10B981`, nhạt `#6EE7B7`.
- Xanh ngọc có độ sáng cao nên hợp làm màu cho thanh tiến độ và số liệu nhỏ.
## `violet`

- Nhấn `#A78BFA`, phụ `#8B5CF6`, nhạt `#C4B5FD`.
- Màu tiêu đề riêng `#F3EBFF` (không dùng trắng tinh) để chữ tím không bị "chói".
## `sunset`

- Nhấn `#FB923C`, phụ `#F97316`, nhạt `#FDBA74`.
- Cam ấm; chữ phụ vẫn dùng xám xanh để không bị "nóng" cả trang.
## `ocean`

- Nhấn `#22D3EE`, phụ `#06B6D4`, nhạt `#67E8F9`.
- Lạnh và sắc; hợp với ảnh chụp màn hình code.
