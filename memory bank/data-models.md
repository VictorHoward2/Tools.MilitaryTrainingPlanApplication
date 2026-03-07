# Mô hình dữ liệu

## Subject (`src/models/subject.py`)

| Thuộc tính | Kiểu | Mô tả |
|------------|------|--------|
| `name` | str | **Bắt buộc.** Tên môn học |
| `subject_id` | Optional[str] | ID (mặc định: `subject_{timestamp}`) |
| `code` | Optional[str] | Mã môn học |
| `lessons` | List[Lesson] | Danh sách bài học (tối đa 500) |
| `location` | Optional[str] | Địa điểm học |
| `default_duration` | Optional[float] | Thời lượng mặc định (giờ) cho bài không có duration |
| `prerequisites` | List[str] | Danh sách subject_id môn tiên quyết |
| `category_main` | Optional[str] | Chính trị / Quân sự / Hậu cần kỹ thuật |
| `category_sub` | Optional[str] | Phân loại phụ (Quân sự: Thông tin, Chiến thuật, Vũ khí, Điều lệnh, Thể lực; Hậu cần KT: Hậu cần, Kỹ thuật) |
| `created_at`, `updated_at` | Optional[datetime] | Thời gian tạo/cập nhật |

**Constants:** `SUBJECT_CATEGORY_MAIN`, `SUBJECT_CATEGORY_QUAN_SU`, `SUBJECT_CATEGORY_HAU_CAN_KY_THUAT` (dict key → label).

**Methods:** `get_lesson_duration(lesson)`, `to_dict()`, `from_dict()`, `to_summary_dict()`.

---

## Lesson (`src/models/lesson.py`)

| Thuộc tính | Kiểu | Mô tả |
|------------|------|--------|
| `name` | str | Tên bài học |
| `duration` | Optional[float] | Thời lượng (giờ); None thì dùng Subject.default_duration |
| `materials` | List[str] | Đường dẫn tài liệu |
| `lesson_id` | Optional[str] | ID (mặc định: `lesson_{timestamp}`) |
| `created_at`, `updated_at` | Optional[datetime] | |

**Methods:** `to_dict()`, `from_dict()`.

---

## Schedule (`src/models/schedule.py`)

### ScheduleItem
- `subject_id`, `lesson_id`, `subject_name`, `lesson_name`, `start_time`, `end_time`, `location`.

### DaySchedule
- `date` (date), `items` (List[ScheduleItem]), `is_completed` (bool), `selected_subject_ids`, `subject_time_slots` (subject_id → "HH:MM"), `subject_lesson_map` (subject_id → lesson_id).

### WeekSchedule
- `week_number`, `start_date` (Monday), `end_date` (Sunday), `days` (List[DaySchedule]).

### Schedule
- `schedule_id`, `name`, `start_date`, `end_date`, `weeks` (List[WeekSchedule]), `created_at`, `updated_at`.

**Enum:** `DayOfWeek` (MONDAY=0 … SUNDAY=6).

---

## User (`src/models/user.py`)

| Thuộc tính | Kiểu | Mô tả |
|------------|------|--------|
| `username` | str | Tên đăng nhập |
| `password_hash` | str | Mật khẩu băm SHA256 |
| `full_name` | Optional[str] | Tên hiển thị |
| `user_id` | Optional[str] | ID |
| `created_at`, `last_login` | Optional[datetime] | |

**Methods:** `User.hash_password(password)`, `verify_password(password)`, `to_dict()`, `from_dict()`.

---

## Lưu trữ file (FileService)

| Dữ liệu | Vị trí |
|---------|--------|
| Danh sách môn (summary) | `src/data/subjects/subjects_summary.json` |
| Chi tiết môn | `src/data/subjects/{subject_id}.json` |
| Danh sách TKB (summary) | `src/data/schedules/schedules_summary.json` |
| Chi tiết TKB | `src/data/schedules/{schedule_id}.json` |
| User | `src/data/users.json` |
| Tài liệu bài học | `src/data/materials/{subject_id}/{lesson_id}/` |
| Tiết cố định (tùy chọn) | `src/data/subjects/fixed_subjects.json` |
| Cài đặt (ngôn ngữ) | `src/data/settings.json` (qua Settings) |

Format `fixed_subjects.json`: danh sách object với `name`, `rule` ("daily"/"weekly"), `day_of_week`, `time_ranges` ([{start, end}]), `is_break`, `first_thursday_of_month`.
