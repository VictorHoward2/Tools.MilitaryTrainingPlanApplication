# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Ứng dụng Quản lý Kế hoạch Huấn luyện

---

## 1. THÔNG TIN TỔNG QUAN

### 1.1. Tên Sản Phẩm
**Ứng dụng Quản lý Kế hoạch Huấn luyện**

### 1.2. Phiên Bản
**Version:** 1.0.0

### 1.3. Ngày Tạo
**05/01/2026**

### 1.4. Người Tạo/Chủ Sở Hữu
**Victor Howard**

---

## 2. TỔNG QUAN SẢN PHẨM

### 2.1. Mô Tả Ngắn Gọn
**Ứng dụng hỗ trợ giảng viên quân đội quản lý các môn học và thời khóa biểu. Hỗ trợ theo dõi tiến độ giảng dạy, huấn luyện và hỗ trợ xây dựng kế hoạch giảng dạy. Hỗ trợ cung cấp tài liệu dạy mỗi ngày cho giảng viên.**

### 2.2. Vấn Đề Cần Giải Quyết
**Hiện tại việc sắp xếp thời khóa biểu và lịch trình giảng dạy đang được xử lý bằng tay, ứng dụng này được sinh ra để hỗ trợ việc này. Mỗi lần đi dạy, giảng viên sẽ phải tìm tài liệu liên quan, ứng dụng này cũng hỗ trợ cung cấp tài liệu liên quan đến môn học. Ngoài ra ứng dụng còn giúp theo dõi tiến độ giảng dạy, bài nào đã được dạy rồi, bài nào chưa.**

### 2.3. Giải Pháp
**Mỗi môn học sẽ có thứ tự danh sách các bài giảng cụ thể trong học đó, mỗi bài giảng sẽ có nội dung và thời lượng giảng dạy, và những điều này rất ít khi thay đổi. Ứng dụng hỗ trợ nhập lại nội dung của từng môn học hoặc import thông qua file Excel. Sau khi có các môn học, ứng dụng hỗ trợ tạo thành thời khóa biểu cho từng ngày, từng tuần, từng tháng theo yêu cầu được chỉ định. Ngoài ra trong mỗi bài học của mỗi môn học có thể lưu trữ các tài liệu liên quan.**

### 2.4. Giá Trị Cốt Lõi
**[Liệt kê 3-5 giá trị cốt lõi mà ứng dụng mang lại]**
- Hỗ trợ giảng viên thiết kế thời khóa biểu
- Theo dõi tiến trình dạy
- Hỗ trợ cung cấp tài liệu dạy mỗi ngày cho giảng viên

---

## 3. MỤC TIÊU VÀ PHẠM VI

### 3.1. Mục Tiêu Sản Phẩm
**[Liệt kê các mục tiêu chính]**
- Quản lý các môn học, trong các môn học có các bài giảng, trong bài giảng có các tài liệu liên quan
- Hỗ trợ lập thời khóa biểu
- Xuất thời khóa biểu

### 3.2. Phạm Vi (Scope)
#### 3.2.1. Trong Phạm Vi (In-Scope)
- Tính năng thiết kế thời khóa biểu
- Tính năng theo dõi tiến trình dạy
- Tính năng cung cấp tài liệu liên quan đến từng môn học

#### 3.2.2. Ngoài Phạm Vi (Out-of-Scope)
- 
- 
- 

### 3.3. Giả Định (Assumptions)
- Giả định sẵn 10 môn học, mỗi môn học có nhiều bài giảng, tài liệu liên quan đến mỗi bài giảng
- 
- 

---

## 4. ĐỐI TƯỢNG NGƯỜI DÙNG

### 4.1. User Personas
#### Persona 1: Nguyễn Văn A
- **Tuổi:** 25-35
- **Nghề nghiệp:** Bộ đội
- **Kỹ năng kỹ thuật:** Trung Bình
- **Mục tiêu:** Lập thời khóa biểu
- **Pain Points:** Mỗi nhiệm kỳ lại mất thời gian lập thời khóa biểu mới.
- **Use Cases:** Dùng tool để lập thời khóa biểu cho tất cả các môn học sao cho đáp ứng các điều kiện

#### Persona 2: Nguyễn Thị B
- **Tuổi:** 30-60
- **Nghề nghiệp:** Giảng viên
- **Kỹ năng kỹ thuật:** Thấp
- **Mục tiêu:** Theo dõi lịch giảng dạy và tham khảo tài liệu liên quan
- **Pain Points:** Trước đây cô đều phải xem hôm nay dạy bài nào và tự tìm tài liệu
- **Use Cases:** Dùng tool để xem lịch giảng dạy hôm nay, tuần này, tháng này.

---

## 5. TÍNH NĂNG CHỨC NĂNG (Functional Requirements)

### 5.1. Tính Năng Ưu Tiên Cao (Must Have - P0)
#### FR-001: Nhập môn học
- **Mô tả:** 
Một môn học bao gồm các thông tin sau: 
1. Tên môn học
2. Mã môn học
3. Các bài học trong môn học
Mỗi bài học bao gồm: Tên bài học, Thời lượng riêng của mỗi bài học và Tài liệu liên quan
4. Địa điểm học
5. Thời lượng mặc định của môn học
6. Yêu cầu: là các môn học cần phải học trước khi học môn này.
7. Phân loại
Một môn học được phân làm 3 loại: Chính trị, Quân sự, Hậu cần kỹ thuật.
Trong đấy:
Quân sự lại được phân làm 5 loại: Thông tin, Chiến thuật, Vũ khí, Điều lệnh, Thể lực.
Hậu cần kỹ thuật lại được phân làm 2 loại: Hậu cần, Kỹ thuật.
- **Input:** Cho người dùng nhập các thông tin cần thiết của một môn học hoặc nhập từ một file Excel. Có form mẫu Excel để người dùng tham khảo.
- **Output:** Môn học được lưu lại trên một file json trong hệ thống. 
- **Business Rules:** Một môn học có tối đa 500 bài học, có thể chọn thời lượng mặc định cho môn học, những bài học nào không có thời lượng riêng thì lấy thời lượng là thời lượng mặc định. Một môn học chỉ có Tên môn học là bắt buộc phải điền. Phần lưu lại thông tin môn học bao gồm 2 phần: đầu tiên là lưu vào một file json tổng hợp tất cả các thông tin cơ bản (tên môn học, địa điểm, thời lượng mặc định, phân loại) của môn học và thứ hai là lưu vào một file json riêng chi tiết của riêng môn học này, các bài học và các thông tin khác của môn học đó. Phần tài liệu liên quan được lưu vào một thư mục riêng, trong đó thư mục đó có các thư mục con là các môn học, trong mỗi thư mục môn học có các thư mục con là các bài học có tài liệu liên quan.

#### FR-002: Quản lý môn học
- **Mô tả:** Quản lý tất cả các môn học hiện có trong app. Trong trang này, người dùng có thể nhìn thấy danh sách các môn học hiện có. Từ trang này, người dùng có thể thêm, sửa, xóa môn học. 
- **Business Rules:** Nếu có quá nhiều môn học thì sẽ phân thành trang. Có thể sắp xếp thứ tự các môn học theo tên, theo mã, theo thời gian thêm vào hoặc theo phân loại. Thêm thanh search để tìm kiếm môn học, mỗi lần search sẽ hiển thị có bao nhiêu kết quả khớp. 

#### FR-003: Sửa môn học
- **Mô tả:** Sửa lại các thông tin của một môn học.
- **Input:** 
- **Output:** 
- **Business Rules:** 

#### FR-004: Xóa môn học
- **Mô tả:** Xóa thông tin của một môn học.
- **Input:** 
- **Output:** 
- **Business Rules:** 

#### FR-005: Tạo thời khóa biểu cho một tháng
- **Mô tả:** Tạo thời khóa biểu huấn luyện trong một tháng. Người dùng chọn ngày bắt đầu (ngày bắt đầu cần phải là ngày thứ Hai) và kết thúc (ngày kết thúc cần phải là ngày Chủ Nhật). Sau đó màn hình sẽ hiển thị 1 trang Thời khóa biểu cho tuần đầu tiên trong khoảng thời gian mà người dùng chọn (1 trang thời khóa biểu chưa có thông tin gì), người dùng sẽ vào đó để lên lịch cho từng ngày trong tuần, sau khi xong 1 tuần sẽ đến tuần tiếp theo. Ví dụ người dùng chọn thứ Hai, sau đó chọn phân loại môn muốn thêm (chính trị, quân sự hay Hậu cần kỹ thuật), sau đó cứ tiếp tục đi vào phân loại nhỏ hơn, cuối cùng lọc ra các môn phù hợp, chọn thêm môn học muốn thêm, chọn bài học cụ thể trong môn (chỉ những bài chưa được lên lịch, những bài học đã được dạy rồi hoặc đã lên lịch không gợi ý nữa), cứ thêm các bài học như thế sao cho phù hợp với yêu cầu.

- **Input:** 
- **Output:** Lưu lại thời khóa biểu dưới file json. Cách lưu cũng sử dụng 1 file json để lưu tổng quát các thông tin của các thời khóa biểu và 1 file json riêng để lưu chi tiết của 1 thời khóa biểu.
- **Business Rules:** 
Các yêu cầu khi tạo thời khóa biểu: Mỗi ngày kế hoạch học tập, huấn luyện cần phải đúng đủ 8 tiếng. Buổi sáng từ 7 giờ tới 11 giờ 30 phút, buổi chiều từ 12 giờ 30 phút tới 16  giờ. 6 ngày một tuần từ thứ Hai tới thứ Bảy. Ngoài ra sẽ có một số tiết học bất biến như: Tiết đầu tiên mỗi thứ Hai hàng tuần là Chào cờ (1 tiếng - 7 giờ - 8 giờ), từ 19h đến 21h mỗi thứ Tư hàng tuần sẽ Hành quân, Thứ Năm đầu tiên trong mỗi tháng sẽ có 1 tiết Văn hóa chính trị tinh thần (1 môn học). 
Nếu như sau khi người dùng thêm các môn học xong mà không đáp ứng được các yêu cầu nêu trên, tìm kiếm các giải pháp để đề xuất cho người dùng. Nếu chưa đủ 8 tiếng, đề xuất thêm một bài học cụ thể nào đó hoặc đổi một bài học sang bài học có thời lượng dài hơn trong cùng môn để đúng đủ 8 tiếng. Nếu thừa 8 tiếng, đề xuất đổi một bài học sang bài học có thời lượng ngắn hơn trong cùng môn để đúng đủ 8 tiếng.

#### FR-006: Quản lý thời khóa biểu
- **Mô tả:** Tương tự như quản lý môn học, có thêm sửa xóa các thời khóa biểu.
- **Input:** 
- **Output:** 
- **Business Rules:** 

#### FR-006: Xem thời khóa biểu
- **Mô tả:** Trình bày thời khóa biểu của một tuần mà người dùng chọn để hiển thị dưới dạng bảng biểu dễ nhìn, hỗ trợ tính năng xuất thành ảnh hoặc pdf hoặc file Excel.
- **Input:** 
- **Output:** 
- **Business Rules:** 

### 5.2. Tính Năng Ưu Tiên Trung Bình (Should Have - P1)
#### FR-007: Theo dõi tiến độ
- **Mô tả:** Hiển thị lịch sử giảng dạy và kế hoạch giảng dạy những ngày tiếp theo

### 5.3. Tính Năng Ưu Tiên Thấp (Nice to Have - P2)
#### FR-004: [Tên Tính Năng]
- **Mô tả:** 
- **User Story:** 
- **Acceptance Criteria:**
  - 
  - 

---

## 6. TÍNH NĂNG PHI CHỨC NĂNG (Non-Functional Requirements) 

### 6.1. Hiệu Năng (Performance)
- **Thời gian khởi động ứng dụng:** [ví dụ: < 3 giây]
- **Thời gian phản hồi UI:** [ví dụ: < 100ms]
- **Xử lý dữ liệu:** [ví dụ: Có thể xử lý 10,000 records trong < 5 giây]
- **Sử dụng bộ nhớ:** [ví dụ: < 200MB RAM khi idle]

### 6.2. Khả Năng Mở Rộng (Scalability)
- **Số lượng người dùng đồng thời:** 1 người dùng - single user app
- **Dung lượng dữ liệu:** [ví dụ: Hỗ trợ tối đa 10GB dữ liệu]

### 6.3. Bảo Mật (Security)
- **Xác thực:** Cần đăng nhập
- **Mã hóa dữ liệu:** [Có/Không]
- **Bảo vệ dữ liệu nhạy cảm:** 
- **Tuân thủ:** [GDPR, các quy định khác nếu có]

### 6.4. Khả Năng Sử Dụng (Usability)
- **Học cách sử dụng:** [ví dụ: < 10 phút]
- **Giao diện:** Modern, intuitive, responsive
- **Hỗ trợ đa ngôn ngữ:** Có - Tiếng Việt, Tiếng Anh (English)
- **Accessibility:** Tuân thủ WCAG 2.1 Level AA

### 6.5. Độ Tin Cậy (Reliability)
- **Uptime:** [ví dụ: 99.9%]
- **Xử lý lỗi:** Graceful error handling, không crash
- **Backup dữ liệu:** Tự động

### 6.6. Khả Năng Bảo Trì (Maintainability)
- **Code quality:** Tuân thủ PEP 8, có type hints
- **Documentation:** Code comments
- **Testing:** [Unit tests coverage > 80%]

### 6.7. Tương Thích (Compatibility)
- **Hệ điều hành:** Windows [ví dụ: Windows 10, 11]
- **Python version:** [ví dụ: Python 3.9+]
- **Screen resolution:** [ví dụ: Tối thiểu 1280x720]
- **Dependencies:** [Liệt kê các thư viện chính]

---

## 7. GIAO DIỆN NGƯỜI DÙNG (UI/UX)

### 7.1. Design Principles
- Thiết kế toát lên vẻ hiện đại
- Phong cách chủ đạo trắng đen
- 

### 7.2. Theme và Styling
- **Color Scheme:** Light [Light/Dark/Both]
- **Primary Colors:** 
- **Font:** 
- **Icon Style:** 

### 7.3. Layout và Navigation
- **Main Window:** 
- **Menu Structure:** 
- **Toolbar:** Có
- **Status Bar:** Có

### 7.4. Các Màn Hình Chính (Wireframes/Mockups)
#### Screen 1: [Tên màn hình]
- **Mô tả:** 
- **Các thành phần:** 
- **User flow:** 

#### Screen 2: [Tên màn hình]
- **Mô tả:** 
- **Các thành phần:** 
- **User flow:** 

### 7.5. Responsive Design
**[Mô tả cách ứng dụng thích ứng với các kích thước màn hình khác nhau]**

---

## 8. XỬ LÝ LỖI VÀ EDGE CASES

### 8.1. Error Handling
- **Network errors:** 
- **File I/O errors:** 
- **Data validation errors:** 
- **Unexpected errors:** 

### 8.2. Logging
- **Log levels:** DEBUG, INFO, WARNING, ERROR
- **Log location:** Ghi lại của mỗi ngày chạy ra một file riêng
- **Log rotation:** 

---

## . YÊU CẦU KỸ THUẬT

### 9.1. Technology Stack
- **Programming Language:** Python [version]
- **GUI Framework:** [PySide6/PyQt6]
- **Database:**  File JSON 
- **Packaging:** PyInstaller
- **Testing Framework:** [pytest/unittest]
- **Other Libraries:** 

---

**Document Version:** 1.0  
**Last Updated:** [09/01/2026]  
**Next Review Date:** [DD/MM/YYYY]