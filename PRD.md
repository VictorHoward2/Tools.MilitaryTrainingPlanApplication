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
- **Business Rules:** Có thể sắp xếp thứ tự các môn học theo tên, theo mã, theo thời gian thêm vào hoặc theo phân loại. Có thanh search để tìm kiếm môn học (theo tên hoặc mã), mỗi lần search hiển thị số kết quả khớp. *(Hiện tại app hiển thị toàn bộ kết quả trong một bảng, chưa có phân trang; có thể bổ sung phân trang khi số lượng môn học rất lớn.)* 

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

#### FR-005: Tạo kế hoạch huấn luyện (thời khóa biểu)
- **Mô tả:** Tạo kế hoạch huấn luyện (thời khóa biểu) cho một khoảng thời gian bất kỳ. Người dùng chọn ngày bắt đầu (phải là Thứ Hai) và ngày kết thúc (phải là Chủ Nhật), có thể một hoặc nhiều tuần/tháng. Sau khi tạo, màn hình hiển thị từng tuần trong khoảng đã chọn; người dùng lên lịch cho từng tuần theo **3 bước**: (1) **Chọn môn học theo từng ngày trong tuần**: bảng 6 cột (Thứ Hai–Thứ Bảy), mỗi cột một ngày; khi thêm môn có thể lọc theo phân loại chính (Chính trị, Quân sự, Hậu cần kỹ thuật) và phân loại phụ, rồi chọn môn; có thể “Xếp môn học giống tuần trước”. (2) **Sắp xếp thứ tự môn học và chọn giờ** cho từng môn trong từng ngày (Lên/Xuống). (3) **Chọn bài học và giờ học** cho từng môn; hệ thống gợi ý bài chưa lên lịch, chọn giờ bắt đầu dự kiến. Có nút **Validate** để kiểm tra tuần có đủ 8 tiếng/ngày hay không và nhận gợi ý điều chỉnh. **Lưu thời khóa biểu** sẽ build toàn bộ các tuần và ghi file.
- **Input:** Ngày bắt đầu (Thứ Hai), ngày kết thúc (Chủ Nhật).
- **Output:** Lưu thời khóa biểu dưới file JSON: 1 file tổng quát (danh sách TKB) và 1 file riêng cho từng TKB (chi tiết theo tuần/ngày).
- **Business Rules:** Khung giờ trong ngày (sáng/chiều/nghỉ trưa) và tổng số tiếng/ngày có thể **chỉnh trong Cài đặt** theo ý người dùng (theo mùa hè/mùa đông); **đánh giá thời khóa biểu (Validate) phải theo đúng cài đặt** (mỗi ngày đủ đúng số tiếng theo khung đã cấu hình). Mặc định: 8 tiếng/ngày (sáng 7:00–11:30, chiều 12:30–16:00). 6 ngày/tuần (Thứ Hai–Thứ Bảy). Tiết cố định: Chào cờ mỗi Thứ Hai (đầu giờ sáng); Nghỉ trưa (theo khung Cài đặt); Hành quân mỗi Thứ Tư 19:00–21:00; Thứ Năm đầu tiên mỗi tháng có tiết Văn hóa chính trị tinh thần (cả ngày). Nếu chưa đủ hoặc thừa số tiếng theo cài đặt, hệ thống đề xuất điều chỉnh (đổi bài có thời lượng dài hơn/ngắn hơn trong cùng môn).

#### FR-006: Quản lý thời khóa biểu
- **Mô tả:** Quản lý danh sách thời khóa biểu (xem danh sách, xóa TKB). *(Hiện tại app: backend hỗ trợ xóa TKB qua service; giao diện màn hình “Xem thời khóa biểu” chưa có nút xóa TKB—có thể bổ sung sau. “Sửa” TKB thực tế là tạo lại hoặc mở lại từ màn hình tạo kế hoạch nếu tính năng mở TKB có sẵn được bổ sung.)*
- **Input:** —
- **Output:** —
- **Business Rules:** —

#### FR-007: Xem thời khóa biểu
- **Mô tả:** Chọn một thời khóa biểu và một tuần để hiển thị dưới dạng bảng (6 cột Thứ Hai–Thứ Bảy). Hỗ trợ xuất: PDF (toàn bộ các tuần), file Excel (toàn bộ TKB), ảnh (chỉ tuần đang chọn).
- **Input:** Chọn TKB từ dropdown, chọn tuần.
- **Output:** Bảng xem trên màn hình; file PDF/Excel/ảnh khi người dùng chọn xuất.
- **Business Rules:** —

### 5.2. Tính Năng Ưu Tiên Trung Bình (Should Have - P1)
#### FR-008: Theo dõi tiến độ
- **Mô tả:** Chọn một thời khóa biểu, xem lịch theo ngày: (1) **Lịch (calendar)** và **Hôm nay**—hiển thị nội dung lịch hôm nay, nút “Đánh dấu đã hoàn thành” cho ngày hiện tại; (2) **Bảng tiến độ** liệt kê các tiết theo ngày với trạng thái Đã hoàn thành / Chưa hoàn thành, có lọc hiển thị (Đã hoàn thành, Chưa hoàn thành); (3) **Đánh dấu tất cả ngày quá khứ** là đã hoàn thành; (4) Click một ngày trên lịch để xem chi tiết lịch ngày đó.

### 5.3. Tính Năng Ưu Tiên Thấp (Nice to Have - P2)
#### FR-009: [Tên Tính Năng]
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
- **Cài đặt:** Màn hình Cài đặt cho phép chỉnh **khung giờ trong ngày** (giờ bắt đầu/kết thúc buổi sáng, nghỉ trưa, buổi chiều) theo mùa hè/mùa đông. **Quy định đánh giá thời khóa biểu** (Validate, số tiếng/ngày) **theo đúng cài đặt** (tổng số tiếng = sáng + chiều theo khung đã cấu hình).

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

## 9. YÊU CẦU KỸ THUẬT

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