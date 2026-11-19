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
| `status.py` | `palette`, `i18n`, `primitives` | không gọi API (nhận `rows` đã chuẩn hoá từ `api.py`) |
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

## `primitives` — nền của mọi thẻ

`open_svg()` lo 6 việc mà thẻ nào cũng cần:

1. Mở `<svg>` với `role="img"`, `aria-label`, `<title>`, `<desc>`.
2. Nhúng CSS đã thay token.
3. Nhúng `<defs>`: gradient, filter glow, mask.
4. Khai báo `clipPath#cardBody` theo bán kính bo góc.
5. Vẽ nền + hai quầng sáng **bên trong clip**.
6. Vẽ viền gradient mảnh.

Nhờ bước 4, mọi lớp trang trí (sóng, sao, bụi, halo) không bao giờ tràn ra ngoài góc bo tròn.

## Chiến lược hoạt ảnh

Hai công cụ, chọn theo tình huống:

**CSS keyframes** — khi chỉ cần lặp vô hạn một kiểu biến đổi: `pulse`, `twinkle`, `floatY`, `spin`, `sheen`, `wave`. Ngắn, dễ đọc, trình duyệt tối ưu tốt.

**SMIL (`<animate>`)** — khi cần chạy đúng một lần rồi dừng, hoặc khi **khung đầu tiên phải sạch**:

- Vệt sáng hero: `values="-460;1012;1012"` — ở t=0 hình chữ nhật nằm ngoài vùng chữ, nên trình xem tĩnh không thấy mảng trắng.
- Kim đồng hồ: CSS vì cần chạy mãi; nhưng nhóm kim được xoay sẵn bằng `transform` tĩnh trước.

Nguyên tắc: **nếu hoạt ảnh làm khung đầu tiên xấu, đổi sang SMIL hoặc đổi trạng thái mặc định**.

## Thời gian trong một file tĩnh

Một file SVG không chạy được code, nên "đồng hồ sống" phải giải bằng dữ liệu:
thay vì một chuỗi `15:04`, `clock.py` phát ra **84 ô chữ chồng lên nhau** —
24 ô giờ ở `x=308`, 60 ô phút ở `x=324`, tất cả cùng `y=124`.

```
.liveHour text, .liveMin text { opacity: 0; animation: slotMin 3600s linear infinite }
.liveHour text                { animation-name: slotHour; animation-duration: 86400s }
.nowSlot                      { opacity: 1 }
```

- Mỗi ô có `animation-delay` âm bằng `((v - hiện_tại) mod chu_kỳ) * bước - giây_đã_trôi`,
  nên ô của phút hiện tại đang ở đúng đầu chu kỳ tại thời điểm tải (không lệch
  theo lúc mở trang).
- Ô `nowSlot` khai báo `opacity: 1` **trước** để trình xem tĩnh — vốn không
  chạy CSS — hiện đúng giờ của ảnh chụp.
- `prefers-reduced-motion` tắt cả 84 ô: người bật "giảm chuyển động" thấy
  đúng giờ của ảnh chụp, đứng yên, không thấy số nhảy.

Đánh đổi: file to thêm ~12 KB. Chấp nhận được — nó mua được việc số phút
đúng **mỗi phút** dù GitHub chỉ cho cron 5 phút một lần, và dù người xem mất
mạng hay mở file offline.

## Ghi file: atomic + vân tay

**Atomic:** ghi ra `.tmp-xxxx.svg` cùng thư mục rồi `os.replace()`. Mất mạng hay bị kill giữa chừng thì file cũ vẫn nguyên — không bao giờ có ảnh nửa vời.

**Vân tay:** mỗi ảnh mang `<!-- data:0123456789ab -->` = SHA-256 của dữ liệu đã dùng (12 ký tự đầu, không gồm thời gian). Chế độ `--smart` đọc dấu này trước khi ghi:

- khác → ghi và commit,
- giống → bỏ qua, không tạo commit rỗng.

## Xử lý lỗi

| Tình huống | Hành vi |
| :-- | :-- |
| Mạng lỗi / 5xx | thử lại 3 lần, backoff tăng dần |
| 403 rate limit | đọc `Retry-After`, chờ rồi thử lại |
| 404 sai user | trả `None`, in hướng dẫn sửa `GH_USER` |
| Thiếu token | dùng quota công khai; thẻ chờ thay vì số liệu giả |
| GraphQL lỗi | `activity_card` trả `None`, ảnh cũ được giữ |

`--strict` đổi "im lặng giữ ảnh cũ" thành mã thoát 1, để workflow báo đỏ khi bạn muốn biết.

## Kiểm tra tự động những gì

`scripts/check_repo.py` chạy trong CI và trên máy, kiểm cả thứ mà test
thường bỏ qua — vì đó là những lỗi đã xảy ra thật ở đây:

| Nhóm | Bắt được |
| :-- | :-- |
| SVG | XML hỏng, thiếu `<title>` (trừ ảnh tự khai trang trí) |
| Chữ | BOM, CRLF, UTF-8 hỏng, ký tự thay thế, mojibake |
| Markdown | link nội bộ chết, ảnh không tồn tại |
| Workflow | thiếu `permissions`/`concurrency`/`timeout-minutes`, `git push` không có cổng bot |
| Tài liệu ↔ YAML | bảng lịch chạy sai cron, workflow không có dòng nào trong bảng |
| Ảnh | `assets/*.svg` không được nhúng ở đâu (ảnh chết), ảnh nặng quá 40 KB |
| Tài liệu | bài trong `docs/` không được dẫn tới, câu "hơn N unit test" đã sai, README dài quá 360 dòng |
| Python | mọi file biên dịch được và mở đầu bằng docstring |
| Merge | dấu `<<<<<<<` còn sót trong bất kỳ file văn bản nào |

## Bảo mật

- **Escaping**: mọi chuỗi từ API đi qua `esc()` trước khi vào SVG. Tên repo hay tên người có `<script>` cũng chỉ là chữ.
- **Token**: chỉ nằm trong `secrets.GITHUB_TOKEN`, không ghi ra file, không in ra log.
- **Không chạy mã lạ**: không `eval`, không render HTML từ dữ liệu ngoài; SVG sinh ra là văn bản do ta kiểm soát.
- **Action bên thứ ba duy nhất**: `github-profile-3d-contrib`, ghim `v0.9.3`.
- **Cổng chặn vòng lặp**: mọi workflow có `git push` đều kiểm
  `github.actor != 'github-actions[bot]'`, nếu không commit của bot lại kích
  hoạt chính nó. `check_repo.check_workflow_hygiene()` bắt buộc điều này.

## Quy ước số

- `human(n)`: `< 1000` giữ nguyên, `1000 → 1k`, `3476 → 3.5k`, `1200000 → 1.2M`. Một chữ số thập phân, bỏ `.0`.
- Phần trăm: một chữ số thập phân (`89.3%`), tính trên **tổng thật** chứ không trên tập đã cắt.
- Rank: `grade()` cho chữ cái + phần trăm; vòng rank vẽ đúng phần trăm đó, không làm tròn lên.
- Thời gian: luôn `Asia/Ho_Chi_Minh` (UTC+7), định dạng `%d/%m · %H:%M`.
  Quy đổi nằm ở **một chỗ duy nhất** — `api.to_vn()` — và mỗi hàm vẽ tự gọi
  nó ở dòng đầu, không tin mốc thời gian người gọi đưa xuống. Đây là bài học
  từ lần ảnh đồng hồ hiển thị giờ UTC dưới nhãn "giờ Việt Nam".

## Khả năng truy cập

- `role="img"` + `aria-label` + `<title>` + `<desc>` cho mọi thẻ nội dung.
- `divider.svg` là `role="presentation"` — trang trí thì im lặng.
- Khối `@media (prefers-reduced-motion: reduce)` tắt toàn bộ hoạt ảnh CSS cho người cần.
- Tương phản: chữ chính trên nền đậm đạt ≥ 7:1 ở cả 6 theme (đo bằng mã màu trong `palette.py`).

## Thêm một thẻ mới

Checklist 7 bước:

1. Tạo `scripts/svgkit/<ten>.py` với một hàm `xxx_card(pal, data, dt, t, width=640, height=258)`.
2. Mở bằng `open_svg(pal, width, height, t("<ten>.title"), desc=t("desc.<ten>"))`.
3. Mọi màu lấy từ `pal`, mọi chữ lấy từ `t(...)`, mọi chuỗi qua `esc()`.
4. Vẽ trong khung của `clipPath#cardBody` nếu có lớp trang trí.
5. Thêm khoá i18n cho **cả** `vi` và `en`.
6. Thêm test vào `scripts/tests/`, thêm một dòng vào bảng trong `docs/ANIMATIONS.md`.
7. Thêm cờ CLI nếu thẻ cần dữ liệu riêng, và một dòng trong workflow.
