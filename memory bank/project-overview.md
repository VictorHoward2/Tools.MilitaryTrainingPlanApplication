# Tổng quan dự án - Ứng dụng Quản lý Kế hoạch Huấn luyện

## Thông tin cơ bản

| Thuộc tính | Giá trị |
|------------|---------|
| **Tên sản phẩm** | Ứng dụng Quản lý Kế hoạch Huấn luyện |
| **Phiên bản** | 1.0.0 |
| **Chủ sở hữu/Tác giả** | Victor Howard |
| **Ngày tạo PRD** | 05/01/2026 |

## Mô tả ngắn gọn

Ứng dụng desktop hỗ trợ **giảng viên quân đội** quản lý môn học và thời khóa biểu: thiết kế kế hoạch huấn luyện, theo dõi tiến độ giảng dạy, và cung cấp tài liệu liên quan cho từng bài học.

## Vấn đề cần giải quyết

- Sắp xếp thời khóa biểu và lịch trình giảng dạy đang làm **thủ công**.
- Giảng viên phải **tự tìm tài liệu** mỗi lần đi dạy.
- Khó **theo dõi tiến độ**: bài nào đã dạy, bài nào chưa.

## Giải pháp

- Mỗi môn học có **danh sách bài giảng** cố định (tên, thời lượng, tài liệu).
- Hỗ trợ **nhập môn học** thủ công hoặc **import từ Excel** (có form mẫu).
- Tạo **thời khóa biểu** theo ngày/tuần/tháng với các ràng buộc (8h/ngày, tiết cố định).
- Mỗi bài học có thể **lưu tài liệu** trong thư mục `materials/{subject_id}/{lesson_id}`.

## Giá trị cốt lõi

1. Hỗ trợ thiết kế thời khóa biểu nhanh, đúng quy định.
2. Theo dõi tiến trình dạy (đã dạy / chưa dạy).
3. Cung cấp tài liệu dạy mỗi ngày cho giảng viên.

## Mục tiêu sản phẩm

- Quản lý môn học (CRUD) và bài học, kèm tài liệu.
- Hỗ trợ lập thời khóa biểu theo tuần/tháng.
- Xuất thời khóa biểu (PDF, Excel, ảnh).

## Đối tượng người dùng

### Persona 1: Người lập kế hoạch (Bộ đội, 25–35 tuổi)
- **Mục tiêu:** Lập thời khóa biểu cho nhiệm kỳ.
- **Pain point:** Mỗi nhiệm kỳ lại mất thời gian lập TKB mới.
- **Use case:** Dùng app để lên lịch tất cả môn học đáp ứng điều kiện (8h/ngày, tiết cố định).

### Persona 2: Giảng viên (30–60 tuổi)
- **Mục tiêu:** Xem lịch giảng dạy và tham khảo tài liệu.
- **Pain point:** Phải tự xem hôm nay dạy gì và tự tìm tài liệu.
- **Use case:** Xem lịch hôm nay/tuần/tháng và mở tài liệu theo bài học.

## Phạm vi (Scope)

**Trong phạm vi:**
- Thiết kế thời khóa biểu.
- Theo dõi tiến trình dạy.
- Cung cấp tài liệu theo môn/bài học.

**Ngoài phạm vi:** (PRD để trống, có thể bổ sung sau.)

## Giả định

- Giả định sẵn ~10 môn học, mỗi môn có nhiều bài giảng và tài liệu tương ứng.
- Ứng dụng single-user, chạy trên Windows.

## Lưu ý đồng bộ PRD ↔ App

- **Quản lý môn học:** Không có phân trang; hiển thị toàn bộ với tìm kiếm (tên/mã), sắp xếp và đếm kết quả.
- **Tạo TKB:** Khoảng thời gian bất kỳ (Thứ Hai–Chủ Nhật, có thể nhiều tuần). Flow thực tế: 3 bước theo tuần (chọn môn theo ngày có lọc phân loại → sắp thứ tự + giờ → chọn bài + giờ), Validate, Lưu.
- **Quản lý TKB:** Backend có xóa TKB; giao diện “Xem thời khóa biểu” chưa có nút xóa TKB.
- **Theo dõi tiến độ:** Có đánh dấu hoàn thành (từng ngày + tất cả ngày quá khứ), lịch, bảng tiến độ (lọc Đã/Chưa), click ngày xem lịch.

## Tài liệu tham chiếu

- **PRD đầy đủ (đã đồng bộ với app):** `PRD.md`
- **Chạy ứng dụng:** `RUN.md`
- **README:** `README.md`
- **Mapping chi tiết PRD ↔ Code:** `memory bank/features-and-requirements.md`
