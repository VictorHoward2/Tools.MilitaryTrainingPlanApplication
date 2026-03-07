# Tính năng và Yêu cầu (Mapping PRD ↔ Code)

*Tài liệu này đã được đồng bộ với PRD.md và thực tế triển khai trong source.*

## P0 - Must Have

### FR-001: Nhập môn học
- **PRD:** Môn học gồm tên, mã, bài học (tên, thời lượng, tài liệu), địa điểm, thời lượng mặc định, yêu cầu (môn tiên quyết), phân loại. Nhập thủ công hoặc từ Excel.
- **Code:** Model: `src/models/subject.py`, `src/models/lesson.py`. Form: `subject_form.py`. Service: `SubjectService.create_subject()`, `SubjectService.import_from_excel()`; `ExcelService.import_subject_from_excel()`, `ExcelService.create_subject_template()`. Lưu: `FileService.save_subject()` → `subjects/{subject_id}.json` + `subjects_summary.json`; tài liệu: `materials/{subject_id}/{lesson_id}/`.

### FR-002: Quản lý môn học
- **PRD:** Danh sách môn học, thêm/sửa/xóa; sắp xếp (tên, mã, thời gian thêm, phân loại); tìm kiếm (tên hoặc mã), hiển thị số kết quả. *(Phân trang: PRD ghi có thể bổ sung khi số lượng rất lớn; hiện tại app hiển thị toàn bộ trong một bảng.)*
- **Code:** `subject_manager.py`: bảng, search (`SubjectService.search_subjects()`), sort (combo), đếm kết quả, nút Thêm/Sửa/Xóa/Import/Template.

### FR-003: Sửa môn học
- **PRD:** Sửa thông tin môn học.
- **Code:** SubjectManager mở SubjectForm với subject đã chọn; `SubjectService.update_subject()`.

### FR-004: Xóa môn học
- **PRD:** Xóa môn học.
- **Code:** `SubjectService.delete_subject()` → `FileService.delete_subject()` (xóa file môn + thư mục materials + cập nhật summary).

### FR-005: Tạo kế hoạch huấn luyện (thời khóa biểu)
- **PRD:** Khoảng thời gian bất kỳ (Thứ Hai–Chủ Nhật, có thể nhiều tuần). 3 bước theo tuần: (1) Chọn môn theo từng ngày (bảng 6 cột), lọc phân loại chính/phụ khi thêm môn, “Xếp môn giống tuần trước”; (2) Sắp thứ tự môn và chọn giờ (Lên/Xuống); (3) Chọn bài học và giờ cho từng môn. Validate tuần theo **cài đặt** (số tiếng/ngày = khung sáng + chiều theo Cài đặt), Lưu TKB. Khung giờ trong ngày có thể chỉnh trong Cài đặt (theo mùa hè/mùa đông); quy định đánh giá TKB theo cài đặt.
- **Code:** `schedule_creator.py`: chọn start/end date, tạo schedule; điều hướng tuần; 3 bước với `step_stack`; dialog `AddSubjectDialog` (lọc phân loại chính/phụ, chọn môn); `ChooseLessonDialog` (chọn bài + giờ); nút Copy tuần trước, Validate, Lưu. `ScheduleService`: `create_schedule()`, `_add_fixed_items()`, `set_day_subjects()`, `set_day_subject_time()`, `set_day_subject_lesson()`, `build_week_items()`, `validate_day_schedule()`, `suggest_adjustments()`, `save_schedule()`. `ScheduleService` nhận `Settings`; dùng `get_schedule_times_from_settings(day, settings)`; `daily_total_hours` tính từ khung đã cấu hình; `validate_day_schedule()`/`suggest_adjustments()` theo cài đặt. Cài đặt: `settings_widget.py`, `Settings`.

### FR-006: Quản lý thời khóa biểu
- **PRD:** Danh sách TKB, xóa TKB. *(PRD ghi: xóa TKB có trong backend; giao diện chưa có nút xóa—có thể bổ sung.)*
- **Code:** Backend: `ScheduleService.delete_schedule()`, `FileService.delete_schedule()`. UI: màn hình “Xem thời khóa biểu” (ScheduleViewer) chỉ có chọn TKB, chọn tuần, xem, xuất—**chưa có nút Xóa TKB**.

### FR-007: Xem thời khóa biểu
- **PRD:** Chọn TKB và tuần, hiển thị bảng 6 cột (T2–T7); xuất PDF (toàn bộ tuần), Excel (toàn bộ TKB), ảnh (tuần đang chọn).
- **Code:** `schedule_viewer.py`: combo TKB, combo tuần, bảng, nút Xuất PDF/Excel/Ảnh. PDF: reportlab, xuất tất cả tuần. Excel: `ExcelService.export_schedule_to_excel()`. Ảnh: Pillow, chỉ tuần hiện tại.

## P1 - Should Have

### FR-008: Theo dõi tiến độ
- **PRD:** Chọn TKB; lịch (calendar); “Hôm nay” + nút Đánh dấu đã hoàn thành; bảng tiến độ (lọc Đã/Chưa hoàn thành); Đánh dấu tất cả ngày quá khứ; click ngày xem lịch ngày đó.
- **Code:** `progress_tracker.py`: combo TKB, QCalendarWidget, nhóm “Hôm nay” + `mark_complete_btn`, bảng tiến độ (cột Ngày, Thời gian, Môn học, Bài học, Trạng thái), checkbox Đã hoàn thành/Chưa hoàn thành, nút “Đánh dấu tất cả ngày quá khứ”, `show_date_schedule()` khi click ngày. Lưu trạng thái: `DaySchedule.is_completed`; `ScheduleService.save_schedule()`.

## Khác biệt đã đồng bộ PRD ↔ App

| Nội dung | Trước (PRD cũ) | Sau (đã cập nhật) |
|----------|----------------|-------------------|
| FR-002 phân trang | “Phân thành trang” khi nhiều môn | Ghi rõ: hiện tại không phân trang, chỉ danh sách + search/sort + đếm kết quả |
| FR-005 phạm vi | “Cho một tháng” | “Một khoảng thời gian bất kỳ (Thứ Hai–Chủ Nhật, có thể nhiều tuần)” |
| FR-005 flow | Mô tả chung “chọn phân loại → môn → bài” | 3 bước theo tuần + dialog lọc phân loại + Validate + Lưu |
| FR-006 / FR-007 | Hai mục cùng số FR-006 | FR-006 Quản lý TKB (xóa có backend, chưa UI); FR-007 Xem TKB |
| Theo dõi tiến độ | FR-007, mô tả ngắn | FR-008, mô tả đầy đủ: lịch, Hôm nay, đánh dấu hoàn thành, bảng lọc, đánh dấu hàng loạt, xem lịch theo ngày |

## Phi chức năng (tóm tắt)

- **Đăng nhập:** AuthService, LoginDialog; users.json; mật khẩu hash SHA256.
- **Đa ngôn ngữ:** i18n.py, resources/translations/vi.json, en.json; menu Language; tr(key).
- **Giao diện:** PySide6, toolbar, status bar.

## File tham chiếu nhanh

| Yêu cầu | File chính |
|--------|------------|
| Nhập/QL môn học | subject_form.py, subject_manager.py, subject_service.py, excel_service.py |
| Tạo TKB | schedule_creator.py (AddSubjectDialog, ChooseLessonDialog), schedule_service.py, constants.py |
| Xem/xuất TKB | schedule_viewer.py, excel_service.py |
| Theo dõi tiến độ | progress_tracker.py, schedule_service.py |
| Auth | auth_service.py, login_dialog.py, user.py |
| Lưu trữ | file_service.py |
| i18n | i18n.py, resources/translations/*.json |
