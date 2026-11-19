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
| `status.py` | dải trạng thái các workflow |
| `api.py` | client GitHub REST + GraphQL |
| `../generate_cards.py` | CLI ghép mọi thứ lại |
| `../tests/` | 163 unit test |
| `../../docs/ARCHITECTURE.md` | vì sao chia module như vậy |

## `palette.py`

- `Palette` là dataclass bất biến, 14 trường; `as_tokens()` đổi thành bảng `@ACCENT@` để thay vào CSS/defs.
- `THEMES`: `sky`, `emerald`, `violet`, `sunset`, `ocean`, `mono`. Tên lạ rơi về `DEFAULT_THEME` chứ không crash.
- `LANG_COLORS` giữ mã màu chính thức của GitHub Linguist; `lang_color(name, i)` trả màu đã biết, ngôn ngữ lạ lấy màu từ `RAMP` theo thứ hạng.
- `grade(stats)` → `("B+", 74)` để vẽ vòng rank.

## `i18n.py`

- `LANGS = ("vi", "en")`; mọi chuỗi nằm trong `STRINGS[lang]`.
- `get("vi")` trả một `Translator`; gọi `t("hero.sub")` hoặc `t("stats.progress", pct=74)` — có `{}` format.
- Khoá thiếu thì trả chính tên khoá (dễ thấy trong ảnh), không ném lỗi giữa workflow.
- `t.weekday(3)` → `"Thứ Năm"` / `"Thursday"` cho dòng ngày của đồng hồ.

## `primitives.py`

- `esc()` thoát `& < > " '` — mọi chuỗi trước khi vào SVG đều phải qua đây.
- `human()` → `1.2k`, `3.5k`, `12.3k`; `num()` cắt số thực cho gọn thuộc tính.
- `ICONS`: 12 icon vẽ bằng path (star, fork, repo, people, eye, commit, flame, trophy, target, clock…), `icon(name, x, y, color)` chèn vào toạ độ.
- `CSS` + `DEFS`: khai báo một lần cho mỗi file, chứa token `@…@` được `css_block()` / `defs_block()` thay bằng màu thật.
- `open_svg()` mở thẻ: `<svg>` + CSS + defs + nền + viền gradient + `clipPath#cardBody` để lớp trang trí không tràn góc bo.
- Có khối `@media (prefers-reduced-motion: reduce)` tắt hết hoạt ảnh khi người xem yêu cầu.

## `hero.py`

`hero(pal, dt, t)` → 1000×280.

- Nền: lưới mờ, ba quầng sáng trôi, sao nhấp nháy, dải quét.
- Trái: monogram "SP" trong hệ quỹ đạo ba hạt sáng.
- Phải: tên, mô tả, ba chip công nghệ bồng bềnh, dòng gõ chữ, con dấu thời gian.
- Mọi lớp trang trí nằm trong `<g clip-path="url(#cardBody)">`.

## `divider.py`

- `divider(pal)` → 1000×26: gradient ngang + tia sáng chạy + hai quầng mờ.
- `footer(pal, t)` → 1000×200: lời cảm ơn, khẩu hiệu, hai lớp sóng trôi ngược chiều.
- `_wave()` sinh path sóng bằng hàm sin, tham số là biên độ và chu kỳ — muốn sóng cao hơn chỉ cần đổi số.

## `cards.py`

- `stats_card()`: 6 ô số liệu (stars, forks, repos, followers, following, commits) + vòng rank.
- `langs_card()`: thanh xếp chồng theo byte code + chú giải 2 cột, mỗi ngôn ngữ có thanh tiến độ riêng.
- `waiting_card()`: thẻ tạm khi chưa có token — nói rõ cần chạy workflow nào, không hiện số liệu giả.
- `_rank_ring()` dùng `stroke-dasharray` để vẽ đúng phần trăm, chữ phần trăm đi qua i18n.

## `clock.py`

- `_dial()`: 60 vạch phút + 12 vạch giờ; vạch giờ dài và sáng hơn.
- `_hands()`: xoay sẵn nhóm kim tới góc hiện tại rồi gắn `animation-delay` âm → kim khớp giờ ngay khung đầu.
- `_greeting_key()`: chia ngày thành sáng / trưa / chiều / tối / đêm; `_sun_moon()` đổi icon theo giờ.
- Thanh tiến độ ngày = số phút đã trôi / 1440.

## `activity.py`

- `activity_card(pal, contrib, dt, t)`; `contrib` đến từ `api.contributions()`.
- Ba ô số: tổng năm, chuỗi hiện tại, chuỗi dài nhất.
- 14 cột cuối, nhãn thứ theo ngôn ngữ; cột hôm nay có điểm nhấp nháy.
- `contrib is None` → trả `None` để CLI giữ ảnh cũ.

## `api.py`

- `api()` gọi REST, `contributions()` gọi GraphQL — cả hai thử lại 3 lần với backoff.
- Mọi lỗi (mạng, 403, 404, JSON hỏng, token thiếu) đều trả `None` / giá trị rỗng; workflow quyết định có báo đỏ hay không qua `--strict`.
- `collect_user()` gom user + repos + ngôn ngữ + commit trong một dict phẳng để `cards.py` khỏi phải biết gì về HTTP.
- `_streaks()` tính chuỗi ngày từ danh sách contribution.

## Quy ước khi sửa `svgkit`

1. Không hard-code màu — lấy từ `pal` (nếu thiếu màu, thêm vào `Palette` và cả 6 theme).
2. Không hard-code chữ — thêm khoá vào `STRINGS` cho cả `vi` và `en`.
3. Mọi chuỗi vào SVG phải qua `esc()`.
4. Thêm thẻ mới thì thêm test trong `scripts/tests/` và một dòng vào bảng trên.
5. Chạy `python3 -m unittest discover -s scripts/tests -t scripts` trước khi commit — CI chạy đúng lệnh đó.
### Cờ CLI đáng chú ý

```bash
--all / --cards / --hero / --clock / --activity   # chọn nhóm ảnh
--demo                                            # dữ liệu mẫu, không gọi API
--theme sky|emerald|violet|sunset|ocean|mono      # bảng màu
--lang vi|en                                      # ngôn ngữ
--strict                                          # API lỗi là exit 1
--smart                                           # chỉ ghi khi dữ liệu đổi
--dry-run                                         # không ghi file nào
--quiet                                           # chỉ in lỗi
--check [--out DIR]                               # parse lại toàn bộ SVG đã có
--version / --list-themes / --list-langs
```

### `--smart` hoạt động thế nào

- `data_hash(payload)` → 12 ký tự SHA-256 của dữ liệu (không gồm thời gian).
- `stamp_data_mark(svg, hash)` chèn `<!-- data:… -->` ngay trước `</svg>`.
- `read_mark(path)` đọc lại dấu đó từ file cũ.
- `write(name, content, hash)` so sánh; trùng thì bỏ qua, khác thì ghi atomic.

Ba hàm này đều là hàm thuần (trừ `write`) nên test được mà không cần đĩa.

### Quy ước đặt tên

| Loại | Mẫu | Ví dụ |
| :-- | :-- | :-- |
| Hàm vẽ công khai | `<thẻ>_card` | `stats_card`, `activity_card` |
| Hàm phụ trong module | `_<việc>` | `_rank_ring`, `_hands`, `_wave` |
| Khoá i18n | `<module>.<mục>` | `hero.sub`, `act.avg`, `desc.stats` |
| Icon | danh từ tiếng Anh | `star`, `flame`, `trophy` |
| Class CSS | camelCase | `fadeUp`, `pulseSlow`, `secHand` |

### Hiệu năng

- Một lượt `--all` ở chế độ demo: **~0,2 giây** cho 7 ảnh, không I/O mạng.
- Ảnh lớn nhất là `live-clock.svg` (~20 KB) vì có 60 vạch + CSS đầy đủ.
- Toàn bộ CSS/defs lặp lại trong từng file — đổi lại là mỗi ảnh **tự đứng một mình**, không phụ thuộc file ngoài, nên dùng được ở bất cứ đâu (README, trang web, PDF).

