# ShorLab - Demo cho bài tập lớn Mật mã nâng cao

ShorLab là hệ thống web cục bộ, không cần cài thư viện web bên ngoài Python.

## Nhóm thực hiện

| Vai trò | Họ và tên | Mã học viên |
|---|---|---|
| Nhóm trưởng | Dương Công Kiên | B25CHKH072 |
| Thành viên | Nguyễn Cảnh Huỳnh | B25CHKH071 |
| Thành viên | Phạm Anh Tuấn | B25CHKH086 |

## Chức năng

1. Mô phỏng tìm chu kỳ và hậu xử lý thuật toán Shor để phân tích số nhỏ.
2. Demo RSA đầu-cuối: tạo khóa, mã hóa, phân tích `n`, khôi phục `d`, giải mã.
3. Minh họa ECDLP trên đường cong nhỏ; việc tìm khóa trong demo dùng vét cạn cổ điển.
4. Tối ưu lựa chọn bộ tham số ML-KEM bằng biến nhị phân, hàm mục tiêu trọng số và ràng buộc tài nguyên.

## Cấu trúc mã nguồn

- `project_info.py`: thông tin chính thức của nhóm và dự án.
- `core.py`: số học mô-đun, mô phỏng hậu xử lý Shor, RSA, ECC và mô hình tối ưu.
- `app.py`: giao diện web cục bộ và API JSON.
- `generate_outputs.py`: sinh JSON, CSV và các hình minh họa dùng trong báo cáo.
- `output/`: kết quả được sinh tự động từ chương trình.

## Chạy trên Windows

```bat
run_demo.bat
```

Hoặc:

```bash
python app.py
```

Mở trình duyệt tại `http://127.0.0.1:8000`.

## Kiểm thử và sinh kết quả

```bash
python app.py --test
python generate_outputs.py
```

## Lưu ý học thuật

Phần tìm chu kỳ được mô phỏng cổ điển để chạy trên máy tính thông thường. Đây không phải là tuyên bố đã thực thi Shor trên phần cứng lượng tử chịu lỗi. Phần hậu xử lý GCD, khôi phục khóa RSA và mô hình tối ưu là chương trình thực thi đầy đủ.
