# Kiểm kê hoạt ảnh

Mỗi hình trong `assets/` đều có chuyển động riêng, tất cả đều viết bằng **CSS keyframes** hoặc **SMIL** ngay trong file SVG — không JavaScript, không thư viện, không request nào thêm.

| Hình | Hoạt ảnh chính |
| :-- | :-- |
| `hero.svg` | quỹ đạo xoay, sao nhấp nháy, bụi sáng bay lên, vòng lan toả, chip bồng bềnh, vệt sáng quét chữ, gõ chữ |
| `divider.svg` | tia sáng chạy dọc đường kẻ |
| `footer.svg` | hai lớp sóng trôi ngược chiều |
| `stats.svg` | vòng rank tự vẽ, số đếm lên, vệt sáng mép trên |
| `top-langs.svg` | thanh xếp chồng lớn dần, chú giải hiện lần lượt, chấm sáng ở đầu mỗi thanh |
| `live-clock.svg` | ba kim quay, chấm nhấp nháy, thanh tiến độ ngày |
| `activity.svg` | cột mọc lên, vòng thở + chấm sáng ở cột hôm nay |
| `status.svg` | viên thuốc hiện lần lượt, vệt sáng quét, vòng cung quay khi đang chạy |

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

- Vòng nền mờ + vòng tiến độ có `stroke-dasharray`/`stroke-dashoffset` chạy từ 0%
  tới đúng phần trăm còn cách hạng kế (B+ 279 điểm → 36% tới A). Con số này
  đổi mỗi lần số liệu đổi, không phải hằng số của hạng.
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

## Live clock — mặt trời và trăng khuyết

- Icon ở góc pill lời chào đổi theo giờ: mặt trời từ 06:00 tới 17:59, trăng
  khuyết từ 18:00. Không dùng emoji — emoji đổi hình theo hệ điều hành.
- Trăng được vẽ bằng **mask**: một hình tròn bị "cắn" bởi một hình tròn khác
  lệch sang phải. Hai lần thử trước đây dùng cung tròn (`a`) đều hỏng: cung
  có bán kính 0 ra một cục méo, và cung ghép từ hai đường `Q` trông như mũi
  tên ở mọi kích thước. Mask là cách duy nhất đọc ra hình trăng ở mọi trình
  vẽ, kể cả trình không hiểu CSS.

## Top languages — vệt sáng thứ hai

- Thanh xếp chồng đã có `sheen` 5.5 giây. Thêm một vệt mảnh 64px chạy chậm
  hơn (`barSweep`, 4.6 giây) với độ trễ 0.9 giây: hai vệt không bao giờ trùng
  nhau nên thanh không rơi vào nhịp đều đặn.
- Vệt được cắt bằng `clip-path="url(#barClip)"` — không cắt thì nó chạy ra
  ngoài thanh và trông như vết bẩn trên thẻ.

## Stats — icon nhích theo nhịp riêng

- Sáu icon trong sáu ô cùng dùng `bob` (lên xuống 1.6px trong 4.8 giây) nhưng
  lệch nhau 0.6 giây mỗi ô. Cùng nhịp thì cả thẻ rung; lệch nhịp thì thẻ thở.
- Biên độ chỉ 1.6px: đủ để mắt thấy ảnh sống, không đủ để mắt bỏ con số.

## Activity — 14 ngày

- Mỗi cột mọc từ đáy lên bằng SMIL `animate` trên `height` + `y`, độ trễ tăng 40ms mỗi ngày.
- Ngày không có contribution vẫn vẽ một vạch mờ để thấy nhịp nghỉ.
- Điểm sáng trên cột hôm nay nhấp nháy (`pulse`) — chỉ báo "số liệu đang tính tới hôm nay".

## Hero — bụi sáng và vòng lan toả

- **Bụi sáng**: 14 hạt, mỗi hạt là một `<circle class="dust">` với hai `<animate>`: `cy` chạy lên 18–40px, `opacity` chạy `0 → .7 → 0`. Chu kỳ 7–13 giây, `begin` âm để lệch pha ngay từ khung đầu.
- Vị trí hạt được sinh bằng `random.Random(77123)` — **cùng seed, cùng kết quả** mỗi lần vẽ, nên ảnh không "nhảy" giữa hai lần build.
- Hạt nào rơi vào vùng chữ (x 250–840, y 40–220) sẽ bị đẩy sang trái; có test khoá lại điều này.
- **Vòng lan toả**: hai vòng tròn quanh lõi "SP", bán kính `26 → 86`, `opacity .55 → 0`, chu kỳ 5.2 giây, lệch pha 2.6 giây — như nhịp thở.

## Stats — chấm sáng ở đầu cung

- Vòng tiến độ vẽ bằng `stroke-dasharray` = chu vi và `stroke-dashoffset` = phần còn thiếu, chạy 1.6s khi ảnh mới xuất hiện.
- Điểm sáng đặt tại toạ độ cực: `góc = -90° + 360° × phần_trăm`, `x = cx + r·cos(góc)`, `y = cy + r·sin(góc)`.
- Điểm sáng có `filter="url(#glow)"` và nhịp `pulse`; quanh nó là một vòng `pulseSlow` mờ.
- Cố ý **không** dùng hiệu ứng mờ dần: khung đầu tiên phải đã có điểm sáng, nếu không trình xem tĩnh sẽ không thấy gì.

## Activity — đường trung bình và nhãn cao nhất

- **Đường trung bình**: nét đứt `4 6`, `opacity .38`, vẽ từ x=22 tới x=618 tại `y = đáy − (trung_bình / cao_nhất) × chiều_cao`.
- Chỉ hiện khi `0 < trung_bình < cao_nhất`. Mọi ngày bằng nhau thì đường này vô nghĩa nên ẩn.
- Nhãn `TB 196` nằm ở đầu trái, phía trên đường.
- **Nhãn cao nhất**: đặt trên đỉnh cột cao nhất, chữ nhỏ màu nhấn. Nếu hôm nay chính là ngày cao nhất thì bỏ nhãn — chỗ đó đã có chấm nhấp nháy của "hôm nay".

## Live clock — vành và kim

- Ba kim quay bằng CSS với chu kỳ thật: 60s, 3600s, 43200s. Góc ban đầu ghi vào `transform` tĩnh, `animation-delay` âm bằng đúng số giây đã trôi → khớp giờ ngay khung đầu.
- **Vành**: một cung gradient `stroke-dasharray="70 320"` quay 18 giây/vòng trên vành ngoài, cùng vòng nét đứt quay 40 giây ở ngoài xa hơn — hai tốc độ khác nhau nên mắt không thấy "đều đều".
- **Kim giây** có đối trọng: một chấm nhỏ phía sau trục, giống đồng hồ cơ thật.

## Divider — hai tia sáng

- Tia chính: dải gradient trắng, rộng 120, chạy `-120 → 1020` trong 7 giây, có `filter` làm mờ viền.
- Tia phụ: rộng 60, chạy ngược `1020 → -120` trong 13 giây, `opacity .45` — tạo chiều sâu, không tranh mắt với tia chính.
- Viên kim cương ở giữa tự xoay 45° → 225° → 45° trong 12 giây, quanh nó là vòng tròn giãn ra rồi biến mất.

## Footer — bong bóng

- Sáu bong bóng, `cy` chạy từ đáy lên ~90px trong 11 giây, `opacity 0 → .55 → 0`.
- Mỗi bong bóng lệch pha (0, −1.6, −3.1, −0.8, −2.4, −4.2 giây) nên nhìn như nước đang lăn tăn chứ không phải "đồng loạt bật lên".
- Toàn bộ nằm trong `clip-path="url(#cardBody)"`.

## Top languages — khoanh sáng ngôn ngữ đầu

- Chấm màu của ngôn ngữ đứng đầu có thêm vòng `r="9"` với `stroke-opacity=".35"` và nhịp `pulseSlow` (4.4s).
- Các ngôn ngữ còn lại chỉ có chấm `r="5"` — mắt tự biết đâu là ngôn ngữ chính mà không cần thêm chữ "top 1".

## Bảng chu kỳ (để dễ chỉnh)

| Hiệu ứng | Chu kỳ | Kiểu |
| :-- | :-- | :-- |
| `pulse` | 2.6s | CSS |
| `pulseSlow` | 4.4s | CSS |
| `blink` (con trỏ gõ chữ) | 1.05s | CSS steps |
| `twinkle` (sao) | 4s | CSS |
| `floatY` (chip) | 5.2s | CSS |
| `sheen` (vệt sáng) | 6.5s | CSS |
| `scan` (dải quét) | 7.5s · 12.5s (hero, hai làn) · 9s (thẻ số liệu) | CSS |
| `spinDot` (vòng cung "đang chạy") | 1.6s | CSS |
| `dashFlow` (nét đứt tự chạy) | 2.6s | CSS |
| `wave` / `wave2` | 14s / 19s | CSS |
| `barSweep` (vệt sáng trong thanh xếp chồng) | 4.6s | CSS |
| `bob` (icon nhích 1.6px) | 4.8s | CSS |
| kim giây / phút / giờ | 60s / 3600s / 43200s | CSS |
| vành đồng hồ | 18s | CSS |
| bụi sáng hero | 7–13s | SMIL |
| vòng lan toả | 5.2s | SMIL |
| tia sáng divider | 7s / 13s | SMIL |
| bong bóng footer | 11s | SMIL |
| sao nhấp nháy ở footer | 4s (lệch pha 0 – 4.2s) | CSS |
| hạt sáng bay quanh vành rank | 22s | SMIL rotate |
| đèn chạy trên 12 vạch giờ | 6s (mỗi vạch lệch 0.5s) | SMIL opacity |
| `slotMin` (ô số phút) | 3600s | CSS |
| `slotHour` (ô số giờ) | 86400s | CSS |
| chấm đầu vòng cung ngày | 3.2s | SMIL `r` |
| hạt sáng chạy dọc divider | 9s | SMIL |
| thanh ngôn ngữ "thở" | 5s / 6s, lệch 0.35s | SMIL opacity |

Đổi số ở đây là đổi nhịp của cả trang — không cần sửa từng ảnh.

## Tất định: cùng đầu vào, cùng đầu ra

Không có `random` nào không seed. `_stars()` dùng `Random(20260820)`, `_particles()` dùng `Random(77123)`, dữ liệu demo dùng `Random(7)`.

Vì vậy:

- Hai lần build liên tiếp cho ra file **giống hệt nhau** (trừ phần thời gian) — `git diff` sạch nghĩa là thật sự không có gì đổi.
- `--smart` so vân tay dữ liệu là đủ tin cậy, không bị "nhiễu" do vị trí sao đổi mỗi lần.
- Test có thể khẳng định chính xác toạ độ, số lượng, chu kỳ.


## Dải trạng thái — `status.svg`

Dải này kể chuyện bằng **màu và chuyển động cùng lúc**, nên nhìn không cần
đọc vẫn biết workflow nào đang có vấn đề.

- **Viên thuốc hiện lần lượt**: mỗi viên `fadeUp` trễ 60ms so với viên trước
  (`animation-delay` 0.00s, 0.06s, 0.12s…). Bảy viên mất 0.42s để vào chỗ.
- **Vệt sáng quét** (`sheen`, 9 giây/vòng) chạy ngang cả dải — cùng một
  chuyển động với các thẻ khác nên cả trang có nhịp thống nhất.
- **ĐẠT**: chấm xanh có vòng `pulseSlow` 4.4 giây — nhịp thở chậm, không
  gây mỏi mắt khi có nhiều viên xanh cùng lúc.
- **ĐANG CHẠY**: vòng cung khuyết `spinDot` quay 1.6 giây/vòng quanh chấm
  hổ phách. `transform-box: fill-box` để vòng cung quay quanh tâm của chính
  nó, không phải tâm cả ảnh.
- **LỖI**: chấm đỏ đứng yên, không nhấp nháy. Lỗi cần được nhìn thấy ngay,
  không cần thu hút thêm.
- **Chờ merge / chưa chạy**: xám và xanh dương, không có vòng — trạng thái
  "chưa có gì để nói" thì cũng không nên động đậy.
- **Chân dải**: chấm `pulse` cạnh dấu thời gian, cùng kiểu với chân các thẻ
  khác, để mắt biết dải này vừa được vẽ lại.
- **Nhãn tuổi quá một ngày**: chữ "25 ngày trước" đổi từ xám sang hổ phách.
  Màu hổ phách trong dải vốn đã mang nghĩa "cần để ý", nên mắt dừng lại đúng
  chỗ một dấu ĐẠT xanh đã cũ không còn nói gì về hôm nay.

Tất cả các lớp trên đều nằm trong danh sách tắt của `prefers-reduced-motion`,
nên ai bật "giảm chuyển động" sẽ thấy một dải tĩnh nhưng vẫn đủ màu và chữ.

## Mọi thẻ — vệt sáng mép trên

- Mỗi thẻ (kể cả `live-clock`, `status`) có một vệt 130px chạy dọc mép trên,
  dùng lại keyframe `sheen` nên cùng nhịp với vệt sáng quét trong thân thẻ.
- Chu kỳ 8–12 giây, **lệch nhau theo bề rộng thẻ** (`8 + width % 5`), nên
  hai thẻ cạnh nhau không bao giờ chớp cùng lúc.
- Vệt nằm trong `<g clip-path="url(#cardBody)">` — không tràn qua góc bo, và
  tự tắt theo `prefers-reduced-motion` vì nó là `sheen`.

## Top languages — chấm sáng ở đầu thanh

- Mỗi thanh tiến độ 3px có một chấm `r=2.4` đặt đúng tại điểm dừng
  (`x = lề + bề dài thanh`), nhấp nháy `pulse` với độ trễ lệch 0.2 giây.
- Thanh tĩnh trả lời "bao nhiêu phần trăm"; chấm sáng trả lời "thanh này
  vừa được vẽ lại" và cho mắt một điểm bám khi quét nhanh cả cột.

## Live clock — số phút tự nhảy, không cần JavaScript

- Con số giờ và phút là **84 ô chồng lên nhau**: 24 ô giờ + 60 ô phút, mỗi ô
  chỉ hiện trong đúng khoảng thời gian của nó. Không có script nào chạy —
  trình duyệt tự đổi số theo phút, kể cả khi không có mạng.
- Ô của ảnh chụp được vẽ sẵn `opacity: 1`, nên trình xem tĩnh thấy đúng giờ
  của lần vẽ cuối; các ô còn lại ẩn cho tới lượt mình.
- Chu kỳ: ô phút `slotMin 3600s`, ô giờ `slotHour 86400s` (dùng
  `animation-duration` riêng vì `animation` viết tắt của ô phút sẽ ghi đè).
- Độ trễ âm đúng số giây đã trôi trong phút/giờ hiện tại, nên số đổi đúng
  giây thứ 0 chứ không lệch theo lúc tải trang.
- Workflow chỉ cần vẽ lại mỗi 5 phút (hạn mức cron của GitHub) để phần
  *ngày tháng* và *vòng cung* khớp lại; phần phút thì CSS tự lo.

## Live clock — vòng cung tiến độ ngày

- Vòng cung ngoài cùng (`r = bán kính + 21`) đi đúng một vòng mỗi 24 giờ:
  06:00 là một phần tư, 12:00 là nửa vòng ở đáy, 18:00 là ba phần tư.
- Chấm ở đầu cung có SMIL `animate` trên `r` (2,6 → 4,4 → 2,6, 3,2 giây) để
  mắt bắt được chỗ đang tiến, không phải một đầu cung chết.
- Ngay sau nửa đêm, cung chỉ dài vài phần nghìn độ — vẽ ra chỉ thành một
  chấm méo ở đỉnh, nên dưới 0,4° thì bỏ hẳn phần cung.

## Activity — vòng thở quanh cột hôm nay

- Sau lưng chấm sáng có thêm vòng `stroke` bán kính 11, `pulseSlow`
  4.4 giây. Cột hôm nay vì thế vẫn nổi bật kể cả khi nó thấp bằng cột bên
  cạnh — trước đây chỉ một chấm 3.4px là không đủ.

## Tắt hoạt ảnh

Mỗi file SVG có sẵn khối `@media (prefers-reduced-motion: reduce)` tắt toàn bộ hoạt ảnh CSS. Nếu bạn thấy chuyển động gây khó chịu:

1. Bật "giảm chuyển động" trong hệ điều hành (Windows: *Animation effects*; macOS: *Reduce motion*; Android/iOS: *Remove animations*).
2. Hoặc xem ảnh qua `https://github.com/.../raw/...svg` — nhiều trình xem tĩnh chỉ hiện khung đầu tiên, và mọi khung đầu tiên đều được vẽ đẹp sẵn.

### SMIL không tắt bằng CSS

`<animate>` của SMIL không bị `animation: none` ảnh hưởng. Vì vậy mọi phần tử
mang SMIL (vệt sáng của đường kẻ, bong bóng chân trang) đều có thêm
`class="smilOnly"`, và file có một thẻ `<style>` riêng:

```
@media (prefers-reduced-motion: reduce) { .smilOnly { display: none } }
```

Chỉ phần **trang trí** bị ẩn. Đường kẻ tĩnh, viên kim cương ở giữa, tiêu đề và
chữ chân trang vẫn hiện đủ — người bật "giảm chuyển động" thấy một ảnh tĩnh
nhưng đầy đủ thông tin, không phải một khung hình trống.

> Mọi hoạt ảnh đều khai báo thời lượng cố định, không dùng `random` — hai lần tải trang luôn giống nhau, nên không có hiện tượng "nhấp nháy khác nhau" mỗi lần refresh.
