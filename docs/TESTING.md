# 🧪 Kiểm thử

Bộ test chạy bằng `unittest` của Python — không cần `pytest`, không cần mạng, không cần token. Toàn bộ dữ liệu GitHub trong test là dữ liệu giả dựng sẵn.

```bash
python3 -m unittest discover -s scripts/tests -t scripts        # chạy hết
python3 -m unittest discover -s scripts/tests -t scripts -v     # in tên từng test
python3 -m unittest tests.test_clock -v                          # chỉ một file
```

Hiện có **159 test** trên 11 file, chạy xong trong chưa tới 1 giây.

