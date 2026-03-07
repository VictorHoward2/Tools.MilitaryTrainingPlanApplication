# Hướng dẫn phát triển và chạy ứng dụng

## Yêu cầu hệ thống

- **Python:** 3.9+
- **Hệ điều hành:** Windows 10/11 (theo PRD)

## Cài đặt

```bash
pip install -r requirements.txt
```

**Dependencies chính:** PySide6, openpyxl, reportlab, Pillow, python-dateutil; pytest, pytest-qt cho test.

## Chạy ứng dụng

```bash
python src/main.py
```

- **Đăng nhập mặc định (tạo lần đầu nếu chưa có user):** Username `admin`, Password `admin`.
- Dữ liệu nằm trong `src/data/` (tự tạo nếu chưa có).

## Cấu trúc chạy (tóm tắt)

1. `main.py`: splash, tạo user mặc định nếu cần, mở MainWindow.
2. MainWindow: đăng nhập (LoginDialog) → 4 view: Môn học, Tạo TKB, Xem TKB, Tiến độ.
3. Mọi thao tác đọc/ghi qua services → FileService (JSON + thư mục materials).

## Test

```bash
pytest tests/
```

- `tests/test_models.py`: model (Subject, Lesson, Schedule, User).
- `tests/test_services.py`: services (file, auth, subject, schedule theo thiết kế hiện tại).

## Đóng gói (theo README)

```bash
pyinstaller --onefile --windowed src/main.py
```

(Đường dẫn data/icons có thể cần cấu hình lại khi đóng gói để trỏ đúng thư mục trong bản build.)

## Quy ước code (theo PRD)

- **Code style:** PEP 8, type hints.
- **Documentation:** Comment trong code.
- **Testing:** Unit test (PRD đề cập coverage > 80%).

## Thư mục và file quan trọng khi dev

- **Thêm key đa ngôn ngữ:** Sửa `resources/translations/vi.json` và `en.json`, dùng `tr("key")` trong UI.
- **Đổi tiết cố định:** Sửa `src/utils/constants.py` (FIXED_SCHEDULE_ITEMS) hoặc thêm file `src/data/subjects/fixed_subjects.json`.
- **Đổi giờ/ngày học:** `src/utils/constants.py` (SCHEDULE_MORNING_*, SCHEDULE_AFTERNOON_*, DAILY_TOTAL_HOURS).
- **Logo/icon:** `resources/icons/logo.jpg`; tham chiếu trong `main.py` và `main_window.set_window_icon()`.
