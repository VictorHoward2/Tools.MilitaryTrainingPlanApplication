# Hướng Dẫn Build File .EXE - TÓM TẮT NHANH

## ⚡ Cách Nhanh Nhất (3 Bước)

### Bước 1: Cài PyInstaller
```bash
pip install pyinstaller
```

### Bước 2: Chạy Build
Chọn MỘT trong các cách sau:

#### 🟢 Cách A: Chạy script batch (Windows - Dễ nhất)
```bash
build_exe.bat
```

#### 🟢 Cách B: Chạy script PowerShell
```bash
.\build_exe.ps1
```

#### 🟢 Cách C: Chạy lệnh trực tiếp
```bash
pyinstaller main.spec
```

### Bước 3: Chạy File .EXE
```bash
dist/MilitaryTrainingPlan.exe
```

---

## 📦 Kết Quả Build

Sau khi chạy build, bạn sẽ có:

```
dist/
├── MilitaryTrainingPlan.exe      ✅ File chính
├── resources/
│   ├── icons/logo.jpg            ✅ Icon
│   └── translations/             ✅ Ngôn ngữ
├── src/data/                     ✅ Dữ liệu
└── (các file thư viện khác)
```

---

## 🔑 Thông Tin Đăng Nhập

Lần đầu chạy:
- **Username:** admin
- **Password:** admin

---

## 💾 Build Dạng One-File (Tất cả trong 1 file)

Nếu muốn tất cả trong 1 file .exe duy nhất:

```bash
build_exe.bat onefile
```

Hoặc:

```bash
.\build_exe.ps1 -onefile
```

Hoặc:

```bash
pyinstaller main.spec --onefile
```

**Ưu điểm:** Chỉ 1 file duy nhất, dễ phân phối  
**Nhược điểm:** File lớn hơn (~100-150 MB)

---

## ❌ Nếu Gặp Lỗi

### PyInstaller chưa cài
```bash
pip install pyinstaller
```

### Lỗi "main.spec not found"
- Chắc chắn chạy script từ thư mục gốc của dự án
- Thử lại: `cd d:\Projects\Tools\MilitaryTrainingPlanApplication`

### Icon/Translations không hiển thị
- Rebuild: `pyinstaller main.spec --clean`

### File .exe không chạy
- Cài đủ dependencies: `pip install -r requirements.txt`

---

## 📚 Chi Tiết Hơn

Xem file [BUILD_EXE.md](BUILD_EXE.md) để hướng dẫn chi tiết.

---

**Chúc bạn build thành công!** 🎉
