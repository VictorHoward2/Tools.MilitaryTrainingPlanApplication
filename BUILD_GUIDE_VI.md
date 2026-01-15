# 🎉 HƯỚNG DẪN BUILD .EXE - HOÀN THÀNH

## 📌 Tóm Tắt Nhanh

Ứng dụng **Military Training Plan** đã được build thành công thành file .exe với tất cả tài nguyên!

```
📍 Vị trí File:    dist/MilitaryTrainingPlan/MilitaryTrainingPlan.exe
📦 Kích thước:     ~6.7 MB  
✅ Bao gồm:        Icons + Translations + Dữ liệu
🎯 Sẵn sàng:       Chạy trực tiếp trên Windows 10/11
```

---

## 🚀 CÁCH CHẠY NGAY (CÓ LIỀN)

### Bước 1: Chạy File .EXE
```bash
dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe
```

**Hoặc:** Dùng File Explorer, đi tới `dist` → `MilitaryTrainingPlan` → Double-click `MilitaryTrainingPlan.exe`

### Bước 2: Đăng Nhập
```
Username: admin
Password: admin
```

### ✅ Xong! Ứng dụng sẽ khởi động

---

## 📋 CÁC LỆNH BUILD THƯỜNG DÙNG

### 1️⃣ Build Thường (Thư Mục - Được Khuyến Khích)
```bash
pyinstaller main.spec
```
**Kết quả:** Thư mục `dist/MilitaryTrainingPlan/` đầy đủ (~68 MB)  
**Tốc độ:** Nhanh  
**Phân phối:** Zip toàn bộ thư mục

### 2️⃣ Build One-File (1 File Duy Nhất)
```bash
pyinstaller main.spec --onefile
```
**Kết quả:** File `dist/MilitaryTrainingPlan.exe` duy nhất (~150 MB)  
**Tốc độ:** Chậm hơn (giải nén mỗi lần)  
**Phân phối:** Gửi 1 file duy nhất

### 3️⃣ Build Sạch (Xóa Cache)
```bash
pyinstaller main.spec --clean
```
**Dùng khi:** Rebuild sau thay đổi lớn

### 4️⃣ Build Nhanh (Dùng Script)
**Windows Batch:**
```bash
build_exe.bat
```

**PowerShell:**
```bash
.\build_exe.ps1
```

---

## 📂 CẤU TRÚC THƯ MỤC

### Sau Build (Thư Mục Chính)
```
dist/MilitaryTrainingPlan/
├── MilitaryTrainingPlan.exe      ← File chính
├── _internal/                     (Dependencies)
├── resources/
│   ├── icons/
│   │   └── logo.jpg              ✅ Icon ứng dụng
│   └── translations/
│       ├── en.json               ✅ English
│       └── vi.json               ✅ Tiếng Việt  
└── src/data/                     ✅ Dữ liệu ứng dụng
    ├── users.json
    ├── subjects/
    └── schedules/
```

### Sau Build (One-File)
```
dist/
└── MilitaryTrainingPlan.exe      ← Tất cả trong 1 file
```

---

## 🔄 REBUILD SAU KHI CÓ THAY ĐỔI

Nếu bạn sửa code hoặc thêm tài nguyên:

```bash
# Xóa build cũ
pyinstaller main.spec --clean

# Build lại
pyinstaller main.spec
```

**Hoặc dùng script:**
```bash
build_exe.bat
```

---

## ⚙️ CẤU HÌNH BUILD (main.spec)

File `main.spec` đã được cấu hình để:
- ✅ Bao gồm `resources/icons/` (logo, icon)
- ✅ Bao gồm `resources/translations/` (en.json, vi.json)
- ✅ Bao gồm `src/data/` (dữ liệu ứng dụng)
- ✅ Ẩn console window (windowed mode)
- ✅ Đặt icon cho .exe
- ✅ Include hidden imports (PySide6)

Bạn có thể sửa file này nếu cần thêm/bớt resources.

---

## 💾 DỮ LIỆU & LOGS

### Lần Đầu Chạy
- Tài khoản `admin/admin` được tạo tự động
- Dữ liệu được lưu vào: `dist/MilitaryTrainingPlan/src/data/`

### Dữ Liệu Người Dùng
```
src/data/
├── users.json              (Tài khoản)
├── subjects/               (Môn học)
├── schedules/              (Thời khóa biểu)
└── materials/              (Tài liệu)
```

### Logs
```
logs/application.log        (Nhật ký ứng dụng)
```

---

## 🐛 GIẢI QUYẾT SỰ CỐ

### ❌ File .exe không chạy

**Kiểm tra:**
```bash
# Chạy từ cmd để xem lỗi chi tiết
cd dist\MilitaryTrainingPlan
MilitaryTrainingPlan.exe
```

**Nguyên nhân thường gặp:**
- Windows Defender chặn
- Thiếu Python runtime (nhưng .exe đã bao gồm)
- Đường dẫn tài nguyên không đúng

### ❌ Icon/Translations không hiển thị

**Giải pháp:**
```bash
# Rebuild sạch
pyinstaller main.spec --clean
```

### ❌ Ứng dụng chạy chậm

**Bình thường với:**
- Lần đầu chạy (giải nén dependencies)
- Build one-file (giải nén file lớn)

**Khắc phục:**
- Dùng build thường (--onedir) thay vì --onefile
- Xóa dữ liệu không cần trong `src/data/`

### ❌ Lỗi "ModuleNotFoundError"

**Giải pháp:**
```bash
# Cài lại dependencies
pip install -r requirements.txt
pip install pyinstaller

# Rebuild
pyinstaller main.spec --clean
```

---

## 📊 CÁC THÔNG SỐ BUILD

| Thông Số | Giá Trị |
|---------|--------|
| **PyInstaller Version** | 6.16.0 |
| **Python Version** | 3.9+ |
| **Framework** | PySide6 6.6.0+ |
| **OS Target** | Windows 10/11 |
| **File Size (--onedir)** | ~68 MB |
| **File Size (--onefile)** | ~150 MB |
| **Dependencies** | Đã include |
| **Console** | Hidden (windowed) |

---

## 📤 PHÂN PHỐI ỨNG DỤNG

### Cách 1: Gửi Toàn Bộ Thư Mục ⭐ Khuyến Khích
1. Zip thư mục `dist/MilitaryTrainingPlan/`
2. Gửi cho người dùng (~68 MB)
3. Extract và chạy `MilitaryTrainingPlan.exe`

**Ưu điểm:**
- ✅ Chạy nhanh
- ✅ Đơn giản

**Nhược điểm:**
- File khá lớn

### Cách 2: Gửi One-File
1. Build: `pyinstaller main.spec --onefile`
2. Gửi file `dist/MilitaryTrainingPlan.exe` (~150 MB)
3. Người dùng chạy file trực tiếp

**Ưu điểm:**
- ✅ Chỉ 1 file duy nhất
- ✅ Dễ phân phối

**Nhược điểm:**
- File lớn hơn
- Chạy chậm lần đầu

---

## 📚 TÀI LIỆU THÊM

| File | Nội Dung |
|------|---------|
| [BUILD_EXE.md](BUILD_EXE.md) | Hướng dẫn chi tiết |
| [QUICK_BUILD.md](QUICK_BUILD.md) | Build nhanh 3 bước |
| [BUILD_SUCCESS.md](BUILD_SUCCESS.md) | Tóm tắt build thành công |
| [RUN.md](RUN.md) | Hướng dẫn chạy ứng dụng |
| [README.md](README.md) | Thông tin chung |
| [main.spec](main.spec) | Cấu hình build |
| [build_exe.bat](build_exe.bat) | Script batch build |
| [build_exe.ps1](build_exe.ps1) | Script PowerShell build |

---

## ✅ CHECKLIST

- ✅ File .exe đã được build
- ✅ Resources đã được include (icons, translations)
- ✅ Dữ liệu đã được include
- ✅ main.spec đã được cấu hình đúng
- ✅ Scripts build đã được tạo (batch & PowerShell)
- ✅ Hướng dẫn đã được viết

---

## 🎯 BƯỚC TIẾP THEO

### Để Chạy Ứng Dụng:
```bash
dist\MilitaryTrainingPlan\MilitaryTrainingPlan.exe
```

### Để Rebuild:
```bash
build_exe.bat
```

### Để Phân Phối:
```bash
# Zip thư mục dist/MilitaryTrainingPlan/ và gửi
```

---

## 💡 MẸO & TRICKY

1. **Nếu muốn thêm file resources:**
   - Thêm vào thư mục `resources/`
   - Update `datas=[ ]` trong `main.spec`
   - Rebuild

2. **Nếu muốn tùy chỉnh icon:**
   - Thay file `resources/icons/logo.jpg`
   - Rebuild

3. **Nếu muốn tăng tốc độ:**
   - Dùng `--onedir` thay vì `--onefile`
   - Xóa dữ liệu không cần

4. **Nếu muốn giảm kích thước:**
   - Dùng `--onefile` kết hợp với optimize
   - Xóa dữ liệu test

---

## 🎉 HOÀN THÀNH!

Bạn đã sẵn sàng phân phối ứng dụng!

**Tóm tắt:**
- 📍 File: `dist/MilitaryTrainingPlan/MilitaryTrainingPlan.exe`
- 🎯 Chạy: Double-click file hoặc chạy lệnh trên
- 📝 Đăng nhập: admin / admin
- 🔄 Rebuild: `build_exe.bat`
- 📤 Phân phối: Zip thư mục `dist/MilitaryTrainingPlan/`

---

**Hỗ Trợ:**
- Xem các file BUILD_EXE.md, QUICK_BUILD.md nếu cần chi tiết
- Xem RUN.md để biết cách chạy ứng dụng
- Xem README.md để biết về dự án

**Chúc bạn thành công!** 🚀
