# Active Context - Ứng dụng Quản lý Kế hoạch Huấn luyện

*File này dùng làm ngữ cảnh chính khi làm việc với dự án (ví dụ trong Cursor).*

## Dự án là gì?

**Desktop app** (Python + PySide6) cho giảng viên quân đội: **quản lý môn học**, **tạo/xem thời khóa biểu**, **theo dõi tiến độ** giảng dạy, **lưu tài liệu** theo bài học. Single-user, dữ liệu lưu JSON trong `src/data/`.

## Cấu trúc nhanh

- **Entry:** `src/main.py` → MainWindow (`src/ui/main_window.py`).
- **4 màn hình chính:** SubjectManager, ScheduleCreator, ScheduleViewer, ProgressTracker (trong `src/ui/widgets/`).
- **Logic:** `src/services/` (FileService, AuthService, SubjectService, ScheduleService, ExcelService).
- **Dữ liệu:** `src/models/` (Subject, Lesson, Schedule, User); lưu trong `src/data/subjects/`, `schedules/`, `users.json`, `materials/`.
- **Đa ngôn ngữ:** `src/utils/i18n.py` + `resources/translations/vi.json`, `en.json`; dùng `tr("key")` trong UI.

## Quy tắc nghiệp vụ cần nhớ

- Môn học: tối đa 500 bài; chỉ **tên** bắt buộc; bài không có thời lượng thì dùng `default_duration`. Quản lý môn: search (tên/mã), sort (tên, mã, thời gian thêm, phân loại), đếm kết quả—**không phân trang**.
- TKB: khoảng bất kỳ (Thứ Hai–Chủ Nhật, có thể nhiều tuần). Tạo TKB: 3 bước theo tuần—chọn môn theo ngày (có lọc phân loại), sắp thứ tự + giờ, chọn bài + giờ; Validate theo cài đặt; Lưu. **Khung giờ trong ngày** (sáng/chiều/nghỉ trưa) và **tổng số tiếng/ngày** có thể **chỉnh trong Cài đặt** (theo mùa hè/mùa đông); **đánh giá TKB (Validate) phải theo đúng cài đặt**. Mặc định 8h/ngày; tiết cố định: Chào cờ T2, Nghỉ trưa (theo Cài đặt), Hành quân T4 (19h–21h), Văn hóa chính trị T5 đầu tháng. Xem TKB: chọn TKB + tuần, xuất PDF/Excel/Ảnh. Xóa TKB: có trong backend, **chưa có nút trong UI**.
- Theo dõi tiến độ: lịch, Hôm nay, đánh dấu hoàn thành (từng ngày hoặc tất cả ngày quá khứ), bảng tiến độ (lọc Đã/Chưa), click ngày xem lịch.
- User mặc định: `admin` / `admin` (tự tạo nếu chưa có user).

## Khi thêm tính năng / sửa lỗi

1. **Đọc PRD:** `PRD.md` (yêu cầu đầy đủ).
2. **Kiến trúc & data:** `memory bank/architecture.md`, `memory bank/data-models.md`.
3. **Mapping tính năng → code:** `memory bank/features-and-requirements.md`.
4. **Chạy & dev:** `RUN.md`, `memory bank/development-guide.md`.

## File trong memory bank

| File | Nội dung |
|------|----------|
| **project-overview.md** | Tổng quan, vấn đề, giải pháp, persona, scope |
| **architecture.md** | Stack, cấu trúc thư mục, luồng khởi động & dữ liệu, tiết cố định |
| **features-and-requirements.md** | FR từ PRD map tới file/module code |
| **data-models.md** | Subject, Lesson, Schedule, User, cách lưu file |
| **development-guide.md** | Cài đặt, chạy, test, đóng gói, quy ước |
| **active-context.md** | File này – ngữ cảnh nhanh cho AI/developer |
