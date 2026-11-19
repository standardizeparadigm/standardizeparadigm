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
