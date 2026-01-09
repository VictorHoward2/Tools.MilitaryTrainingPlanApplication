# Ứng dụng Quản lý Kế hoạch Huấn luyện

Ứng dụng hỗ trợ giảng viên quân đội quản lý các môn học và thời khóa biểu. Hỗ trợ theo dõi tiến độ giảng dạy, huấn luyện và hỗ trợ xây dựng kế hoạch giảng dạy.

## Tính năng chính

- Quản lý môn học và bài giảng
- Tạo và quản lý thời khóa biểu
- Theo dõi tiến độ giảng dạy
- Cung cấp tài liệu liên quan đến môn học
- Export thời khóa biểu ra PDF/Excel/Image

## Yêu cầu hệ thống

- Python 3.9+
- Windows 10/11

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python -m src.main
```

## Đóng gói

```bash
pyinstaller --onefile --windowed src/main.py
```

