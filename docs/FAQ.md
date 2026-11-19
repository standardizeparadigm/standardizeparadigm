# ❓ Hỏi nhanh đáp gọn

Những câu hay gặp khi xem (hoặc fork) trang này.

## Ảnh vừa cập nhật mà trang vẫn hiện ảnh cũ?

**Cache.** GitHub phục vụ ảnh qua CDN, giữ bản cũ vài phút. Cách kiểm tra:

1. Mở thẳng file: `https://github.com/standardizeparadigm/standardizeparadigm/blob/main/assets/stats.svg` — nếu số liệu ở đây đúng thì ảnh đã cập nhật.
2. Quay lại trang chủ, `Ctrl + F5` (hoặc `Cmd + Shift + R`).

Thường 1–5 phút là hết.

## Đồng hồ ghi 16:23 mà giờ Việt Nam là 16:41?

Thẻ đồng hồ là **ảnh chụp**, không phải đồng hồ hệ thống. Số lớn là giờ tại
lần vẽ gần nhất; dòng nhỏ `cập nhật 16:23` nói rõ đó là ảnh chụp lúc mấy giờ.

Sau khi chụp, kim vẫn quay bằng CSS (kim giây 60 giây/vòng, kim phút 1
giờ/vòng), nên ảnh "sống" giữa hai lần cập nhật — nhưng con số đứng yên cho
tới lượt chạy kế tiếp. Workflow vẽ lại mỗi 5 phút; nếu ảnh lâu hơn 15 phút,
hãy xem tab **Actions** xem lượt chạy gần nhất có lỗi không.

Nếu con số lệch đúng 7 tiếng thì đó là lỗi thật: mọi mốc thời gian đều được
quy về UTC+7 ở `api.to_vn()` trước khi vẽ, và `test_api_time.py` canh chỗ đó.

## Vì sao không chạy mỗi phút một lần?

GitHub Actions **không hỗ trợ** cron mỗi phút; chu kỳ ngắn nhất là `*/5`. Ngoài ra lượt chạy theo lịch có thể bị trễ vài phút khi hệ thống tải cao.

Nên trang này làm hai lớp:

- **Lớp ảnh**: đồng hồ 5 phút một lần, dải trạng thái 10 phút, biểu đồ 3D 30
  phút (có cổng 24h), thẻ số liệu và README 3 giờ một lần. Mỗi job giữ một phút
  riêng (:00, :02, :07, :13, :23) nên không hai job nào cùng `git push` một
  lúc — bảng phút đầy đủ ở [WORKFLOWS.md](./WORKFLOWS.md). Chỗ nào có `--smart`
  thì chỉ commit khi số liệu thật sự đổi.
- **Lớp hoạt ảnh**: CSS/SMIL trong file SVG làm ảnh **luôn chuyển động** giữa hai lần cập nhật. Kim đồng hồ quay liên tục, không cần workflow nào cả.
- **Lớp chữ số**: con số giờ:phút không phải một chuỗi tĩnh mà là 24 ô giờ +
  60 ô phút chồng lên nhau, mỗi ô chỉ hiện trong đúng phút của nó. Nên **số
  phút nhảy đúng mỗi phút** trên màn hình người xem, dù workflow chỉ chạy 5
  phút một lần — và kể cả khi máy bạn mất mạng.

Nói cách khác: thứ duy nhất cần workflow là phần *ngày tháng* và *vòng cung
tiến độ ngày*; phần "mấy giờ rồi" thì trình duyệt tự lo.

## Muốn xem đồng hồ lúc nửa đêm mà không phải chờ?

```bash
python3 scripts/generate_cards.py --clock --at 2026-11-19T23:50 --out /tmp/thu
```

`--at` nhận `2026-11-19T23:50`, `2026-11-19 23:50` hoặc `2026-11-19T23`, hiểu
theo giờ Việt Nam. Lệch múi giờ, cung tiến độ ngày, lời chào, icon mặt trăng —
tất cả vẽ theo đúng thời điểm đó. Dùng để chụp ảnh tài liệu, hoặc để kiểm tra
một khung giờ hiếm khi ai nhìn tới.

## Nhãn `9 giờ trước` trên dải trạng thái nghĩa là gì?

Đó là tuổi của **lần chạy gần nhất** của workflow đó, tính từ lúc dải được vẽ.

- `2 phút trước` — workflow vừa chạy xong, trạng thái còn nóng.
- `24 ngày trước` — workflow nằm trên nhánh khác và chưa từng chạy trên nhánh
  mặc định. Trạng thái khi đó là `CHỜ MERGE`; tuổi lớn chính là dấu hiệu.
- Không có nhãn — API không trả mốc thời gian. Thà thiếu nhãn còn hơn in một
  con số sai; `api.age_minutes()` trả `None` thay vì `0` trong trường hợp đó.

## Ảnh đẹp trong Chrome nhưng vỡ trong app GitHub?

Vì SVG không phải một chuẩn được hiểu giống nhau ở mọi nơi. Trình duyệt hiểu
`font: 800 54px Arial`; resvg và vài bản librsvg bỏ qua **cả khai báo** và
kéo chữ về 16px — số giờ teo lại, nhãn trên dải trạng thái chèn lên nhau.

Ba quy ước giữ cho ảnh đọc được ở mọi trình:

- **Không dùng `font:` viết tắt.** Viết `font-weight`, `font-size`,
  `font-family`. `check_repo.py` báo lỗi nếu quên.
- **Hoạt ảnh phải có trạng thái tĩnh đẹp sẵn.** Nhiều trình xem chỉ vẽ khung
  hình đầu tiên — nếu khung đó là `opacity: 0` thì người xem thấy ảnh trống.
- **`prefers-reduced-motion` tắt mọi chuyển động**, nhưng nội dung vẫn đủ.

## Dải trạng thái cần thêm quyền gì?

`actions: read` để đọc trạng thái các lần chạy, và `contents: write` để commit
`assets/status.svg`. Cả hai đều nằm trong `permissions:` của `status.yml`; token
mặc định của Actions có sẵn quyền này nên không cần tạo secret.

## Tốn bao nhiêu phút runner mỗi ngày?

| Workflow | Lượt/ngày | Thời gian mỗi lượt | Tổng |
| :-- | --: | --: | --: |
| `live-clock` | 288 | ~15 giây | ~72 phút |
| `status` | 96 (+ mỗi lượt chạy xong) | ~10 giây | ~16 phút |
| `profile-3d` | 48 (phần lớn bị cổng chặn) | ~8 giây khi bị chặn | ~7 phút + vài lượt vẽ thật |
| `profile-cards` | 8 (phần lớn `--smart` bỏ qua) | ~25 giây | ~4 phút |
| `readme-tend` | 8 | ~12 giây | ~2 phút |
| `health` | 1 + mỗi push | ~60 giây | ~2 phút |

Với repo công khai, phút runner miễn phí — nhưng vẫn giữ ở mức này để không bị coi là lạm dụng.

## `check_repo.py` báo lỗi BOM/CRLF, sửa tay từng file à?

Không cần: `python3 scripts/check_repo.py --fix`.

Cờ này chuẩn hoá những thứ vô hình với người đọc — BOM, xuống dòng CRLF,
khoảng trắng cuối dòng, dòng trống cuối file, thiếu newline cuối — rồi chạy
lại toàn bộ kiểm tra. Nó **không** đổi một ký tự nội dung nào: chữ tiếng Việt,
dấu em dash và dấu giữa (`·`) đi qua nguyên vẹn, và điều đó được khoá bằng test.

Chạy hai lần liên tiếp thì lần thứ hai không sửa gì — nếu không, workflow sẽ
tự đẩy một commit mỗi 5 phút.

## Muốn thêm một luật mới thì làm ở đâu?

Ba bước, theo đúng thứ tự:

1. Viết hàm `check_…()` trong `scripts/check_repo.py`, gọi `err()` khi sai và
   `warn()` khi chỉ đáng nhắc. Hàm nhận `root=None` để test được trên thư mục
   tạm thay vì repo thật.
2. Gọi nó trong `main()`, **ngay sau** hàm liên quan — để thứ tự đọc báo lỗi
   khớp thứ tự trong đầu người sửa.
3. Thêm một lớp vào `scripts/tests/test_check_repo.py`: một ca sạch phải im,
   một ca hỏng phải báo. Không có ca sạch thì luật dễ báo sai; không có ca
   hỏng thì luật có thể đã chết từ lâu mà không ai biết.

Nếu luật áp cho cả repo (không chỉ thư mục tạm), thêm một dòng nữa vào
`TestNewLawsOnRealRepo` trong `test_repo_workflows.py` — để sai quy ước là đỏ
ngay trên máy, không phải đợi CI.

## Để tab mở qua đêm thì ảnh có còn đúng không?

Tuỳ phần:

- **Số giờ:phút** — vẫn đúng. Nó là 84 ô chữ chồng nhau, trình duyệt tự đổi
  ô hiện mỗi phút, không cần mạng và không cần tải lại.
- **Kim đồng hồ** — vẫn đúng, chúng quay bằng CSS với chu kỳ thật.
- **Thứ, ngày tháng, vòng cung tiến độ ngày, lời chào** — đứng ở lúc ảnh được
  vẽ. Đó là lý do có dấu `cập nhật HH:MM`: bạn luôn biết mình đang xem ảnh
  chụp lúc nào. Tải lại trang là có bản mới (workflow vẽ lại mỗi 5 phút).

## Vì sao ảnh đồng hồ nặng thêm khoảng 12 KB?

Vì 84 ô số. Mỗi ô là một thẻ `<text>` kèm một `animation-delay`, cộng thêm
hai khối `@keyframes`. Đổi lại: con số đúng **mỗi phút** dù GitHub chỉ cho
cron 5 phút một lần, và đúng cả khi bạn mở file offline.

12 KB với ảnh đã có ~30 KB là mức đáng trả. Nếu cần nhẹ hơn, xoá
`_live_time()` trong `clock.py` là quay lại con số tĩnh — nhưng khi đó ảnh
sẽ "sai" trong khoảng 5 phút giữa hai lần vẽ.

## Vì sao là SVG mà không phải PNG?

- **Nhẹ**: thẻ 640×258 chỉ ~16 KB, PNG cùng kích thước dễ vượt 100 KB.
- **Nét**: phóng to bao nhiêu cũng sắc, hợp màn hình Retina.
- **Động**: chứa được CSS/SMIL — PNG thì không.
- **Chữ chọn được**: người xem có thể bôi đen số liệu, trình đọc màn hình đọc được.

Đổi lại: SVG cần trình duyệt để render, và một số nơi (email, một số trình xem markdown) chặn hoạt ảnh — nên mọi khung hình đầu tiên đều được vẽ đẹp sẵn.

## Số liệu trên thẻ khác số trên GitHub?

Có ba lý do chính đáng:

1. **Thời điểm**: thẻ được vẽ lúc workflow chạy, GitHub hiện tại có thể mới hơn vài phút.
2. **Phạm vi**: `stars` và `langs` chỉ tính repo **công khai**; repo private không được tính.
3. **Ngôn ngữ**: tính theo **byte code** (GitHub Linguist), không theo số file hay số dòng.

Nếu lệch cả tháng, có thể `GITHUB_TOKEN` hết quyền — xem log của workflow `Profile Cards`.

## Muốn đổi tên hiển thị hoặc bảng màu?

Không sửa file SVG. Sửa chỗ sinh ra nó:

- Tên: biến `DISPLAY_NAME` trong `.github/workflows/profile-cards.yml`.
- Bảng màu: thêm `--theme ocean` vào lệnh trong workflow (hoặc đổi `DEFAULT_THEME` trong `scripts/svgkit/palette.py`).
- Ngôn ngữ: `--lang en`.

Sau đó vào tab **Actions → Profile Cards → Run workflow**.

## Dùng lại code này cho trang của mình?

Được — giấy phép MIT. Gọn nhất là:

1. Fork repo.
2. Sửa `GH_USER` (workflow đã tự lấy `github.repository_owner`, thường không cần sửa).
3. Bật Actions, chạy `Profile Cards` một lần để có ảnh thật.
4. Xoá bớt mục bạn không cần trong `README.md`.

Nhớ đổi tên, tiểu sử và liên hệ — đừng để hai trang giống hệt nhau.


## Ảnh 3D đứng im dù workflow vẫn chạy xanh?

Đúng thiết kế: cổng thông minh bỏ qua lượt chạy khi chưa có push mới và ảnh chưa quá 24 giờ. Muốn vẽ ngay: **Actions → GitHub Profile 3D Contrib → Run workflow** — `workflow_dispatch` luôn đi qua cổng ở trạng thái "chưa có mốc", nên vẽ lại ngay.


## Dải trạng thái báo `CHỜ MERGE` nghĩa là gì?

Nghĩa là file workflow đó **chưa có trên nhánh mặc định**. Dải đọc Actions API
bằng tên file; API trả 404 thì dải ghi `CHỜ MERGE` thay vì đoán bừa.

Merge xong, lượt chạy kế tiếp của `status.yml` sẽ đổi nó thành `ĐẠT` (hoặc
`LỖI` nếu workflow đỏ). Đây là trạng thái tạm, không phải lỗi cấu hình.

## Badge trên trang báo `repo or workflow not found`?

Badge shields.io đọc trạng thái qua API `.../actions/workflows/<file>`, và
API đó **chỉ thấy workflow nằm trên nhánh mặc định**. Workflow còn ở nhánh
khác thì badge trả `repo or workflow not found`; workflow có trên nhánh
mặc định nhưng chưa chạy xong lần nào thì trả `no status`.

Cách chắc chắn nhất: dùng `assets/status.svg` — repo tự vẽ dải trạng thái
bằng token của chính nó, nên không có khái niệm "không tìm thấy".

## Đã thêm workflow mới, sao không chạy tay được?

`workflow_dispatch` chỉ xuất hiện khi file workflow **đã có trên nhánh mặc
định**. Đây là quy định của GitHub, không phải lỗi cấu hình: `gh workflow
run` trên một workflow chỉ có ở nhánh phụ sẽ trả HTTP 404.

Merge trước, chạy sau.
