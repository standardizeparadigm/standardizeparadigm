# 📝 Nhật ký thay đổi

Những thay đổi đáng kể của trang cá nhân này, mới nhất ở trên cùng.
Mỗi mục ghi lại *vì sao* thay đổi, không chỉ *cái gì* đã đổi.

## 2026-11-19 — Nhãn tuổi đổi màu, và `--check` bắt ảnh phình

- Dải trạng thái: tuổi quá một ngày chuyển sang hổ phách, để một dấu ĐẠT từ
  25 ngày trước không trông y hệt lượt chạy sáng nay.
- `generate_cards.py --check` in tổng dung lượng và trả mã 1 nếu có ảnh vượt
  40 KB — trước đây một file 120 KB vẫn được báo là "hợp lệ".
- `README_BUDGET` đếm dòng bằng `splitlines`, nên README đúng 360 dòng không
  còn bị báo là 361.

## 2026-11-19 — Bốn luật mới bắt những lỗi không ai báo

- **`id` trùng trong một ảnh**: `url(#halo)` chỉ trỏ tới phần tử đầu tiên,
  bản sao thứ hai lặng lẽ mất hiệu ứng.
- **Lớp CSS không tồn tại**: `class="pulse-typo"` không làm ảnh hỏng, chỉ
  đứng im — và mắt người không phân biệt được với "ảnh tĩnh".
- **`url(#x)` trỏ hụt**: `filter="url(#gloww)"` khiến trình duyệt bỏ qua
  thuộc tính và vẽ nét sắc thay vì nét phát sáng.
- **Keyframe lẻ**: khai báo mà không dùng là byte chết; dùng mà không khai
  báo là hoạt ảnh câm.
- **Số không hợp lệ**: `d="MNaN 12"` là XML hợp lệ, trình duyệt bỏ cả phần
  tử, ảnh chỉ mất một nét.

## 2026-11-19 — Mỗi workflow một phút riêng

`:13` cho thẻ số liệu, `:23` cho README, `:07`/`:37` cho biểu đồ 3D — không
job nào chạm phút của job khác nên không phải rebase rồi đẩy lại. `check_repo.py`
cảnh báo nếu sau này có lịch mới rơi vào phút đã có người giữ.

## 2026-11-19 — Chữ trong ảnh hiện đúng ở mọi trình vẽ, không chỉ trình duyệt

- CSS trong ảnh dùng `font: 800 54px Arial` — cú pháp hợp lệ, trình duyệt hiểu
  đủ. Nhưng resvg, một số bản librsvg và trình xem ảnh desktop **bỏ qua cả
  khai báo**, nên chữ rơi về 16px: số giờ teo lại, nhãn tuổi trên dải trạng
  thái chèn lên nhãn trạng thái.
- Đổi toàn bộ 28 chỗ sang `font-weight` / `font-size` / `font-family`. Ảnh
  giống nhau ở mọi nơi đọc nó, không chỉ trong Chrome.
- Luật mới: cấm `font:` viết tắt trong `assets/*.svg`, để không ai vô tình
  quay lại cú pháp chỉ-một-trình-duyệt-hiểu.

## 2026-11-19 — Sửa: trăng khuyết vẽ bằng cung tròn bán kính 0

- Icon ban đêm dùng `a4.6 4.6 0 106.4 6.4 5.6 5.6 0 01-0 -0`: bán kính truyền
  vào là hằng số 0, nên mọi trình vẽ đều ra một cục méo ở cạnh pill lời chào.
- Giờ là một hình tròn bị "cắn" bởi hình tròn khác, cắt bằng `mask` — đúng ở
  mọi bộ dựng, kể cả trình xem không hiểu CSS.
- Lỗi này chỉ hiện sau 18h, nên ban ngày nó nằm im. Tám test mới khoá cả hai
  nhánh mặt trời / trăng.

## 2026-11-19 — Sửa: `main()` không dọn lỗi của lượt trước

- `check_repo.py` giữ danh sách lỗi ở cấp module. Gọi `main()` hai lần trong
  một tiến trình (điều mà test làm liên tục) thì lỗi của lượt trước còn nằm
  đó và lượt sau báo đỏ vô cớ.
- Trên CI không ai thấy, vì mỗi lượt chạy là một tiến trình mới. Chỉ test
  phát hiện — và đúng là test phát hiện thật, ngay khi thêm ca "cây sạch thì
  mã thoát bằng 0".

## 2026-11-19 — Luật thứ hai mươi: bảng Markdown thẳng cột

- Một dòng thiếu dấu `|` làm cả bảng lệch: ô cuối trôi sang cột khác và trên
  GitHub trông như bảng bị gãy. Markdown không coi đó là lỗi cú pháp.
- Cùng đợt: tài liệu phải mở bằng tiêu đề `#` (GitHub lấy dòng đầu làm mô tả
  khi chia sẻ link), và ảnh không được gọi URL ngoài hay mang `<script>`.

## 2026-11-19 — Sửa: README ghi nhầm lịch của đồng hồ

- Bảng workflow trong README ghi dòng Live Clock chạy `*/30` "mỗi 30 phút".
  Nó chạy `*/5`. Con số đó là bản sao của dòng biểu đồ 3D nằm ngay dưới.
- Trong cùng ô, phần mô tả lại viết đúng "vẽ lại mỗi 5 phút" — nên chỉ người
  đối chiếu hai chỗ mới thấy. Đây là loại lỗi không công cụ nào bắt: cả hai
  câu đều là văn xuôi tiếng Việt.
- Sửa luôn câu chân trang dưới ảnh: nói thêm **số phút tự nhảy**, không chỉ
  tay kim quay.

## 2026-11-19 — Sửa: dải trạng thái tiếng Anh vẫn hiện 'CHỜ MERGE'

- Bảng `en` có hai giá trị chép nguyên tiếng Việt: `status.foot` và
  `status.missing`. Người chọn tiếng Anh thấy giữa dải trạng thái một nhãn
  tiếng Việt in hoa.
- Không test nào bắt, vì hai bảng chỉ được so **tập khoá**, không so ngôn ngữ
  của giá trị. Bộ test mới kiểm cả nội dung: chữ cái tiếng Việt trong bảng
  `en`, khoảng trắng thừa, dấu rời NFD (hiện thành ô vuông ở vài font).

## 2026-11-19 — Thêm bảy luật tự kiểm

- `check_repo.py` có thêm: địa danh cũ, dấu `TODO`/`FIXME`, `workflow_dispatch`,
  badge workflow của shields, nhịp cron dày hơn 5 phút, action không ghim
  phiên bản, job thiếu `timeout-minutes`, tiêu đề Markdown nhảy cấp, chữ SVG
  thiếu `class`, `id` trùng trong một file.
- Mỗi luật ra đời từ một lỗi đã xảy ra thật và đều thuộc loại trình duyệt vẫn
  vẽ, GitHub vẫn hiện — chỉ người đọc mới chịu.
- `docs/TESTING.md` có bảng "Những luật chỉ máy thấy" ghi lại lỗi gốc, để lần
  sau không ai xoá luật vì "có vẻ thừa".

## 2026-11-19 — Đồng hồ tự đếm phút, không cần JavaScript

- Con số giờ:phút trước đây là một chuỗi tĩnh, chỉ đổi khi workflow chạy lại
  (5 phút một lần, và GitHub hay trễ thêm). Kim quay mà số đứng yên trông
  như ảnh hỏng.
- Cách làm: 24 ô giờ + 60 ô phút chồng đúng một chỗ, mỗi ô có `animation-delay`
  âm bằng quãng thời gian từ bây giờ tới lượt nó. Trình duyệt tự đổi số mỗi
  phút, kể cả khi mất mạng. Không script, không cron phút.
- Ô của ảnh chụp vẫn `opacity: 1` mặc định nên trình xem tĩnh thấy đúng giờ
  của lần vẽ cuối; `prefers-reduced-motion` đóng băng cả 84 ô.

## 2026-11-19 — Vòng cung tiến độ ngày trên mặt đồng hồ

- Kim nói "mấy giờ", nhưng không nói "ngày còn dài hay đã gần hết". Thêm
  vòng cung ngoài cùng chạy đúng một vòng mỗi 24 giờ, chấm ở đầu cung thở
  nhẹ để thấy chỗ đang tiến.
- 06:00 là đúng một phần tư vòng, 18:00 là ba phần tư — kiểm bằng toạ độ
  tuyệt đối trong test, không phải bằng mắt.
- Dưới 0,4° (vài phút sau nửa đêm) thì không vẽ cung: một cung dài vài phần
  nghìn độ chỉ thành chấm méo ở đỉnh.

## 2026-11-19 — Sửa: chân thẻ đồng hồ bị cắt mất chữ

- Chuỗi tiếng Việt "Kim và số phút tự chạy bằng CSS giữa hai lần cập nhật ·
  workflow vẽ lại mỗi 5 phút" dài 78 ký tự, chạy quá khổ 640px và bị cắt
  thành "mỗi 5 p…". Chữ SVG không tự xuống dòng nên không có gì báo lỗi.
- Rút gọn cả hai ngôn ngữ còn dưới 56 ký tự, và thêm test khoá ngưỡng đó —
  chân thẻ 9px chỉ chứa được khoảng 55 ký tự.

## 2026-11-19 — Hero cũng tôn trọng "giảm chuyển động"

- 14 hạt bụi (mỗi hạt hai `<animate>`), hai vòng lan toả quanh lõi và vệt
  sáng quét chữ đều là SMIL — CSS không tắt được, nên người bật giảm chuyển
  động vẫn thấy hero động đùng đùng trong khi mọi thứ khác đứng yên.
- Cách sửa: class `smilOnly` + một thẻ `<style>` ẩn chúng. Hạt bụi và vòng
  lan toả là trang trí thuần; tiêu đề, chip, sóng nền vẫn đủ.
- Test cũ cấm mọi dấu `@` trong thân SVG để bắt token palette chưa thay —
  giờ kiểm đúng tên token, vì `@media` là dấu `@` hợp lệ.

## 2026-11-19 — Luật thứ mười ba: dấu merge còn sót

- Vừa merge `main` vào nhánh PR (bot trên main ghi lại `stats.svg` và
  `top-langs.svg` mỗi 3 giờ), xung đột đúng ở hai file ảnh đó.
- Giữ bản của nhánh rồi vẽ lại từ API ngay sau khi merge, để số liệu là mới
  nhất chứ không phải bản của bot lúc 13h.
- Luật mới bắt `<<<<<<<` / `=======` / `>>>>>>>` trong mọi file văn bản: một
  dấu sót lại làm Python `SyntaxError` và SVG hỏng XML, nhưng chỉ khi có ai
  mở đúng file đó.

## 2026-11-19 — Chân dải trạng thái có con số tổng kết

- Thêm `4/7 workflow ổn` ở góc phải chân dải: đọc được tình hình chung mà
  không phải đếm màu trên bảy viên thuốc.
- "Đang chạy" được tính là ổn (nó không phải vấn đề); lỗi và chờ merge mới
  là vấn đề. Bốn test khoá cách đếm này.

## 2026-11-19 — Hoạt ảnh SMIL và "giảm chuyển động"

- `prefers-reduced-motion` chỉ tắt được hoạt ảnh CSS. `<animate>` của SMIL
  vẫn chạy, nên vệt sáng của đường kẻ và bong bóng chân trang vẫn động với
  người đã bật "giảm chuyển động".
- Cách sửa: đánh dấu mọi phần tử mang SMIL bằng `class="smilOnly"` và thêm
  thẻ `<style>` ẩn chúng theo media query. Chỉ ẩn phần trang trí — đường kẻ
  tĩnh, viên kim cương, tiêu đề vẫn hiện đủ.
- Lỗi này được phát hiện bởi `test_repo_assets.py` — module kiểm **ảnh đã
  commit**, không phải hàm vẽ. Một ảnh có thể sinh từ phiên bản cũ và không
  ai vẽ lại.

## 2026-11-19 — svgkit 2.2.0

- Vòng này thêm ba thứ làm thay đổi API công khai, nên nâng phiên bản nhỏ:
  `api.to_vn()` / `api.age_minutes()`, khoá i18n `clock.updated` +
  `clock.left`, và `status_strip()` nhận hàng ba phần tử có nhãn tuổi.
- Không có thay đổi phá vỡ: mọi lời gọi cũ với hàng hai phần tử vẫn chạy
  đúng — điều này được khoá bằng test, không phải bằng lời hứa.

## 2026-11-19 — README có ngân sách dòng

- Trang cá nhân là thứ người lạ mở 20 giây rồi đóng. README hiện 338 dòng;
  luật mới chặn ở 360 và nhắc chuyển bớt nội dung vào `docs/`.
- Đây là yêu cầu trực tiếp ("đừng làm quá dài") được biến thành thứ máy
  kiểm được, thay vì một lời hứa dễ quên.

## 2026-11-19 — Gõ sai `--theme` / `--lang` thì được nhắc

- Trước đây `--lang xx` hay `--theme nokey` im lặng rơi về mặc định: người
  dùng tưởng đã đổi mà ảnh vẫn như cũ, và không có dấu hiệu nào để biết.
- Giờ có cảnh báo kèm gợi ý gần đúng (`difflib`): `--theme skky` → "dùng
  'sky' (ý bạn là 'sky'?)". Vẫn rơi về mặc định để lượt chạy không hỏng.

## 2026-11-19 — Bốn luật mới cho repo tự canh mình

- **Tài liệu mồ côi**: bài trong `docs/` mà không bài nào dẫn tới thì người
  mới sẽ không bao giờ đọc. README và CHANGELOG được miễn.
- **Ngân sách ảnh**: `assets/*.svg` phải dưới 40 KB. Ảnh được tải mọi lần mở
  trang; vượt ngưỡng đó thường là dấu hiệu nhúng dữ liệu lớn vào file.
  `profile-3d-contrib/` nằm ngoài phạm vi — action khác sinh ra.
- **Docstring đầu file**: thứ duy nhất nói *vì sao* module tồn tại.
- Cùng với luật "hơn N unit test" ở trên, cả bốn đều được test bằng fixture
  tạm trong `test_check_repo.py` và chạy lại trên repo thật trong
  `test_repo_workflows.py`.

## 2026-11-19 — `check_repo.py --fix` và luật "số test trong tài liệu"

- `--fix` chuẩn hoá BOM/CRLF/khoảng trắng/dòng trống cuối file. Chỉ đụng
  thứ vô hình với người đọc: có test khoá lại rằng chữ tiếng Việt, dấu em
  dash và dấu giữa (`·`) đi qua nguyên vẹn, và chạy hai lần thì lần hai
  không sửa gì (nếu không, workflow sẽ tự push một commit mỗi 5 phút).
- Generator SVG giờ ghi newline cuối file, nên `--fix` không còn gì để sửa
  trên ảnh vừa vẽ — hết vòng lặp giữa hai công cụ.
- Luật mới: câu `hơn N unit test` phải còn đúng (`N <= số thật < N + 100`).
  Bốn file từng ghi `hơn 100` trong khi bộ test đã hơn 320.

## 2026-11-19 — Nhãn "còn 7g37" trong thẻ đồng hồ

- Thanh tiến độ ngày chỉ nói *đã trôi bao nhiêu*; lúc 23h cái người ta cần
  biết là *còn bao lâu*. Nhãn `còn 7g37` nằm ngay cạnh phần trăm.
- Khoá i18n `clock.left` ở cả hai ngôn ngữ; phút luôn hai chữ số để nhãn
  không nhảy bề rộng giữa 23:55 (`còn 1g05`) và 23:05 (`còn 1g55`).

## 2026-11-19 — Lịch chạy so le để không giành `git push`

- Sáu workflow cùng ghi vào một nhánh. `*/5` (đồng hồ) và `*/10` (trạng thái)
  trùng nhau ở phút 0, 10, 20… — hai lượt chạy có thể push cùng lúc.
- `status.yml` chuyển sang `2-59/10` (phút 2, 12, 22, 32, 42, 52): lệch 2
  phút, đủ để đồng hồ (~40 giây/lượt) chạy xong trước.
- `docs/WORKFLOWS.md` có thêm bảng "Ai push lúc nào" và ba lớp bảo hiểm:
  `concurrency` riêng từng workflow, `git pull --rebase` trước khi push, và
  dải trạng thái là thứ chịu thiệt sau cùng nếu có lượt trượt.

## 2026-11-19 — Hai luật tài liệu, và một luật ảnh

- `check_workflow_docs()` bắt cả hai chiều: bảng ghi sai cron, **và**
  workflow mới không có dòng nào trong bảng.
- `check_dead_assets()`: ảnh trong `assets/` mà không được nhúng ở đâu là ảnh
  chết — vẫn được vẽ lại mỗi ngày, vẫn nằm trong lịch sử git, không ai thấy.
- `check_svg()` đòi `<title>`, trừ ảnh tự khai `role="presentation"` /
  `aria-hidden="true"`. Đường kẻ trang trí phải nói rõ "đừng đọc tôi".
- `test_docs.py` kiểm hình thức Markdown (một H1, không nhảy cấp, dòng trống
  trước tiêu đề) và đếm lại tổng số test so với `docs/TESTING.md`.

## 2026-11-19 — Nhãn tuổi trên dải trạng thái

- Dải trạng thái cũ 6 tiếng trông y hệt dải vừa vẽ — đúng loại lỗi khiến
  người xem tưởng workflow đứng. Giờ mỗi viên thuốc có nhãn "9 giờ trước" ở
  góc phải, lấy từ `updated_at` của lần chạy gần nhất.
- `human_age()` gộp ba mốc: phút (<1 giờ), giờ (<1 ngày), ngày. "3 ngày
  trước" đúng bản chất hơn "71 giờ trước".
- `api.age_minutes()` trả `None` khi không đọc được mốc — thà thiếu nhãn còn
  hơn nói dối "0 phút trước".

## 2026-11-19 — Hiệu ứng mới, vẫn tắt được bằng một dòng CSS

- Vệt sáng chạy dọc mép trên mọi thẻ (130px, 8-12 giây, lệch nhịp theo bề
  rộng) — nằm trong clip-path nên không tràn qua góc bo.
- Chấm sáng nhấp nháy ở đầu mỗi thanh tiến độ ngôn ngữ: thanh không còn là
  vạch tĩnh, mắt bám được điểm dừng.
- Cột hôm nay trong thẻ hoạt động có thêm vòng thở `r=11` phía sau chấm sáng.
- Tất cả dùng lại keyframe sẵn có (`sheen`, `pulse`, `pulseSlow`) nên
  `prefers-reduced-motion` tắt sạch, không phải thêm ngoại lệ.

## 2026-11-19 — Bốn quy ước an toàn cho workflow

- `check_workflow_hygiene()` bắt bốn thứ mà thiếu là sinh sự cố khó lần:
  - không có `permissions:` → mặc định rộng hoặc thiếu quyền ở bước push;
  - có lịch chạy mà không có `concurrency:` → hai lượt chồng nhau cùng push;
  - mỗi job phải có `timeout-minutes` → mặc định của GitHub là **6 tiếng**;
  - có `git push` mà không có cổng `github.actor != 'github-actions[bot]'`
    → workflow tự kích hoạt chính nó, vòng lặp vô hạn.
- Cùng luật đó chạy lại trên repo thật trong `test_repo_workflows.py`, nên
  sai quy ước là đỏ ngay trên máy chứ không phải đợi CI.

## 2026-11-19 — Tài liệu phải khớp lịch chạy thật

- Trong một vòng đã có hai lần bảng lịch chạy trong `docs/WORKFLOWS.md` và
  `README.md` nói một đằng, YAML nói một nẻo. Người đọc tin bảng, không ai
  đọc cron.
- `check_repo.check_workflow_docs()` đọc cron thật từ `.github/workflows/*`,
  rồi so từng dòng bảng có nhắc tên workflow và từng `<code>cron</code>`
  trong README. Chạy ngay lần đầu đã bắt được `*/15` còn sót.

## 2026-11-19 — Mọi thẻ đều quy về giờ Việt Nam

- Thẻ số liệu, ngôn ngữ, hoạt động và dải trạng thái cũng in mốc thời gian;
  nếu chỉ sửa đồng hồ thì bốn thẻ còn lại vẫn lệch 7 tiếng trên máy chủ CI.
- `to_vn()` được gọi ở **đầu mỗi hàm vẽ thẻ**, không phải ở chỗ gọi: hàm vẽ
  tự chịu trách nhiệm về giờ của chính nó, không tin người gọi.
- Test riêng cho từng thẻ: đầu vào 09:00 UTC phải ra chuỗi 16:00.

## 2026-11-19 — Đồng hồ sai giờ: hai lỗi chồng lên nhau

- Ảnh đồng hồ cũ hiển thị **giờ UTC** dưới nhãn "giờ Việt Nam": renderer
  không hề quy đổi múi giờ, cứ thế vẽ nguyên `datetime` nhận được.
- Và ảnh trong repo đã nguội 25 phút, nên dù giờ đúng thì nhìn vẫn "lệch".
  Sửa một trong hai lỗi thì vẫn thấy sai — nên phải sửa cả hai.
- `api.to_vn()`: `None` → `None`, giờ không kèm múi (naive) coi như đã là giờ
  Việt Nam, giờ có múi thì `astimezone(TZ_VN)`.
- Thêm dòng `cập nhật HH:MM` ngay trong thẻ và ghi chú dưới đáy: kim tự quay
  bằng CSS giữa hai lần vẽ lại, nên đọc thẻ là biết ảnh chụp lúc nào.

## 2026-11-19 — Dải trạng thái workflow thay cho badge shields.io

- Ba badge trong ảnh chụp bị hỏng: `live-clock` và `health` trả *repo or
  workflow not found* (file chỉ có ở nhánh phụ), `welcome` trả *no status*
  (có workflow nhưng chưa chạy xong lần nào).
- `assets/status.svg` do chính repo vẽ từ Actions API: 7 viên thuốc, mỗi
  viên một workflow, màu theo lần chạy gần nhất. Không phụ thuộc server ngoài
  nên không có khái niệm "not found".

## 2026-11-19 — Năm trạng thái, không phải ba

- `passing` / `failing` / `running` / `none` / `unknown` ban đầu chỉ đủ cho
  badge. Khi đọc API thật mới thấy cần thêm `missing` (404 = workflow chưa
  nằm trên nhánh mặc định) — đúng lý do khiến shields báo đỏ.
- Màu cố định theo nghĩa (xanh/đỏ/hổ phách/xám/xanh dương) chứ không theo
  theme: "đỏ = lỗi" phải đúng ở cả 6 bảng màu.

## 2026-11-19 — Nhịp chạy: giãn chỗ thừa, giữ chỗ cần

- 3D: `*/5` → `*/30` (ảnh chỉ đổi khi có push hoặc sang ngày; push đã có
  trigger riêng nên lịch 5 phút chỉ tạo 288 lượt chạy rỗng/ngày).
- Thẻ số liệu: `*/10` → `15 */3 * * *` (star/fork/ngôn ngữ đổi vài ngày/lần).
- README Garden dời sang phút 45 để hai workflow không giành `git push`.
- Đồng hồ giữ `*/5` — đây là sàn của GitHub và cũng là thứ duy nhất thật sự
  cần tươi theo phút.

## 2026-11-19 — Workflow tự vẽ dải trạng thái

- `status.yml`: cron 15 phút **và** `workflow_run` — có workflow vừa xong là
  dải cập nhật ngay, không phải đợi lượt kế tiếp.
- Quyền `contents: write` + `actions: read`; kiểm tra XML trước khi commit;
  không đọc được API thì giữ ảnh cũ chứ không ghi thẻ rỗng.

## 2026-11-19 — Vệ sinh file trong check_repo

- Bốn loại lỗi vô hình: BOM UTF-8, xuống dòng CRLF, ký tự điều khiển dưới
  U+0020, và file không phải UTF-8 hợp lệ. Đều là mầm của "hỏng kí tự".
- Khoảng trắng thừa cuối dòng chỉ là cảnh báo để không chặn CI.
- Bỏ qua `.git`, `node_modules`, `.venv`, `__pycache__` và file nhị phân.

## 2026-11-19 — Hai lớp test bị che khuất

- `test_cli.py` có ba lớp cùng tên `TestInfoFlags`/`TestCheckFlag`;
  `test_cards.py` và `test_primitives.py` mỗi file hai lớp trùng tên. Python
  chỉ giữ lớp cuối, nên các bản trước **không bao giờ chạy**.
- Đã xoá hai bản sao trong `test_cli.py`, đổi tên hai lớp còn lại. Số test
  tăng từ 211 lên 214 dù không viết thêm test nào — đó là phần bị che.

## 2026-11-19 — Dải trạng thái: hoạt ảnh theo nghĩa

- ĐẠT: nhịp thở chậm 4.4s · ĐANG CHẠY: vòng cung khuyết quay 1.6s/vòng ·
  LỖI: đứng yên (lỗi cần thấy ngay, không cần thu hút) · chưa chạy: không vòng.
- Viên thuốc hiện lần lượt cách nhau 60ms, vệt sáng quét ngang cả dải.

## 2026-11-19 — Thêm hoạt ảnh ở bốn ảnh cũ

- `stats.svg`: hạt sáng bay quanh vành rank (22s/vòng) + vệt quét dọc thẻ.
- `top-langs.svg`: mỗi đoạn thanh "thở" nhịp riêng (fill-opacity 1→.82→1).
- `activity.svg`: đường trung bình chạy nét đứt (`dashFlow`).
- `divider.svg`: hạt sáng chạy dọc đường kẻ + hai chấm thở ngược pha.
- `footer.svg`: năm ngôi sao nhấp nháy ở nửa trên.
- `hero.svg`: làn quét thứ hai, 12.5s, lệch pha 4.2s.
- `live-clock.svg`: 12 vạch giờ sáng lần lượt như đèn chạy, 6s/vòng.

## 2026-11-19 — Trạng thái "đang chạy" có vòng cung quay

- Nhấp nháy không nói rõ "đang chạy" bằng một vòng cung khuyết xoay tròn.
- Lớp CSS mới `.spinDot` dùng `transform-box: fill-box` để quay quanh tâm
  của chính nó thay vì tâm cả ảnh; có mặt trong danh sách tắt của
  `prefers-reduced-motion`.

## 2026-11-19 — `api_status()` tách 404 khỏi lỗi mạng

- `api()` trả `None` cho mọi lỗi nên không phân biệt được "workflow chưa có
  trên nhánh mặc định" với "mạng hỏng". `api_status()` trả `(mã, json)`.
- `api()` và `request_json()` có thêm `quiet=True` để dò workflow không làm
  ngập log CI bằng ba dòng 404 mỗi lượt chạy.

## 2026-11-19 — Test chống tái phát đúng lỗi của vòng này

- `test_every_workflow_file_is_on_the_strip`: so file trong `.github/workflows/`
  với danh sách của dải, cả hai chiều — thêm workflow mà quên dải là đỏ ngay.
- `test_workflow_states.py`: 11 test mô phỏng 404/success/failure/timeout/
  in_progress/queued/cancelled/không có lượt chạy/lỗi 500/không token.

## 2026-11-19 — README ngắn lại, đúng hơn

- Sáu dòng badge shields (3 hỏng) → một ảnh `assets/status.svg`.
- Bảng workflow thêm dòng `Workflow Status`, sửa nhịp chạy của 3D và thẻ số liệu.

## 2026-11-19 — Tài liệu: nhịp chạy và badge

- `docs/WORKFLOWS.md`: mục "Chọn nhịp thế nào" (bảng bốn loại dữ liệu), mục 7
  về dải trạng thái, ba dòng sự cố mới về badge và `workflow_dispatch`.
- `docs/FAQ.md`: vì sao badge báo `not found`, vì sao `Run workflow` không
  thấy workflow mới, bảng phút runner tính lại (~103 phút/ngày).
- `docs/ANIMATIONS.md`: mục hoạt ảnh của dải trạng thái.
- `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `scripts/svgkit/README.md`: thêm
  `status.py` vào bản đồ module và bản đồ test.

## 2026-11-19 — Thêm workflow mới: ba chỗ phải sửa

- `.github/workflows/`, `WORKFLOWS` trong `scripts/svgkit/status.py`, và bảng lịch
  chạy trong README + docs. Quên chỗ thứ hai thì dải trạng thái bỏ sót workflow
  mới mà không báo gì (đã có test so hai chiều).

## 2026-11-19 — Màu trạng thái không theo theme

- Dải trạng thái dùng 5 màu cố định theo nghĩa, không lấy từ `Palette`. "Đỏ =
  lỗi" phải đúng ở cả 6 bảng màu; màu trạng thái không phải màu trang trí.

## 2026-11-19 — Ba chú thích đã lỗi thời

- `generate_cards.py` còn ghi "vẽ lại mỗi 10 phút", `docs/WORKFLOWS.md` còn ghi
  `*/5` cho 3D. Sửa cả ba chỗ cho khớp nhịp mới — chú thích sai còn tệ hơn
  không có chú thích.

## 2026-11-19 — Khoá CSS mới và chuỗi mới bằng test

- 3 test cho `.spinDot`/`.dashFlow` (có định nghĩa + có trong danh sách tắt của
  `prefers-reduced-motion`), 3 test cho 9 khoá chuỗi của dải trạng thái ở cả
  hai ngôn ngữ.

## 2026-11-19 — Tài liệu dùng 'hơn N test'

- Bốn chỗ ghi số test cứng đã lệch ba lần trong một vòng. Đổi sang "hơn 230" để
  tài liệu không phải sửa mỗi lần thêm test; con số chính xác thì chạy bộ test.

## 2026-11-19 — Dải trạng thái cần quyền gì

- `actions: read` (đọc lượt chạy) và `contents: write` (commit SVG). Cả hai đã
  khai trong `permissions:` của `status.yml`; token mặc định của Actions có sẵn,
  không cần secret mới.

## 2026-11-19 — svgkit 2.1.0

- Thêm `status.py` (module thứ tám) nên nâng phiên bản nhỏ: 2.0.0 → 2.1.0. API
  cũ không đổi, chỉ thêm `status_strip`, `api_status`, `workflow_states`.

## 2026-11-19 — Bảng chu kỳ đã đủ

- Thêm `spinDot` 1.6s, `dashFlow` 2.6s, đèn chạy 6s, hạt bay 22s, scan 12.5s và
  9s, thanh ngôn ngữ "thở" 5s/6s — chỉnh nhịp cả trang giờ nằm ở một bảng.

## 2026-11-19 — Cổng 3D: sửa lỗi mốc 24 giờ không bao giờ tới

- Cổng so "lần chạy thành công gần nhất", nhưng lượt bị cổng bỏ qua **vẫn** là lượt thành công → mốc 24 giờ không bao giờ đạt được, ảnh chỉ đổi khi có push.
- Giờ so theo `git log -1 -- profile-3d-contrib` (lần ảnh đổi thật), cần `fetch-depth: 0`, và có 2 test dựng repo git tạm để khoá hành vi.

## 2026-11-19 — Icon lạ không còn để trống

- `icon()` rơi về `spark` thay vì trả chuỗi rỗng — không bao giờ có ô trống trong thẻ vì gõ sai tên icon.

## 2026-11-19 — Thẻ chờ có `<desc>`

- Trước đây thẻ tạm chỉ có `aria-label`; giờ có thêm mô tả nên trình đọc màn hình đọc được cả thẻ tạm.

## 2026-11-19 — Test tự soi mã nguồn

- Test mới quét `svgkit/*.py` để chắc mọi khoá `t("…")` đều có trong `STRINGS`, và mọi token `@…@` trong CSS đều có giá trị trong `Palette`.

## 2026-11-19 — docs/FAQ.md

- Tám câu hỏi hay gặp: cache ảnh, vì sao không chạy mỗi phút, tốn bao nhiêu phút runner, vì sao SVG, số liệu lệch, đổi theme, dùng lại code.

## 2026-11-19 — Mọi thứ đều tất định

- Sao, bụi sáng, dữ liệu demo đều dùng `random.Random(seed)` cố định — hai lần build cho ra file giống hệt (trừ thời gian), nên `--smart` đáng tin và test khẳng định được toạ độ chính xác.

## 2026-11-19 — docs/ANIMATIONS.md: bảng chu kỳ

- Một bảng gom toàn bộ chu kỳ hoạt ảnh (CSS và SMIL) để chỉnh nhịp cả trang ở một chỗ.

## 2026-11-19 — docs/TESTING.md

- Bản đồ 11 file test, mỗi file kiểm tra gì, cách viết test mới và CI chạy những gì.

## 2026-11-19 — docs/ARCHITECTURE.md

- Giải thích luồng dữ liệu, ranh giới module, vì sao chỉ dùng thư viện chuẩn, chiến lược hoạt ảnh, cách ghi file, xử lý lỗi và checklist thêm thẻ mới.

## 2026-11-19 — Hero: hai vòng lan toả quanh lõi

- Bán kính 26 → 86, mờ dần, chu kỳ 5.2 giây, lệch pha nửa chu kỳ — như nhịp thở của monogram.

## 2026-11-19 — Top languages: khoanh sáng ngôn ngữ đứng đầu

- Chấm màu của ngôn ngữ lớn nhất có thêm vòng mờ nhấp nháy — mắt bám vào đó trước.

## 2026-11-19 — Activity: nhãn ngày cao nhất

- Cột cao nhất có nhãn `cao nhất 1.1k`, ẩn đi khi hôm nay đã là ngày cao nhất (chỗ đó đã có chấm nhấp nháy).

## 2026-11-19 — `--dry-run` và `--quiet`

- `--dry-run` vẽ và kiểm tra nhưng không ghi file — xem trước mà không đụng ảnh thật.
- `--quiet` im lặng hoàn toàn khi mọi thứ ổn, chỉ còn lỗi trên stderr.

## 2026-11-19 — Bộ test lên 150

- Thêm test cho hạt bụi, cung rank, vành đồng hồ, đường trung bình, tia sáng và vân tay dữ liệu.

## 2026-11-19 — Footer: bong bóng sáng

- Sáu bong bóng bay từ đáy lên với chu kỳ 11 giây, lệch pha; thêm quầng sáng nhấp nháy sau tiêu đề.

## 2026-11-19 — Divider: tia sáng thứ hai

- Thêm một tia mảnh, mờ hơn, chạy ngược chiều 13 giây/lần — đường kẻ có chiều sâu hơn.

## 2026-11-19 — Activity: đường trung bình 14 ngày

- Đường nét đứt màu nhấn, kèm nhãn `TB 196` ở góc trái — chỉ hiện khi dữ liệu có chênh lệch thật.
- Mọi ngày bằng nhau thì ẩn đi, vì đường trung bình lúc đó chẳng nói gì.

## 2026-11-19 — Clock: đuôi kim giây

- Kim giây có thêm chấm đối trọng phía sau trục, đúng kiểu đồng hồ cơ.

## 2026-11-19 — Clock: vệt sáng quét quanh vành

- Một cung gradient `dasharray="70 320"` quay 18 giây/vòng, trên vành ngoài — vành cũng "thở" như kim.

## 2026-11-19 — Top languages: phần trăm tính trên toàn bộ byte code

- Trước đây tổng chỉ cộng 8 ngôn ngữ hiển thị, nên ngôn ngữ nhỏ bị "đội" phần trăm lên.
- Giờ tổng lấy từ mọi ngôn ngữ; phần còn lại hiện `+N ngôn ngữ khác · x%` ở góc phải.

## 2026-11-19 — Stats: chấm sáng ở đầu cung rank

- Điểm sáng đặt đúng toạ độ đầu cung (góc `-90 + 360×74%`), có quầng `glow` và nhịp `pulse`.
- Khung đầu tiên đã hiện sẵn — không dùng hiệu ứng mờ dần để trình xem tĩnh vẫn thấy.

## 2026-11-19 — Hero: bụi sáng bay lên

- 14 hạt sáng nhỏ dùng SMIL `animate` trên `cy` và `opacity`, chu kỳ 7–13 giây, lệch pha ngẫu nhiên nhưng cố định.
- Hạt bị đẩy ra khỏi vùng chữ, có test khoá lại.

## 2026-11-19 — `--smart`: kiểm tra mỗi 10 phút, commit khi có lý do

- Mỗi ảnh mang một dấu `<!-- data:… -->` là vân tay dữ liệu đã dùng để vẽ.
- Lượt sau, vân tay không đổi thì không ghi file và không commit — trang vẫn được kiểm tra mỗi 10 phút.

## 2026-11-19 — Bộ test vượt 130

- Thêm test cho `human()`, `esc()`, i18n dự phòng, tiêu đề/desc của từng thẻ và cổng workflow 3D.
- Test không cần mạng: mọi lời gọi API đều được thay bằng dữ liệu mẫu.

## 2026-11-19 — Cổng 3D không được chết im lặng

- `${GITHUB_REPOSITORY_OWNER}` chưa đặt + `set -u` → cổng thoát giữa đường và luôn bỏ qua lượt vẽ.
- Giờ có giá trị dự phòng, số đếm sai định dạng được đưa về 0, và 5 test dùng `gh` giả khoá lại hành vi.

## 2026-11-19 — `check_assets()` khai báo sai thứ tự

- Hàm nằm sau khối `if __name__ == "__main__"` nên khi chạy bằng script thì `NameError`.
- Đã chuyển lên trước `main()`, kèm 3 test chạy CLI qua `subprocess`.

## 2026-11-19 — Sửa lỗi `--check` chọn nhầm thư mục

- `--check` từng bỏ qua `--out` vì biến toàn cục `OUT_DIR` luôn khác rỗng — kiểm tra nhầm thư mục `assets/`.
- Test chạy CLI như tiến trình con đã bắt được lỗi này; trước đó test import module nên không thấy.

## 2026-11-19 — Ba cờ CLI mới

- `--version`, `--list-langs` và `--check` (parse mọi SVG trong thư mục ra rồi báo cáo).
- `--check` tiện cho người mới: vẽ xong, kiểm tra ngay, khỏi mở trình duyệt.

## 2026-11-19 — Tôn trọng `prefers-reduced-motion`

- Người bật “giảm chuyển động” trong hệ điều hành sẽ thấy ảnh tĩnh — không còn hoạt ảnh nào quay cuồng.
- Ảnh tĩnh vẫn đẹp vì khung đầu tiên đã được vẽ sẵn ở trạng thái cuối.

## 2026-11-19 — Mọi thẻ có `<title>` và `<desc>`

- Trước chỉ có `aria-label` — trình đọc màn hình đọc được nhưng công cụ tìm kiếm và chế độ đọc không thấy gì.
- Giờ mỗi tấm ảnh có tiêu đề trùng `aria-label` và một dòng mô tả riêng, đã dịch cả vi/en.

## 2026-11-19 — CONTRIBUTING: nhắc không sửa tay SVG

- `assets/*.svg` do máy sinh; sửa tay sẽ bị lượt workflow kế tiếp ghi đè.
- Thêm lệnh chạy bộ test ngay trên máy.

## 2026-11-19 — README ngắn hơn, nhiều hình hơn

- Thêm thẻ hoạt động và chân trang, nhưng số dòng vẫn giữ nguyên — chỗ mới lấy từ chỗ cũ rút gọn.

## 2026-11-19 — Health: thử vẽ cả 6 theme × 2 ngôn ngữ

- Mỗi lần push, CI vẽ lại toàn bộ SVG với mọi bảng màu và mọi ngôn ngữ rồi parse XML từng file.
- Bảng màu nào làm vỡ bố cục là biết ngay.

## 2026-11-19 — README Garden: mỗi 3 giờ

- Con dấu “lần cập nhật gần nhất” không cũ quá 3 giờ, chỉ tốn 8 lượt chạy mỗi ngày thay vì 1 lượt mỗi tuần.

## 2026-11-19 — Thẻ: cập nhật mỗi 30 phút

- `profile-cards.yml` chạy `*/30 * * * *`, thêm bước vẽ `activity.svg` (lỗi thì bỏ qua, không làm đỏ build).

## 2026-11-19 — 3D contrib: kiểm tra mỗi 5 phút

- Lịch `*/5 * * * *` cộng **cổng thông minh**: chỉ vẽ lại khi có PushEvent mới hoặc đã quá 24 giờ.
- Ảnh vẫn tươi theo phút mà không đốt hàng giờ runner mỗi ngày.

## 2026-11-19 — check_repo kiểm tra tham chiếu ảnh

- Mọi `./…` trong Markdown phải trỏ tới file có thật — đổi tên ảnh mà quên sửa README là bắt được ngay.
- Có 4 test riêng cho phần này.

## 2026-11-19 — check_repo quét mọi file Python

- Trước chỉ biên dịch `scripts/*.py`, giờ đi cả cây `scripts/` gồm `svgkit/` và `tests/`.
- Thiếu `__init__.py` trong thư mục con cũng bị cảnh báo.

## 2026-11-19 — Song ngữ Việt / Anh

- `--lang vi|en`. Mọi chuỗi nằm trong `scripts/svgkit/i18n.py`, không rải rác trong code vẽ.

## 2026-11-19 — Sáu bảng màu

- `--theme sky|emerald|violet|sunset|ocean|mono`, mỗi bảng màu là một bộ token `@ACCENT@`… thay vào CSS.
- `--list-themes` in ra danh sách kèm mã màu.

## 2026-11-19 — Activity: bỏ tổng Σ

- Góc phải hiện `Σ 2.7k` trùng ý với ô `CẢ NĂM 2.8k` bên trên.
- Thay bằng `HÔM NAY +0` — thông tin mới, không lặp.

## 2026-11-19 — Activity: cột 0 vẫn nhìn thấy

- Ngày không có contribution trước đây vẽ bằng màu nền nên mất hút.
- Đổi sang màu viền mờ 70% — nhìn được nhịp nghỉ, không phải lỗi render.

## 2026-11-19 — Stats: phần trăm rank theo i18n

- Chuỗi `74% tiến độ` trước đây hard-code `%d%%`, giờ đi qua khoá dịch `stats.progress`.

## 2026-11-19 — Đồng hồ: kim quay bằng CSS

- Ba kim dùng `animation-delay` âm để khớp giờ thật ngay sau khi commit, không cần chờ.
- Giữa hai lần workflow cập nhật, kim vẫn chạy — nhìn là biết trang còn sống.

## 2026-11-19 — Đồng hồ: thêm thứ và ngày

- Thẻ đồng hồ có thêm dòng `Thứ Năm · 19/11/2026` lấy từ `Translator.weekday()`.
- Icon mặt trời / mặt trăng đổi theo giờ, canh cạnh pill lời chào.

## 2026-11-19 — Footer: nâng chữ khỏi sóng

- Dòng “Làm bằng Python…” nằm đúng ngọn sóng nên chìm vào nền.
- Khối chữ nâng lên 14px, hai lớp sóng hạ xuống — chữ luôn nổi.

## 2026-11-19 — Hero: dấu nhắc vẽ bằng path

- Ký tự `›` phụ thuộc font, máy thiếu font sẽ ra ô vuông.
- Thay bằng một path chevron 2 nét — hiển thị giống nhau ở mọi nơi.

## 2026-11-19 — Hero: vệt sáng chuyển sang SMIL

- Vệt sáng quét qua tiêu đề trước đây dùng `clip-path` + CSS: trình xem nào đứng yên ở khung đầu sẽ thấy một mảng trắng đè nửa tiêu đề.
- Đổi sang `<animate attributeName="x">` — khung đầu nằm ngoài màn hình nên luôn sạch.

## 2026-11-19 — Hero: bỏ chip thứ tư bị tràn

- Chip `AI` chen vào vùng chữ cuối trang nên đã bỏ; ba chip `PY` / `JS` / `TS` xếp so le.
- Ít hơn nhưng không đè chữ — ưu tiên đọc được hơn là nhiều.

## 2026-11-19 — Divider phát sáng

- `assets/divider.svg` vẽ lại bằng f-string thay cho `%`-format (chuỗi CSS có dấu `%` từng làm crash).
- Tia sáng chạy dọc đường kẻ, có quầng mờ hai đầu.

## 2026-11-19 — Ảnh chân trang dạng sóng

- `assets/footer.svg`: hai lớp sóng chuyển động ngược chiều, lời cảm ơn + khẩu hiệu.
- Sóng nằm trong `clip-path="url(#cardBody)"` nên không tràn ra ngoài góc bo tròn.

## 2026-11-19 — Thẻ hoạt động 14 ngày

- `assets/activity.svg`: 14 cột contribution thật từ GraphQL, kèm chuỗi ngày hiện tại và chuỗi dài nhất.
- Không lấy được dữ liệu thì trả `None` và giữ ảnh cũ, không làm đỏ workflow.

## 2026-11-19 — svgkit 2.0 — tách thư viện vẽ

- `scripts/generate_cards.py` từ 1 file dài thành gói `scripts/svgkit/`: palette, i18n, primitives, hero, divider, cards, clock, activity, api.
- Thêm thẻ mới giờ chỉ là thêm một module, không phải sửa file khổng lồ.

## 2026-11-19 — Bộ kiểm thử tự động đầu tiên

- Hơn 100 unit test phủ palette, i18n, từng thẻ SVG, CLI và `check_repo.py`.
- Chạy bằng `python3 -m unittest discover -s scripts/tests -t scripts`, không cần cài gì thêm.
