# Hướng dẫn chạy ứng dụng

## Yêu cầu hệ thống

- Python 3.9 hoặc cao hơn
- Windows 10/11

## Cài đặt

1. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

1. Chạy ứng dụng:
```bash
python src/main.py
```

2. Đăng nhập:
   - Username: `admin`
   - Password: `admin`
   (Tài khoản mặc định sẽ được tạo tự động lần đầu chạy)

## Cấu trúc dự án

- `src/main.py`: Entry point của ứng dụng
- `src/models/`: Các data models (Subject, Lesson, Schedule, User)
- `src/services/`: Business logic services
- `src/ui/`: Giao diện người dùng
- `src/data/`: Thư mục lưu trữ dữ liệu (JSON files)
- `tests/`: Unit tests

## Tính năng chính

1. **Quản lý môn học**: Thêm, sửa, xóa môn học và bài học
2. **Tạo thời khóa biểu**: Tạo thời khóa biểu theo tuần/tháng
3. **Xem thời khóa biểu**: Xem và xuất thời khóa biểu ra PDF/Excel/Image
4. **Theo dõi tiến độ**: Đánh dấu bài đã dạy và xem lịch sử

## Lưu ý

- Dữ liệu được lưu trong `src/data/` dưới dạng JSON files
- Logs được lưu trong thư mục `logs/`
- Tài liệu giảng dạy được lưu trong `src/data/materials/`

