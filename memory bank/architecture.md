# Kiến trúc ứng dụng

## Technology Stack

| Thành phần | Công nghệ |
|------------|-----------|
| **Ngôn ngữ** | Python 3.9+ |
| **GUI** | PySide6 (Qt for Python) |
| **Lưu trữ** | File JSON (không dùng database) |
| **Import/Export Excel** | openpyxl |
| **Xuất PDF/ảnh** | reportlab, Pillow |
| **Đóng gói** | PyInstaller (theo PRD) |
| **Test** | pytest, pytest-qt |

## Cấu trúc thư mục

```
MilitaryTrainingPlanApplication/
├── src/
│   ├── main.py                 # Entry point, splash, tạo user mặc định
│   ├── config/
│   │   └── settings.py         # Cài đặt app (language, v.v.)
│   ├── models/                 # Data models (dataclass)
│   │   ├── subject.py          # Subject, categories
│   │   ├── lesson.py           # Lesson
│   │   ├── schedule.py         # Schedule, WeekSchedule, DaySchedule, ScheduleItem
│   │   └── user.py            # User (auth)
│   ├── services/               # Business logic
│   │   ├── file_service.py     # Đọc/ghi JSON, thư mục data
│   │   ├── auth_service.py    # Đăng nhập/đăng xuất, tạo user
│   │   ├── subject_service.py # CRUD môn học, import Excel
│   │   ├── schedule_service.py # Tạo/sửa TKB, tiết cố định, validate 8h
│   │   └── excel_service.py   # Import subject, export schedule, template
│   ├── ui/
│   │   ├── main_window.py      # Cửa sổ chính, menu, toolbar, stacked views
│   │   ├── dialogs/
│   │   │   ├── login_dialog.py
│   │   │   └── lesson_dialog.py
│   │   ├── widgets/
│   │   │   ├── subject_manager.py   # Danh sách môn học, search, sort, CRUD
│   │   │   ├── subject_form.py     # Form thêm/sửa môn học
│   │   │   ├── schedule_creator.py # Tạo TKB theo tuần, 3 bước
│   │   │   ├── schedule_viewer.py  # Xem TKB, xuất PDF/Excel/Image
│   │   │   └── progress_tracker.py # Lịch, đánh dấu hoàn thành
│   │   └── utils/
│   │       ├── helpers.py
│   │       └── validators.py
│   └── utils/
│       ├── constants.py        # Giờ học, tiết cố định, categories
│       ├── date_utils.py       # Tuần, ngày, thời lượng
│       ├── i18n.py            # Đa ngôn ngữ (vi/en)
│       └── logger.py
├── resources/
│   ├── icons/                 # logo.jpg (Quân khu 1)
│   └── translations/
│       ├── vi.json
│       └── en.json
├── tests/
│   ├── test_models.py
│   └── test_services.py
├── memory bank/               # Tài liệu dự án (các file .md này)
├── PRD.md
├── RUN.md
├── README.md
├── requirements.txt
└── setup.py
```

## Luồng khởi động

1. **`src/main.py`**
   - Thêm project root vào `sys.path`.
   - Tạo `QApplication`, set icon, hiện splash screen (logo).
   - `FileService` + `AuthService`: nếu chưa có user thì tạo user mặc định `admin`/`admin`.
   - Tạo `MainWindow`, show; đóng splash.

2. **`MainWindow` (`main_window.py`)**
   - Khởi tạo: `FileService`, `AuthService`, `SubjectService`, `ScheduleService`.
   - Nếu chưa đăng nhập → mở `LoginDialog`; không đăng nhập thì đóng app.
   - `setup_ui`: `QStackedWidget` với 4 view: SubjectManager (0), ScheduleCreator (1), ScheduleViewer (2), ProgressTracker (3).
   - Menu: File (logout, exit), View (4 view), Language (vi/en), Help (about).
   - Toolbar: 4 nút view + Refresh. Status bar: user, message.

## Luồng dữ liệu

- **Đọc/ghi:** Tất cả qua `FileService`.
  - Môn học: `src/data/subjects/` (mỗi môn `{subject_id}.json` + `subjects_summary.json`).
  - Thời khóa biểu: `src/data/schedules/` (mỗi TKB `{schedule_id}.json` + `schedules_summary.json`).
  - User: `src/data/users.json`.
  - Tài liệu: `src/data/materials/{subject_id}/{lesson_id}/`.
- **Ngôn ngữ:** `src/utils/i18n.py` đọc `resources/translations/{vi|en}.json`, `tr(key)` để lấy chuỗi; `Settings` lưu language trong `src/data/settings.json`.

## Khung giờ trong ngày và Cài đặt

- **Cài đặt (Settings):** Khung giờ trong ngày (giờ bắt đầu/kết thúc sáng, nghỉ trưa, chiều) và khoảng mùa hè/mùa đông có thể chỉnh trong màn hình **Cài đặt** (`SettingsWidget`); lưu trong `src/data/settings.json`. `ScheduleService` nhận `Settings` và dùng `get_schedule_times_from_settings(day_date, settings)` để lấy khung giờ theo ngày; **số tiếng/ngày** (`daily_total_hours`) được **tính từ khung đã cấu hình** (sáng + chiều) trong `season_schedule.get_schedule_times_from_settings`, nên **đánh giá TKB (Validate) luôn theo cài đặt**.

## Tiết cố định (Fixed schedule items)

- Định nghĩa: `src/utils/constants.py` → `FIXED_SCHEDULE_ITEMS` (Chào cờ, Nghỉ trưa, Hành quân, Văn hóa chính trị tinh thần).
- Có thể ghi đè bằng file: `src/data/subjects/fixed_subjects.json` (format có `name`, `rule`, `day_of_week`, `time_ranges`, `is_break`, `first_thursday_of_month`).
- `ScheduleService._add_fixed_items()` thêm các tiết này vào từng ngày khi tạo TKB; **thời gian Nghỉ trưa/Chào cờ/Văn hóa** lấy từ khung giờ theo Cài đặt (season).

## Quy tắc nghiệp vụ chính

- **Môn học:** Tối đa 500 bài học; chỉ **tên môn học** bắt buộc; thời lượng bài không có thì dùng `default_duration` của môn. Quản lý môn học: danh sách + tìm kiếm (tên/mã) + sắp xếp (tên, mã, thời gian thêm, phân loại) + đếm kết quả; **không có phân trang** (hiển thị toàn bộ trong một bảng).
- **Thời khóa biểu:** Khoảng bất kỳ (Thứ Hai–Chủ Nhật, có thể nhiều tuần). Tạo TKB: 3 bước theo tuần—(1) Chọn môn theo từng ngày (dialog lọc phân loại chính/phụ), có “Xếp môn giống tuần trước”; (2) Sắp thứ tự môn và chọn giờ; (3) Chọn bài học và giờ; Validate theo cài đặt, Lưu. **Khung giờ trong ngày** (sáng/chiều/nghỉ trưa) và **số tiếng/ngày** có thể **chỉnh trong Cài đặt** (Settings, theo mùa hè/mùa đông); **đánh giá TKB (Validate) theo đúng cài đặt** (tổng tiếng = sáng + chiều theo khung đã cấu hình). Mặc định 8 tiếng/ngày; 6 ngày/tuần (T2–T7). Tiết cố định: Chào cờ (T2), Nghỉ trưa (theo Cài đặt), Hành quân (T4, 19h–21h), Văn hóa chính trị (T5 đầu tháng). Xem TKB: chọn TKB + tuần, bảng 6 cột; xuất PDF/Excel/Ảnh. **Quản lý TKB:** backend có `delete_schedule()`; giao diện Xem TKB **chưa có nút xóa TKB**.
- **Theo dõi tiến độ (FR-008):** Chọn TKB; lịch; “Hôm nay” + đánh dấu hoàn thành; bảng tiến độ (lọc Đã/Chưa hoàn thành); đánh dấu tất cả ngày quá khứ; click ngày xem lịch ngày đó.
