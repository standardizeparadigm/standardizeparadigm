# 🎞️ Kiểm kê hoạt ảnh

Mỗi hình trong `assets/` đều có chuyển động riêng, tất cả đều viết bằng **CSS keyframes** hoặc **SMIL** ngay trong file SVG — không JavaScript, không thư viện, không request nào thêm.

| Hình | Hoạt ảnh chính |
| :-- | :-- |
| `hero.svg` | quỹ đạo xoay, sao nhấp nháy, bụi sáng bay lên, vòng lan toả, chip bồng bềnh, vệt sáng quét chữ, gõ chữ |
| `divider.svg` | tia sáng chạy dọc đường kẻ |
| `footer.svg` | hai lớp sóng trôi ngược chiều |
| `stats.svg` | vòng rank tự vẽ, số đếm lên, vệt sáng |
| `top-langs.svg` | thanh xếp chồng lớn dần, chú giải hiện lần lượt |
| `live-clock.svg` | ba kim quay, chấm nhấp nháy, thanh tiến độ ngày |
| `activity.svg` | cột mọc lên, điểm hôm nay nhấp nháy |

## Hero — lớp nền

- **Lưới mờ**: tĩnh, làm nền cho phần chữ.
- **Ba quầng sáng** (`driftA` 16s, `driftB` 21s, `driftC` 26s): trôi chậm theo các hướng khác nhau để nền không bao giờ "đứng hình".
- **Sao** (`twinkle` 4s, độ trễ so le): mờ 12% rồi sáng 85%, giống sao thật.
- **Dải quét** (`scan` 7.5s): một vệt sáng mảnh chạy từ trên xuống; đặt `opacity="0"` để khung hình tĩnh vẫn sạch.

## Hero — quỹ đạo quanh monogram

- Vòng nét đứt bán kính 55 xoay một vòng 26 giây (`spinSlow`), vòng cung 36 xoay ngược 34 giây (`spinRev`).
- Ba hạt sáng nằm trên ba quỹ đạo khác nhau, mỗi hạt một tốc độ (15s / 22s / 29s) — nhìn như hệ hành tinh nhỏ.
- Hạt sáng dùng `filter="url(#glow)"` để có quầng; lõi "SP" đứng yên làm điểm neo.

## Hero — chip công nghệ

- Ba chip `PY` / `JS` / `TS` nằm bên phải, xếp so le theo trục dọc.
- Mỗi chip dùng `floatY` (5.2s) lệch pha 92ms / 140ms / 188ms, nên chúng nhấp nhô lệch nhau chứ không đồng loạt.

## Hero — tiêu đề và vệt sáng

- Tiêu đề dùng gradient dọc (`titleGrad`), vẽ bằng **một** phần tử `<text>`.
- Vệt sáng là một `<text>` trắng mờ 28% bị cắt bởi `clipPath` chứa hình chữ nhật chạy ngang.
- Chuyển động bằng SMIL: `values="-460;1012;1012"` — quét hết chữ trong 55% thời gian rồi nghỉ. Dùng SMIL vì nếu trình xem không chạy hoạt ảnh, khung đầu vẫn nằm ngoài vùng chữ (không bị mảng trắng đè lên).

## Hero — gõ chữ

- Ba câu `hero.type1/2/3` cùng nằm ở một chỗ; mỗi câu có `clipPath` riêng giãn từ 0 đến hết câu.
- Chu kỳ 25.2 giây: câu hiện dần ~1.5s, giữ ~3.9s, xoá, nghỉ — rồi tới câu kế.
- Con trỏ `|` nhấp nháy bằng `blink` (1.05s, `steps(1, end)`) để giống terminal thật.

## Divider — tia sáng

- Đường kẻ là gradient ngang, hai đầu mờ dần.
- Một hình thoi nhỏ chạy hết chiều ngang (SMIL, `repeatCount="indefinite"`), kèm hai quầng mờ để lại vệt.

## Footer — sóng

- Hai lớp `<path>` sóng, lớp sau lệch pha và trong hơn.
- `wave` trôi sang trái 14 giây, `wave2` trôi ngược 19 giây (`animation-direction: reverse`) — hai lớp chồng nhau tạo cảm giác nước chảy.
- Mỗi lớp nằm trong `<g class="wave">` lồng trong `<g transform="translate(...)">` để hoạt ảnh CSS không đè lên transform tĩnh.
- Toàn bộ sóng nằm trong `clip-path="url(#cardBody)"` nên không tràn ra ngoài góc bo tròn.

## Stats — vòng rank

- Vòng nền mờ + vòng tiến độ có `stroke-dasharray`/`stroke-dashoffset` chạy từ 0% tới đúng phần trăm (74% với rank B+).
- Sáu ô số liệu và nhãn dùng `fadeUp` (0.72s) với độ trễ tăng dần 60ms mỗi ô.
- Một vệt sáng mảnh (`sheen`, 6.5s) quét ngang giữa thẻ mỗi chu kỳ.

## Top languages — thanh xếp chồng

- Mỗi đoạn ngôn ngữ là một `<rect>`, chiều rộng chạy từ 0 tới đúng tỉ lệ bằng SMIL `animate` với `calcMode="spline"` (nảy nhẹ ở cuối).
- Độ trễ tăng 60ms mỗi đoạn nên thanh "mọc" từ trái sang phải.
- Chú giải 2 cột hiện lần lượt bằng `fadeUp`, thanh tiến độ nhỏ bên dưới mỗi ngôn ngữ dùng `growIn` (scaleX từ 0).

## Live clock — kim và tiến độ ngày

- Ba kim: `secHand` 60s, `minHand` 3600s, `hourHand` 43200s — mỗi kim quay đúng một vòng theo chu kỳ thật của nó.
- Trước khi vẽ, nhóm kim được xoay sẵn tới góc hiện tại, rồi hoạt ảnh nhận `animation-delay` âm đúng số giây đã trôi — nên kim khớp giờ ngay giây đầu tiên, không bị "nhảy" khi ảnh mới được commit.
- Chấm ở tâm nhấp nháy (`pulse`), thanh tiến độ ngày chạy tới phần trăm đã trôi.

## Activity — 14 ngày

- Mỗi cột mọc từ đáy lên bằng SMIL `animate` trên `height` + `y`, độ trễ tăng 40ms mỗi ngày.
- Ngày không có contribution vẫn vẽ một vạch mờ để thấy nhịp nghỉ.
- Điểm sáng trên cột hôm nay nhấp nháy (`pulse`) — chỉ báo "số liệu đang tính tới hôm nay".

## Tắt hoạt ảnh

Mỗi file SVG có sẵn khối `@media (prefers-reduced-motion: reduce)` tắt toàn bộ hoạt ảnh CSS. Nếu bạn thấy chuyển động gây khó chịu:

1. Bật "giảm chuyển động" trong hệ điều hành (Windows: *Animation effects*; macOS: *Reduce motion*; Android/iOS: *Remove animations*).
2. Hoặc xem ảnh qua `https://github.com/.../raw/...svg` — nhiều trình xem tĩnh chỉ hiện khung đầu tiên, và mọi khung đầu tiên đều được vẽ đẹp sẵn.

> Mọi hoạt ảnh đều khai báo thời lượng cố định, không dùng `random` — hai lần tải trang luôn giống nhau, nên không có hiện tượng "nhấp nháy khác nhau" mỗi lần refresh.
