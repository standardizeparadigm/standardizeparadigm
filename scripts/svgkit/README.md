# `svgkit` — thư viện vẽ thẻ SVG

Chiếc hộp đựng mọi thứ cần để vẽ một tấm thẻ đẹp: màu, chữ, hình khối, hoạt ảnh. **Chỉ dùng thư viện chuẩn của Python** — không `pip install`, không mạng, chạy được trên máy nào có Python 3.8+.

```bash
python3 scripts/generate_cards.py --demo --all --out /tmp/xem-thu
```

| Module | Việc |
| :-- | :-- |
| `palette.py` | 6 bảng màu, màu chính thức của ~30 ngôn ngữ, cách tính rank |
| `i18n.py` | toàn bộ chuỗi tiếng Việt / tiếng Anh |
| `primitives.py` | escape XML, icon path, CSS + defs dùng chung, khung thẻ bo góc |
| `hero.py` | ảnh bìa 1000×280 |
| `divider.py` | đường kẻ 1000×26 và chân trang 1000×200 |
| `cards.py` | thẻ stats, top-langs, thẻ chờ |
| `clock.py` | đồng hồ sống 640×258 |
| `activity.py` | thẻ hoạt động 14 ngày |
| `api.py` | client GitHub REST + GraphQL |
| `../generate_cards.py` | CLI ghép mọi thứ lại |
| `../tests/` | hơn 100 unit test |

