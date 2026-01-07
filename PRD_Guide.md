# HƯỚNG DẪN SỬ DỤNG PRD TEMPLATE

## Tổng Quan
File `PRD_Template.md` là một bản Product Requirements Document (Bản Yêu Cầu Sản Phẩm) đầy đủ và chuyên nghiệp, được thiết kế đặc biệt cho việc phát triển ứng dụng desktop Python trên Windows.

## Cách Sử Dụng

### 1. Bắt Đầu
- Mở file `PRD_Template.md`
- Điền các thông tin cơ bản ở phần 1 (Thông Tin Tổng Quan)
- Xác định trạng thái của document

### 2. Các Phần Quan Trọng Cần Điền Đầu Tiên

#### Phần 2: Tổng Quan Sản Phẩm
- **Mô tả ngắn gọn:** Viết 2-3 câu về ứng dụng
- **Vấn đề cần giải quyết:** Xác định rõ vấn đề
- **Giải pháp:** Mô tả cách ứng dụng giải quyết vấn đề
- **Giá trị cốt lõi:** Liệt kê 3-5 lợi ích chính

#### Phần 4: Đối Tượng Người Dùng
- Tạo 1-2 user personas
- Viết 5-10 user stories quan trọng nhất

#### Phần 5: Tính Năng Chức Năng
- Ưu tiên các tính năng theo thứ tự P0 (Must Have) → P1 (Should Have) → P2 (Nice to Have)
- Mỗi tính năng cần có:
  - Mô tả rõ ràng
  - User story
  - Acceptance criteria (tiêu chí chấp nhận)
  - Input/Output
  - Business rules

### 3. Các Phần Kỹ Thuật

#### Phần 6: Tính Năng Phi Chức Năng
- Đặt mục tiêu cụ thể cho hiệu năng
- Xác định yêu cầu bảo mật
- Quyết định về khả năng sử dụng

#### Phần 7: Giao Diện Người Dùng
- Mô tả design principles
- Chọn color scheme và theme
- Liệt kê các màn hình chính
- Tạo wireframes/mockups (có thể tham chiếu đến file riêng)

#### Phần 8: Dữ Liệu và Lưu Trữ
- Thiết kế data model
- Chọn phương thức lưu trữ (SQLite thường phù hợp cho desktop app)
- Xác định import/export formats

#### Phần 12: Yêu Cầu Kỹ Thuật
- Chọn GUI framework (khuyến nghị: PyQt5/6 cho ứng dụng chuyên nghiệp)
- Liệt kê các thư viện cần thiết
- Xác định build và deployment process

### 4. Planning

#### Phần 13: Timeline và Milestones
- Chia dự án thành các phases
- Đặt các milestones quan trọng
- Ước tính thời gian cho mỗi phase

#### Phần 14: Rủi Ro và Phụ Thuộc
- Xác định các rủi ro kỹ thuật
- Liệt kê dependencies
- Đề xuất mitigation strategies

### 5. Success Metrics

#### Phần 15: Tiêu Chí Thành Công
- Đặt KPIs cụ thể
- Xác định acceptance criteria
- Định nghĩa "Definition of Done"

## Tips và Best Practices

### 1. Ưu Tiên Tính Năng
- **P0 (Must Have):** Tính năng không thể thiếu, ứng dụng không hoạt động được nếu thiếu
- **P1 (Should Have):** Tính năng quan trọng nhưng có thể release sau
- **P2 (Nice to Have):** Tính năng làm tăng giá trị nhưng không bắt buộc

### 2. User Stories Format
Sử dụng format: "As a [user type], I want [goal] so that [benefit]"

Ví dụ:
- "As a student, I want to create a timetable so that I can organize my classes"
- "As a teacher, I want to export timetable to PDF so that I can share it with students"

### 3. Acceptance Criteria
Mỗi tính năng nên có 3-5 acceptance criteria cụ thể, có thể test được.

Ví dụ:
- User có thể tạo mới một timetable entry
- User có thể chỉnh sửa timetable entry đã tồn tại
- Hệ thống validate input trước khi lưu

### 4. Technical Decisions
Khi điền phần 12 (Yêu Cầu Kỹ Thuật), cân nhắc:
- **PyQt5/6:** Phù hợp cho ứng dụng phức tạp, cần UI đẹp
- **Tkinter:** Đơn giản, built-in, phù hợp cho ứng dụng nhỏ
- **SQLite:** Phù hợp cho desktop app, không cần server
- **PyInstaller:** Tool phổ biến để tạo .exe file

### 5. Keep It Updated
- Cập nhật PRD khi có thay đổi
- Ghi lại changes trong Change Log (Phần 17.2)
- Review định kỳ với team/stakeholders

## Checklist Trước Khi Bắt Đầu Development

- [ ] Đã điền đầy đủ phần 1-5 (Overview, Goals, Users, Features)
- [ ] Đã xác định rõ các tính năng P0
- [ ] Đã chọn technology stack
- [ ] Đã thiết kế data model cơ bản
- [ ] Đã có timeline và milestones
- [ ] Đã xác định success criteria
- [ ] PRD đã được review và approved

## Sử Dụng PRD Với AI (Cursor)

Khi làm việc với AI như Cursor, PRD này sẽ giúp:

1. **Cung cấp context đầy đủ:** AI có thể đọc PRD để hiểu rõ yêu cầu
2. **Tạo code phù hợp:** AI sẽ tạo code theo đúng specifications
3. **Đảm bảo tính nhất quán:** Tất cả features đều align với PRD
4. **Tạo tests:** AI có thể tạo tests dựa trên acceptance criteria

### Cách Sử Dụng Với Cursor:
1. Điền đầy đủ PRD
2. Share PRD với Cursor: "Đọc PRD_Template.md và bắt đầu implement theo yêu cầu"
3. Cursor sẽ đọc và hiểu toàn bộ requirements
4. Bắt đầu development từ các tính năng P0

## Tài Liệu Tham Khảo

- [How to Write a PRD](https://www.atlassian.com/agile/product-management/requirements)
- [User Story Mapping](https://www.jpattonassociates.com/user-story-mapping/)
- [Acceptance Criteria Best Practices](https://www.agilealliance.org/glossary/acceptance-criteria/)

---

**Lưu ý:** Template này có thể được tùy chỉnh theo nhu cầu cụ thể của dự án. Không phải tất cả các phần đều bắt buộc - hãy điều chỉnh cho phù hợp với quy mô và độ phức tạp của ứng dụng.

