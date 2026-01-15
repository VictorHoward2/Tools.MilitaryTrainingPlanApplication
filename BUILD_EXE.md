# Hướng dẫn Build File .exe

## Yêu cầu chuẩn bị

Đảm bảo bạn đã cài đặt tất cả dependencies:

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Phương pháp 1: Build bằng Spec File (Khuyến khích)

### Bước 1: Đảm bảo file `main.spec` có cấu hình đúng

File `main.spec` đã được cấu hình để:
- Bao gồm tất cả tài nguyên trong thư mục `resources/` (icons, translations)
- Bao gồm dữ liệu ban đầu trong thư mục `src/data/`
- Đặt tên file executable là `MilitaryTrainingPlan.exe`
- Sử dụng icon từ `resources/icons/logo.jpg`

### Bước 2: Chạy lệnh build

Mở terminal và chạy:

```bash
pyinstaller main.spec
```

### Bước 3: Kết quả

File .exe sẽ được tạo tại:
```
dist/MilitaryTrainingPlan.exe
```

Cấu trúc thư mục `dist/`:
```
dist/
├── MilitaryTrainingPlan.exe
├── resources/
│   ├── icons/
│   │   └── logo.jpg
│   └── translations/
│       ├── en.json
│       └── vi.json
├── src/
│   └── data/
│       └── (các file dữ liệu JSON)
└── (các file thư viện khác)
```

---

## Phương pháp 2: Build một File Duy Nhất (One-File)

Nếu bạn muốn đóng gói tất cả thành một file .exe duy nhất:

```bash
pyinstaller main.spec --onefile
```

**Ưu điểm:**
- Chỉ có 1 file .exe duy nhất
- Dễ dàng phân phối

**Nhược điểm:**
- File sẽ lớn hơn (80-150 MB tùy dependencies)
- Lần đầu chạy sẽ chậm hơn vì phải giải nén

---

## Phương pháp 3: Build thủ công không dùng spec file

Nếu không muốn dùng spec file:

```bash
pyinstaller --name="MilitaryTrainingPlan" ^
  --icon="resources/icons/logo.jpg" ^
  --add-data="resources/icons;resources/icons" ^
  --add-data="resources/translations;resources/translations" ^
  --add-data="src/data;src/data" ^
  --windowed ^
  --onedir ^
  src/main.py
```

---

## Xóa các Build Cũ

Trước khi build lại, bạn có thể xóa build cũ:

```bash
pyinstaller main.spec --clean
```

Hoặc xóa thủ công các thư mục:
```bash
rmdir /s build
rmdir /s dist
del main.spec.spec
```

---

## Chạy File .exe

Sau khi build thành công:

```bash
# Từ thư mục gốc dự án
dist/MilitaryTrainingPlan.exe

# Hoặc truy cập trực tiếp vào thư mục dist
cd dist
MilitaryTrainingPlan.exe
```

Lần đầu chạy, hãy đảm bảo đăng nhập với:
- **Username:** admin
- **Password:** admin

---

## Các Tùy Chọn PyInstaller Thường Dùng

| Tùy chọn | Ý nghĩa | Ví dụ |
|---------|---------|-------|
| `--onefile` | Tạo file .exe duy nhất | `pyinstaller --onefile main.spec` |
| `--onedir` | Tạo thư mục (mặc định) | `pyinstaller --onedir main.spec` |
| `--windowed` | Ẩn cửa sổ console | `pyinstaller --windowed main.spec` |
| `--icon` | Đặt icon | `pyinstaller --icon=logo.ico main.spec` |
| `--add-data` | Thêm dữ liệu | `--add-data="src/data;src/data"` |
| `--clean` | Xóa build cũ trước build | `pyinstaller --clean main.spec` |
| `-w` | Viết tắt của `--windowed` | `pyinstaller -w main.spec` |
| `-F` | Viết tắt của `--onefile` | `pyinstaller -F main.spec` |

---

## Khắc Phục Sự Cố

### 1. Lỗi: "main.spec not found"
**Giải pháp:** Đảm bảo bạn chạy lệnh từ thư mục gốc của dự án (nơi có `main.spec`)

### 2. Tài nguyên không được load (icon/translations không hiển thị)
**Giải pháp:**
- Kiểm tra file `main.spec` có các dòng `datas` đúng không
- Rebuild: `pyinstaller main.spec --clean`
- Xác nhận thư mục `resources/` có tồn tại

### 3. File .exe không chạy được
**Giải pháp:**
- Chạy từ command prompt để xem lỗi: `dist/MilitaryTrainingPlan.exe`
- Đảm bảo tất cả dependencies đã cài đặt: `pip install -r requirements.txt`
- Kiểm tra Windows Defender/Antivirus có chặn không

### 4. File .exe chạy chậm lần đầu
**Giải pháp:** Điều này là bình thường với PyInstaller, lần sau sẽ nhanh hơn

### 5. Lỗi "ModuleNotFoundError: No module named 'PySide6'"
**Giải pháp:** Cài đặt PySide6:
```bash
pip install PySide6>=6.6.0
```

---

## Tệp Chứa Dữ Liệu Người Dùng

Sau khi chạy .exe, dữ liệu sẽ được lưu tại:
```
dist/src/data/
├── users.json
├── subjects/
├── schedules/
└── materials/
```

---

## Phân Phối Ứng Dụng

Để phân phối ứng dụng:

1. **Nếu dùng --onedir:**
   - Copy toàn bộ thư mục `dist/MilitaryTrainingPlan/` hoặc `dist/`

2. **Nếu dùng --onefile:**
   - Copy file `dist/MilitaryTrainingPlan.exe`
   - Người dùng chạy file này trên máy Windows 10/11

---

## Mẹo Tối Ưu Hóa

- **Giảm kích thước file:** Dùng `--onefile` kết hợp với tối ưu hóa
- **Tăng tốc độ khởi động:** Dùng `--onedir` (nhanh hơn `--onefile`)
- **Thêm version:** Sửa trong `main.spec` hoặc dùng `--version-file`

---

Chúc bạn build thành công! 🎉
