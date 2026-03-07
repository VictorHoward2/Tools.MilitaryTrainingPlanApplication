"""Schedule service for creating and managing schedules"""

from typing import List, Optional, Tuple, Dict, Set
from datetime import date, time, timedelta
from ..models.schedule import (
    Schedule, WeekSchedule, DaySchedule, ScheduleItem, DayOfWeek
)
from ..models.subject import Subject
from ..models.lesson import Lesson
from .file_service import FileService
from .subject_service import SubjectService
from ..utils.logger import setup_logger
from ..utils.date_utils import (
    get_week_start, get_week_end, get_weeks_in_range,
    is_first_thursday_of_month, time_duration, add_hours_to_time
)
from ..utils.season_schedule import (
    get_schedule_times_for_date,
    get_schedule_times_from_settings,
)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..config.settings import Settings

logger = setup_logger()

# Delimiter for diagnostic block: user can copy from DIAGNOSTIC_START to DIAGNOSTIC_END and paste when reporting errors
DIAGNOSTIC_START = "--- DIAGNOSTIC (copy from here to END and send when reporting errors) ---"
DIAGNOSTIC_END = "--- END DIAGNOSTIC ---"


def _log_build_week_diagnostic(
    schedule: "Schedule",
    week_num: int,
    errors: List[str],
    subject_service: "SubjectService",
) -> None:
    """Log a structured diagnostic block for build_week_items failures (easy to copy-paste for support)."""
    week = schedule.weeks[week_num - 1]
    lines = [
        DIAGNOSTIC_START,
        "context: build_week_items failed",
        f"schedule_id: {getattr(schedule, 'schedule_id', '')}",
        f"schedule_name: {getattr(schedule, 'name', '') or ''}",
        f"week_num: {week_num}",
        f"week_dates: {week.days[0].date.isoformat() if week.days else ''} .. {week.days[-1].date.isoformat() if week.days else ''}",
        "",
        "errors:",
    ]
    for e in errors:
        lines.append(f"  - {e}")
    lines.append("")
    for day in week.days:
        d = day.date.isoformat()
        lines.append(f"day {d}:")
        lines.append(f"  selected_subject_ids: {list(day.selected_subject_ids)}")
        for sid in day.selected_subject_ids:
            subj = subject_service.get_subject(sid) if subject_service else None
            name = subj.name if subj else sid
            lessons = day.get_lesson_ids(sid)
            slots = day.get_time_slots(sid)
            durations = day.subject_slot_durations.get(sid)
            lines.append(f"  subject {sid} ({name}):")
            lines.append(f"    lesson_ids: {lessons}")
            lines.append(f"    time_slots: {slots}")
            if durations:
                lines.append(f"    slot_durations: {durations}")
        fixed = [i for i in day.items if not i.subject_id and not i.lesson_id]
        if fixed:
            lines.append("  fixed_items:")
            for it in fixed:
                lines.append(f"    - {it.subject_name or '?'} {it.start_time.strftime('%H:%M')}-{it.end_time.strftime('%H:%M')}")
        lines.append("")
    lines.append(DIAGNOSTIC_END)
    logger.error("\n".join(lines))


def _fmt_time(t: Optional[time]) -> str:
    """Format time for diagnostic log."""
    return t.strftime("%H:%M") if t and hasattr(t, "strftime") else str(t)


def _log_validate_day_diagnostic(
    day: DaySchedule,
    total_hours: float,
    daily_total: float,
    suggestion: Optional[str],
    times: Dict,
) -> None:
    """Log a structured diagnostic block for validate_day_schedule failures (easy to copy-paste for support)."""
    lines = [
        DIAGNOSTIC_START,
        "context: validate_day_schedule failed (total hours mismatch)",
        f"date: {day.date.isoformat()}",
        f"daily_total_required: {daily_total}",
        f"total_hours_computed: {total_hours}",
        f"morning: {_fmt_time(times.get('morning_start'))} - {_fmt_time(times.get('morning_end'))}",
        f"afternoon: {_fmt_time(times.get('afternoon_start'))} - {_fmt_time(times.get('afternoon_end'))}",
        f"suggestion: {suggestion or ''}",
        "",
        "items (subject_name | lesson_name | start | end):",
    ]
    for it in day.items:
        lines.append(f"  {it.subject_name or '?'} | {it.lesson_name or '?'} | {it.start_time.strftime('%H:%M')} | {it.end_time.strftime('%H:%M')}")
    lines.append("")
    lines.append(DIAGNOSTIC_END)
    logger.warning("\n".join(lines))


class ScheduleService:
    """Service for schedule management"""
    
    def __init__(self, file_service: Optional[FileService] = None, 
                 subject_service: Optional[SubjectService] = None,
                 settings: Optional["Settings"] = None):
        """Initialize schedule service"""
        self.file_service = file_service or FileService()
        self.subject_service = subject_service or SubjectService(self.file_service)
        self.settings = settings
        self.fixed_subjects = self.file_service.load_fixed_subjects()
        self.break_subject_names = {"Nghỉ trưa"}
        if self.fixed_subjects:
            for subject in self.fixed_subjects:
                if subject.get("is_break"):
                    self.break_subject_names.add(subject.get("name", ""))
    
    def _get_schedule_times_for_date(self, day_date: date) -> dict:
        """Get morning/afternoon/break times for a date (based on season)."""
        if self.settings:
            return get_schedule_times_from_settings(day_date, self.settings)
        return get_schedule_times_for_date(day_date)
    
    def get_schedule_times_for_date(self, day_date: date) -> dict:
        """Public: get schedule times for a date (for UI)."""
        return self._get_schedule_times_for_date(day_date)
    
    def _get_fixed_subjects_for_date(self, day_date: date) -> List[Dict]:
        """Build fixed schedule items for a day with time ranges from season."""
        times = self._get_schedule_times_for_date(day_date)
        morning_start = times["morning_start"]
        morning_end = times["morning_end"]
        break_start = times["break_start"]
        break_end = times["break_end"]
        afternoon_start = times["afternoon_start"]
        afternoon_end = times["afternoon_end"]
        chao_co_end = add_hours_to_time(morning_start, 1.0)
        
        return [
            {
                "name": "Nghỉ trưa",
                "rule": "daily",
                "day_of_week": None,
                "first_thursday_of_month": False,
                "time_ranges": [{"start": break_start.strftime("%H:%M"), "end": break_end.strftime("%H:%M")}],
                "is_break": True,
            },
            {
                "name": "Chào cờ",
                "rule": "weekly",
                "day_of_week": "MONDAY",
                "first_thursday_of_month": False,
                "time_ranges": [{"start": morning_start.strftime("%H:%M"), "end": chao_co_end.strftime("%H:%M")}],
                "is_break": False,
            },
            {
                "name": "Văn hóa chính trị tinh thần",
                "rule": "weekly",
                "day_of_week": "THURSDAY",
                "first_thursday_of_month": True,
                "time_ranges": [
                    {"start": morning_start.strftime("%H:%M"), "end": morning_end.strftime("%H:%M")},
                    {"start": afternoon_start.strftime("%H:%M"), "end": afternoon_end.strftime("%H:%M")},
                ],
                "is_break": False,
            },
            {
                "name": "Hành quân",
                "rule": "weekly",
                "day_of_week": "WEDNESDAY",
                "first_thursday_of_month": False,
                "time_ranges": [{"start": "19:00", "end": "21:00"}],
                "is_break": False,
            },
        ]
    
    def create_schedule(self, start_date: date, end_date: date, name: Optional[str] = None) -> Schedule:
        """Create a new empty schedule with fixed items"""
        # Validate dates
        if not self._is_monday(start_date):
            raise ValueError("Start date must be Monday")
        if not self._is_sunday(end_date):
            raise ValueError("End date must be Sunday")
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        schedule = Schedule(
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create weeks
        weeks_data = get_weeks_in_range(start_date, end_date)
        for week_num, (week_start, week_end) in enumerate(weeks_data, 1):
            week = WeekSchedule(
                week_number=week_num,
                start_date=week_start,
                end_date=week_end
            )
            
            # Create days (Monday to Saturday)
            for day_offset in range(6):  # 0-5 for Monday-Saturday
                day_date = week_start + timedelta(days=day_offset)
                day_schedule = DaySchedule(date=day_date)
                
                # Add fixed schedule items
                self._add_fixed_items(day_schedule, day_date)
                
                week.days.append(day_schedule)
            
            schedule.weeks.append(week)
        
        return schedule
    
    def _is_monday(self, d: date) -> bool:
        """Check if date is Monday"""
        return d.weekday() == 0
    
    def _is_sunday(self, d: date) -> bool:
        """Check if date is Sunday"""
        return d.weekday() == 6
    
    def _add_fixed_items(self, day_schedule: DaySchedule, day_date: date):
        """Add fixed schedule items to a day (times depend on season for this date)."""
        day_of_week = DayOfWeek(day_date.weekday())

        for subject in self._get_fixed_subjects_for_date(day_date):
            if not self._should_add_fixed_subject(subject, day_date, day_of_week):
                continue

            for time_range in subject.get("time_ranges", []):
                start_time = self._parse_time_str(time_range.get("start"))
                end_time = self._parse_time_str(time_range.get("end"))
                if not start_time or not end_time:
                    continue

                item = ScheduleItem(
                    subject_id="",
                    lesson_id="",
                    subject_name=subject.get("name", "Môn học"),
                    lesson_name=subject.get("name", "Môn học"),
                    start_time=start_time,
                    end_time=end_time
                )
                self._insert_item_sorted(day_schedule.items, item)

    def _should_add_fixed_subject(self, subject: Dict, day_date: date, day_of_week: DayOfWeek) -> bool:
        """Check if a fixed subject should be added for a specific date."""
        rule = (subject.get("rule") or "weekly").lower()
        if rule != "daily":
            day_value = subject.get("day_of_week")
            if day_value is None:
                return False
            try:
                if isinstance(day_value, int):
                    expected_day = DayOfWeek(day_value)
                else:
                    expected_day = DayOfWeek[str(day_value)]
            except Exception:
                return False
            if expected_day != day_of_week:
                return False

        if subject.get("first_thursday_of_month") and not is_first_thursday_of_month(day_date):
            return False
        return True

    def _parse_time_str(self, value: Optional[str]) -> Optional[time]:
        """Parse time from HH:MM string."""
        if not value:
            return None
        try:
            return time.fromisoformat(value)
        except ValueError:
            return None

    def set_day_subjects(self, schedule: Schedule, week_num: int, day_index: int,
                         subject_ids: List[str]) -> Tuple[bool, Optional[str]]:
        """Set ordered subject list for a day"""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, "Số tuần không hợp lệ"
        week = schedule.weeks[week_num - 1]
        if day_index < 0 or day_index >= len(week.days):
            return False, "Chỉ số ngày không hợp lệ"

        seen = set()
        ordered = []
        for subject_id in subject_ids:
            if subject_id and subject_id not in seen:
                ordered.append(subject_id)
                seen.add(subject_id)

        day = week.days[day_index]
        day.selected_subject_ids = ordered
        day.subject_time_slots = {s: day.get_time_slots(s) for s in seen}
        day.subject_lesson_map = {s: day.get_lesson_ids(s) for s in seen}
        return True, None

    def set_day_subject_time(self, schedule: Schedule, week_num: int, day_index: int,
                             subject_id: str, start_time: Optional[time],
                             slot_index: int = 0) -> Tuple[bool, Optional[str]]:
        """Set start time for a subject slot in a day. If slot_index >= current list length, appends."""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, "Số tuần không hợp lệ"
        week = schedule.weeks[week_num - 1]
        if day_index < 0 or day_index >= len(week.days):
            return False, "Chỉ số ngày không hợp lệ"
        if not subject_id:
            return False, "Môn học không hợp lệ"

        day = week.days[day_index]
        if subject_id not in day.selected_subject_ids:
            return False, "Môn học chưa được chọn trong ngày"

        if start_time is None:
            day.subject_time_slots.pop(subject_id, None)
        else:
            slots = day.get_time_slots(subject_id)
            t = start_time.strftime("%H:%M")
            if slot_index < len(slots):
                slots[slot_index] = t
            else:
                slots.append(t)
            day.subject_time_slots[subject_id] = slots
        return True, None

    def set_day_subject_lesson(self, schedule: Schedule, week_num: int, day_index: int,
                               subject_id: str, lesson_id: str,
                               slot_index: int = 0) -> Tuple[bool, Optional[str]]:
        """Set lesson for a subject slot in a day. If slot_index >= current list length, appends."""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, "Số tuần không hợp lệ"
        week = schedule.weeks[week_num - 1]
        if day_index < 0 or day_index >= len(week.days):
            return False, "Chỉ số ngày không hợp lệ"
        if not subject_id:
            return False, "Môn học không hợp lệ"

        day = week.days[day_index]
        if subject_id not in day.selected_subject_ids:
            return False, "Môn học chưa được chọn trong ngày"

        if not lesson_id:
            day.subject_lesson_map.pop(subject_id, None)
        else:
            lessons = day.get_lesson_ids(subject_id)
            if slot_index < len(lessons):
                lessons[slot_index] = lesson_id
            else:
                lessons.append(lesson_id)
            day.subject_lesson_map[subject_id] = lessons
        return True, None

    def copy_week_subjects_and_times(self, schedule: Schedule, from_week_num: int,
                                     to_week_num: int) -> Tuple[bool, Optional[str]]:
        """Copy subject order and time slots from previous week. Lesson map is cleared."""
        if from_week_num < 1 or from_week_num > len(schedule.weeks):
            return False, "Số tuần nguồn không hợp lệ"
        if to_week_num < 1 or to_week_num > len(schedule.weeks):
            return False, "Số tuần đích không hợp lệ"

        from_week = schedule.weeks[from_week_num - 1]
        to_week = schedule.weeks[to_week_num - 1]

        for day_index, from_day in enumerate(from_week.days):
            if day_index >= len(to_week.days):
                break
            to_day = to_week.days[day_index]
            to_day.selected_subject_ids = list(from_day.selected_subject_ids)
            to_day.subject_time_slots = {k: list(v) for k, v in from_day.subject_time_slots.items()}
            to_day.subject_lesson_map = {}
        return True, None

    def build_week_items(
        self, schedule: Schedule, week_num: int
    ) -> Tuple[bool, Optional[str], List[str]]:
        """Build schedule items for a week from selected subjects and (lesson_id, time) lists per subject.
        Returns: (success, summary_for_ui, all_errors). When success, errors=[]."""
        if week_num < 1 or week_num > len(schedule.weeks):
            msg = "Số tuần không hợp lệ"
            logger.warning("build_week_items: %s (week_num=%s, schedule_id=%s)", msg, week_num, getattr(schedule, "schedule_id", None))
            return False, msg, [msg]

        week = schedule.weeks[week_num - 1]
        errors: List[str] = []
        schedule_label = schedule.name or schedule.schedule_id or "TKB"

        for day in week.days:
            fixed_items = [item for item in day.items if not item.subject_id and not item.lesson_id]
            new_items = list(fixed_items)
            day_label = day.date.isoformat()

            for subject_id in day.selected_subject_ids:
                subject = self.subject_service.get_subject(subject_id)
                if not subject:
                    err = f"Ngày {day_label}, môn (id={subject_id}): Không tìm thấy môn học trong hệ thống."
                    errors.append(err)
                    logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                    continue

                lesson_ids = day.get_lesson_ids(subject_id)
                time_slots = day.get_time_slots(subject_id)
                if len(lesson_ids) != len(time_slots):
                    err = f"Ngày {day_label}, môn \"{subject.name}\": Số bài học ({len(lesson_ids)}) và số giờ ({len(time_slots)}) không khớp. Cần chỉnh lại từng tiết cho đủ cặp bài–giờ."
                    errors.append(err)
                    logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                    continue
                if not lesson_ids:
                    err = f"Ngày {day_label}, môn \"{subject.name}\": Chưa chọn bài học nào. Hãy chọn ít nhất một bài (và giờ bắt đầu) cho môn này."
                    errors.append(err)
                    logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                    continue

                for slot_i, (lesson_id, time_str) in enumerate(zip(lesson_ids, time_slots)):
                    lesson = next((l for l in subject.lessons if l.lesson_id == lesson_id), None)
                    if not lesson:
                        err = f"Ngày {day_label}, môn \"{subject.name}\": Bài học (id={lesson_id}) không tồn tại trong môn. Có thể đã bị xóa hoặc đổi mã."
                        errors.append(err)
                        logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                        continue
                    if not time_str:
                        err = f"Ngày {day_label}, môn \"{subject.name}\", bài \"{lesson.name}\": Chưa chọn giờ bắt đầu. Hãy chọn giờ cho tiết này."
                        errors.append(err)
                        logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                        continue

                    start_time = time.fromisoformat(time_str)
                    slot_dur = day.get_slot_duration(subject_id, slot_i)
                    duration = (slot_dur if slot_dur is not None else subject.get_lesson_duration(lesson))
                    end_time = add_hours_to_time(start_time, duration)

                    conflict = self._check_time_conflict_items(new_items, start_time, end_time)
                    if conflict:
                        slot_range = f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
                        err = f"Ngày {day_label}, môn \"{subject.name}\", bài \"{lesson.name}\" (tiết {slot_range}): Trùng giờ với tiết khác: {conflict}. Hãy đổi giờ hoặc bỏ bớt tiết trùng."
                        errors.append(err)
                        logger.warning("[Kiểm tra TKB] Tuần %s, %s: %s", week_num, day_label, err)
                        continue

                    item = ScheduleItem(
                        subject_id=subject.subject_id,
                        lesson_id=lesson.lesson_id,
                        subject_name=subject.name,
                        lesson_name=lesson.name,
                        start_time=start_time,
                        end_time=end_time,
                        location=subject.location
                    )
                    self._insert_item_sorted(new_items, item)

            day.items = new_items

        if errors:
            full_text = "\n".join(errors)
            logger.error(
                "[Kiểm tra TKB] Tuần %s (%s): Phát hiện %s lỗi.\n%s",
                week_num, schedule_label, len(errors), full_text
            )
            _log_build_week_diagnostic(schedule, week_num, errors, self.subject_service)
            summary = f"Tuần {week_num}: phát hiện {len(errors)} lỗi. Chi tiết đã ghi trong file log (thư mục logs/).\n\nMột số lỗi:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                summary += f"\n... và {len(errors) - 5} lỗi khác (xem log)."
            return False, summary, errors

        from datetime import datetime
        schedule.updated_at = datetime.now()
        return True, None, []

    def validate_week_schedule(
        self, schedule: Schedule, week_num: int
    ) -> Tuple[bool, List[str]]:
        """Gom tất cả kiểm tra tuần vào một: thiếu thông tin, trùng giờ, không đủ tổng giờ.
        Returns: (is_valid, all_issues). Khi hợp lệ, issues=[]."""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, ["Số tuần không hợp lệ"]

        issues: List[str] = []
        success, _, build_errors = self.build_week_items(schedule, week_num)
        issues.extend(build_errors)

        week = schedule.weeks[week_num - 1]
        day_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
        for day_index, day in enumerate(week.days):
            is_valid, total_hours, suggestion = self.validate_day_schedule(day)
            if not is_valid and suggestion:
                day_name = day_names[day_index]
                day_date = day.date.isoformat()
                issues.append(f"{day_name} ({day_date}): {suggestion}")
                logger.warning(
                    "[Kiểm tra TKB] Tuần %s, %s: không đủ/đúng tổng giờ. total=%.2f. %s",
                    week_num, day_date, total_hours, suggestion
                )

        return len(issues) == 0, issues
    
    def add_lesson_to_day(self, schedule: Schedule, week_num: int, day_index: int,
                         subject: Subject, lesson: Lesson, 
                         start_time: time) -> Tuple[bool, Optional[str]]:
        """Add a lesson to a specific day"""
        try:
            if week_num < 1 or week_num > len(schedule.weeks):
                return False, "Số tuần không hợp lệ"
            
            week = schedule.weeks[week_num - 1]
            if day_index < 0 or day_index >= len(week.days):
                return False, "Chỉ số ngày không hợp lệ"
            
            day = week.days[day_index]
            
            # Calculate end time
            duration = subject.get_lesson_duration(lesson)
            end_time = add_hours_to_time(start_time, duration)
            
            # Check for conflicts
            conflict = self._check_time_conflict(day, start_time, end_time)
            if conflict:
                return False, f"Xung đột thời gian với: {conflict}"
            
            # Check if lesson already scheduled
            if self._is_lesson_scheduled(schedule, subject.subject_id, lesson.lesson_id):
                return False, "Bài học này đã được lên lịch"
            
            # Create schedule item
            item = ScheduleItem(
                subject_id=subject.subject_id,
                lesson_id=lesson.lesson_id,
                subject_name=subject.name,
                lesson_name=lesson.name,
                start_time=start_time,
                end_time=end_time,
                location=subject.location
            )
            
            # Insert in chronological order
            self._insert_item_sorted(day.items, item)
            
            # Update timestamp
            from datetime import datetime
            schedule.updated_at = datetime.now()
            
            logger.info(f"Added lesson '{lesson.name}' to {day.date}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error adding lesson to day: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def _check_time_conflict(self, day: DaySchedule, start: time, end: time) -> Optional[str]:
        """Check if time conflicts with existing items"""
        return self._check_time_conflict_items(day.items, start, end)
    
    def _check_time_conflict_items(self, items: List[ScheduleItem], start: time, end: time) -> Optional[str]:
        """Check if time conflicts with existing items list. Returns short description for UI/log."""
        for item in items:
            if not (end <= item.start_time or start >= item.end_time):
                slot = f"{item.start_time.strftime('%H:%M')}–{item.end_time.strftime('%H:%M')}"
                name = item.subject_name or "(Tiết cố định)"
                lesson = f" - {item.lesson_name}" if item.lesson_name else ""
                return f"{name}{lesson} ({slot})"
        return None
    
    def _insert_item_sorted(self, items: List[ScheduleItem], new_item: ScheduleItem):
        """Insert item in chronological order"""
        for i, item in enumerate(items):
            if new_item.start_time < item.start_time:
                items.insert(i, new_item)
                return
        items.append(new_item)
    
    def _is_lesson_scheduled(self, schedule: Schedule, subject_id: str, lesson_id: str) -> bool:
        """Check if a lesson is already scheduled"""
        for week in schedule.weeks:
            for day in week.days:
                for item in day.items:
                    if item.subject_id == subject_id and item.lesson_id == lesson_id:
                        return True
        return False

    def get_scheduled_lesson_ids_for_subject(self, schedule: Schedule, subject_id: str) -> Set[str]:
        """Collect all lesson_ids already assigned to this subject in the schedule (from map and items)."""
        return self.get_scheduled_lesson_ids_for_subject_in_weeks(
            schedule, subject_id, week_range=None
        )

    def get_scheduled_lesson_ids_for_subject_in_weeks_before(
        self, schedule: Schedule, subject_id: str, current_week_num: int
    ) -> Set[str]:
        """Chỉ lấy bài đã dạy ở các tuần TRƯỚC tuần hiện tại.
        Tuần 1: chưa có bài nào đã dạy. Tuần 2: bài trong tuần 1. Tuần 3: bài trong tuần 1+2."""
        if current_week_num <= 1:
            return set()
        return self.get_scheduled_lesson_ids_for_subject_in_weeks(
            schedule, subject_id, week_range=(1, current_week_num - 1)
        )

    def get_scheduled_lesson_ids_for_subject_in_weeks(
        self,
        schedule: Schedule,
        subject_id: str,
        week_range: Optional[Tuple[int, int]] = None,
    ) -> Set[str]:
        """Collect lesson_ids for subject. week_range=(start, end) 1-indexed inclusive; None = all weeks."""
        seen: Set[str] = set()
        weeks = schedule.weeks
        if week_range:
            start, end = week_range
            weeks = schedule.weeks[max(0, start - 1) : min(len(schedule.weeks), end)]
        for week in weeks:
            for day in week.days:
                for lesson_id in day.get_lesson_ids(subject_id):
                    if lesson_id:
                        seen.add(lesson_id)
                for item in day.items:
                    if item.subject_id == subject_id and item.lesson_id:
                        seen.add(item.lesson_id)
        return seen
    
    def get_available_lessons(self, schedule: Schedule, subject: Subject) -> List[Lesson]:
        """Get lessons that haven't been scheduled yet (uses subject_lesson_map + items)."""
        scheduled = self.get_scheduled_lesson_ids_for_subject(schedule, subject.subject_id)
        return [lesson for lesson in subject.lessons if lesson.lesson_id not in scheduled]

    @staticmethod
    def _subtract_time_range(
        outer_start: time, outer_end: time, remove_start: time, remove_end: time
    ) -> List[Tuple[time, time]]:
        """Return outer range minus remove range (0, 1 or 2 segments)."""
        if remove_end <= outer_start or remove_start >= outer_end:
            return [(outer_start, outer_end)]
        result: List[Tuple[time, time]] = []
        if outer_start < remove_start:
            result.append((outer_start, remove_start))
        if remove_end < outer_end:
            result.append((remove_end, outer_end))
        return result

    def _get_free_intervals_for_day(self, day: DaySchedule, day_date: date) -> List[Tuple[time, time]]:
        """Free intervals for placing subject lessons (work range minus fixed items). Do not merge across break."""
        times = self._get_schedule_times_for_date(day_date)
        morning_start = times["morning_start"]
        morning_end = times["morning_end"]
        afternoon_start = times["afternoon_start"]
        afternoon_end = times["afternoon_end"]

        work = [(morning_start, morning_end), (afternoon_start, afternoon_end)]
        fixed_ranges: List[Tuple[time, time]] = []
        for item in day.items:
            if not item.subject_id and not item.lesson_id:
                fixed_ranges.append((item.start_time, item.end_time))

        result: List[Tuple[time, time]] = []
        for (w_start, w_end) in work:
            current = [(w_start, w_end)]
            for (r_start, r_end) in fixed_ranges:
                if r_end <= w_start or r_start >= w_end:
                    continue
                new_current: List[Tuple[time, time]] = []
                for (a, b) in current:
                    new_current.extend(self._subtract_time_range(a, b, r_start, r_end))
                current = new_current
            result.extend(current)
        return result

    def _fill_day_times_and_lessons(
        self, day: DaySchedule, schedule: Schedule, week_num: int, day_index: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """Auto-fill subject_time_slots and subject_lesson_map for one day. Đã dạy = bài trong tuần trước + bài trong các ngày trước đó trong tuần này."""
        from ..utils.date_utils import time_duration as duration_hours

        free = self._get_free_intervals_for_day(day, day.date)
        if not free:
            return True, None
        subject_ids = list(day.selected_subject_ids)
        if not subject_ids:
            return True, None

        # Clear existing subject assignments for this day so we build from scratch (avoids old data causing conflicts)
        for s in subject_ids:
            day.subject_lesson_map.pop(s, None)
            day.subject_time_slots.pop(s, None)
            day.subject_slot_durations.pop(s, None)

        times = self._get_schedule_times_for_date(day.date)
        afternoon_start = times["afternoon_start"]

        scheduled_this_run: Set[str] = set()
        subject_idx = 0
        lesson_lists: Dict[str, List[str]] = {s: [] for s in subject_ids}
        time_lists: Dict[str, List[str]] = {s: [] for s in subject_ids}
        duration_lists: Dict[str, List[Optional[float]]] = {s: [] for s in subject_ids}
        # Ranges already used this day (including spanning afternoon part) so we don't double-book
        used_ranges: List[Tuple[time, time]] = []

        def advance_cursor_past_used(t: time) -> time:
            while True:
                overlap = next(
                    (end for (start, end) in used_ranges if start <= t < end),
                    None
                )
                if overlap is None:
                    return t
                t = overlap

        for interval_idx, (interval_start, interval_end) in enumerate(free):
            cursor = advance_cursor_past_used(interval_start)
            remaining_hours = duration_hours(cursor, interval_end)
            interval_is_afternoon = interval_start >= afternoon_start

            while remaining_hours > 0.01:
                tried = 0
                placed = False
                while tried < len(subject_ids):
                    subject_id = subject_ids[subject_idx % len(subject_ids)]
                    subject = self.subject_service.get_subject(subject_id)
                    subject_idx += 1
                    tried += 1
                    if not subject:
                        continue

                    already = set(
                        self.get_scheduled_lesson_ids_for_subject_in_weeks_before(
                            schedule, subject_id, week_num
                        )
                    )
                    # Thêm bài đã dạy trong các ngày trước đó của tuần này (vd: Thứ Hai đã học bài 1 thì Thứ Ba không dạy lại)
                    week = schedule.weeks[week_num - 1]
                    for prev_day in week.days[:day_index]:
                        for lid in prev_day.get_lesson_ids(subject_id):
                            if lid:
                                already.add(lid)
                        for item in prev_day.items:
                            if item.subject_id == subject_id and item.lesson_id:
                                already.add(item.lesson_id)
                    already.update(scheduled_this_run)
                    available = [l for l in subject.lessons if l.lesson_id not in already]
                    if not available:
                        continue

                    duration = subject.get_lesson_duration(available[0])
                    fits = duration <= remaining_hours + 0.01
                    if fits:
                        start_str = cursor.strftime("%H:%M")
                        end_t = add_hours_to_time(cursor, duration)
                        lesson_lists[subject_id].append(available[0].lesson_id)
                        time_lists[subject_id].append(start_str)
                        duration_lists[subject_id].append(None)
                        used_ranges.append((cursor, end_t))
                        scheduled_this_run.add(available[0].lesson_id)
                        cursor = end_t
                        remaining_hours = duration_hours(cursor, interval_end)
                        placed = True
                        break

                    shorter = [l for l in available if subject.get_lesson_duration(l) <= remaining_hours + 0.01]
                    if shorter:
                        best = max(shorter, key=lambda l: subject.get_lesson_duration(l))
                        start_str = cursor.strftime("%H:%M")
                        dur = subject.get_lesson_duration(best)
                        end_t = add_hours_to_time(cursor, dur)
                        lesson_lists[subject_id].append(best.lesson_id)
                        time_lists[subject_id].append(start_str)
                        duration_lists[subject_id].append(None)
                        used_ranges.append((cursor, end_t))
                        scheduled_this_run.add(best.lesson_id)
                        cursor = end_t
                        remaining_hours = duration_hours(cursor, interval_end)
                        placed = True
                        break

                    if not interval_is_afternoon and interval_idx + 1 < len(free):
                        next_start, next_end = free[interval_idx + 1]
                        if next_start >= afternoon_start:
                            part1 = remaining_hours
                            part2 = duration - part1
                            if part2 <= duration_hours(next_start, next_end) + 0.01:
                                start1 = cursor
                                end1 = add_hours_to_time(cursor, part1)
                                start2 = next_start
                                end2 = add_hours_to_time(next_start, part2)
                                lesson_lists[subject_id].append(available[0].lesson_id)
                                time_lists[subject_id].append(start1.strftime("%H:%M"))
                                duration_lists[subject_id].append(part1)
                                lesson_lists[subject_id].append(available[0].lesson_id)
                                time_lists[subject_id].append(start2.strftime("%H:%M"))
                                duration_lists[subject_id].append(part2)
                                used_ranges.append((start1, end1))
                                used_ranges.append((start2, end2))
                                scheduled_this_run.add(available[0].lesson_id)
                                remaining_hours = 0
                                placed = True
                                break
                    continue

                if not placed:
                    break

        for s in subject_ids:
            if lesson_lists[s]:
                day.subject_lesson_map[s] = lesson_lists[s]
                day.subject_time_slots[s] = time_lists[s]
                if any(d is not None for d in duration_lists[s]):
                    day.subject_slot_durations[s] = duration_lists[s]
        return True, None

    def auto_fill_week_times_and_lessons(
        self, schedule: Schedule, week_num: int
    ) -> Tuple[bool, Optional[str], List[Tuple[str, str, str]]]:
        """Auto-fill subject_time_slots and subject_lesson_map for all days in the week.
        Returns: (success, error, days_with_issues). days_with_issues = [(day_name, date, suggestion), ...] cho các ngày chưa đạt đủ tổng giờ."""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, "Số tuần không hợp lệ", []

        week = schedule.weeks[week_num - 1]
        for day_index, day in enumerate(week.days):
            if day.selected_subject_ids:
                self._fill_day_times_and_lessons(day, schedule, week_num, day_index)

        success, summary, _ = self.build_week_items(schedule, week_num)
        if not success:
            return False, summary, []

        day_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
        days_with_issues: List[Tuple[str, str, str]] = []
        for day_index, day in enumerate(week.days):
            if not day.selected_subject_ids:
                continue
            is_valid, total_hours, suggestion = self.validate_day_schedule(day)
            if not is_valid and suggestion:
                day_name = day_names[day_index]
                day_date = day.date.isoformat()
                days_with_issues.append((day_name, day_date, suggestion))

        return True, None, days_with_issues

    def validate_day_schedule(self, day: DaySchedule) -> Tuple[bool, float, Optional[str]]:
        """Validate if day schedule meets 8 hours requirement (using season times for this day).
        
        Returns: (is_valid, total_hours, suggestion_message)
        """
        times = self._get_schedule_times_for_date(day.date)
        morning_start = times["morning_start"]
        morning_end = times["morning_end"]
        afternoon_start = times["afternoon_start"]
        afternoon_end = times["afternoon_end"]
        daily_total = times["daily_total_hours"]
        
        total_hours = 0.0
        morning_hours = 0.0
        afternoon_hours = 0.0
        
        for item in day.items:
            if (
                not item.subject_id
                and not item.lesson_id
                and item.subject_name in self.break_subject_names
            ):
                continue
            if item.start_time < morning_start or item.end_time > afternoon_end:
                continue
            
            duration = time_duration(item.start_time, item.end_time)
            total_hours += duration
            if item.start_time >= morning_start and item.end_time <= morning_end:
                morning_hours += duration
            elif item.start_time >= afternoon_start and item.end_time <= afternoon_end:
                afternoon_hours += duration
        
        is_valid = abs(total_hours - daily_total) < 0.1

        suggestion = None
        if not is_valid:
            if total_hours < daily_total:
                shortage = daily_total - total_hours
                suggestion = (
                    f"Tổng giờ dạy hiện tại: {total_hours:.1f} giờ, yêu cầu: {daily_total:.1f} giờ. "
                    f"Thiếu {shortage:.1f} giờ."
                )
            else:
                excess = total_hours - daily_total
                suggestion = (
                    f"Tổng giờ dạy hiện tại: {total_hours:.1f} giờ, yêu cầu: {daily_total:.1f} giờ. "
                    f"Thừa {excess:.1f} giờ. Hãy đổi sang bài có thời lượng ngắn hơn hoặc bớt tiết."
                )
            logger.warning(
                "[Kiểm tra TKB] Ngày %s: không đủ/đúng giờ. total_hours=%.2f, daily_total=%.2f. %s",
                day.date.isoformat(), total_hours, daily_total, suggestion
            )
            _log_validate_day_diagnostic(day, total_hours, daily_total, suggestion, times)

        return is_valid, total_hours, suggestion
    
    def suggest_adjustments(self, day: DaySchedule, subject: Subject) -> List[Dict]:
        """Suggest lesson adjustments to meet 8 hours requirement"""
        suggestions = []
        is_valid, total_hours, _ = self.validate_day_schedule(day)
        
        if is_valid:
            return suggestions
        
        times = self._get_schedule_times_for_date(day.date)
        daily_total = times["daily_total_hours"]
        shortage = daily_total - total_hours
        
        # Find lessons in the day from this subject
        subject_items = [item for item in day.items 
                        if item.subject_id == subject.subject_id]
        
        if shortage > 0:
            # Need longer lessons
            for item in subject_items:
                current_lesson = next(
                    (l for l in subject.lessons if l.lesson_id == item.lesson_id),
                    None
                )
                if not current_lesson:
                    continue
                
                # Find longer lessons in same subject
                for lesson in subject.lessons:
                    if lesson.lesson_id == item.lesson_id:
                        continue
                    
                    lesson_duration = subject.get_lesson_duration(lesson)
                    current_duration = subject.get_lesson_duration(current_lesson)
                    
                    if lesson_duration > current_duration:
                        diff = lesson_duration - current_duration
                        if diff <= shortage + 0.5:  # Within reasonable range
                            suggestions.append({
                                "type": "replace",
                                "current_lesson": current_lesson.name,
                                "suggested_lesson": lesson.name,
                                "reason": f"Tăng thời lượng thêm {diff:.1f} giờ"
                            })
        else:
            # Need shorter lessons
            excess = -shortage
            for item in subject_items:
                current_lesson = next(
                    (l for l in subject.lessons if l.lesson_id == item.lesson_id),
                    None
                )
                if not current_lesson:
                    continue
                
                # Find shorter lessons in same subject
                for lesson in subject.lessons:
                    if lesson.lesson_id == item.lesson_id:
                        continue
                    
                    lesson_duration = subject.get_lesson_duration(lesson)
                    current_duration = subject.get_lesson_duration(current_lesson)
                    
                    if lesson_duration < current_duration:
                        diff = current_duration - lesson_duration
                        if diff <= excess + 0.5:
                            suggestions.append({
                                "type": "replace",
                                "current_lesson": current_lesson.name,
                                "suggested_lesson": lesson.name,
                                "reason": f"Giảm thời lượng {diff:.1f} giờ"
                            })
        
        return suggestions
    
    def save_schedule(self, schedule: Schedule) -> Tuple[bool, Optional[str]]:
        """Save schedule"""
        try:
            if self.file_service.save_schedule(schedule):
                logger.info(f"Saved schedule: {schedule.schedule_id}")
                return True, None
            else:
                return False, "Lỗi khi lưu thời khóa biểu"
        except Exception as e:
            logger.error(f"Error saving schedule: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def load_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Load schedule by ID"""
        return self.file_service.load_schedule(schedule_id)
    
    def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        return self.file_service.load_all_schedules()
    
    def delete_schedule(self, schedule_id: str) -> Tuple[bool, Optional[str]]:
        """Delete schedule"""
        try:
            if self.file_service.delete_schedule(schedule_id):
                logger.info(f"Deleted schedule: {schedule_id}")
                return True, None
            else:
                return False, "Lỗi khi xóa thời khóa biểu"
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return False, f"Lỗi: {str(e)}"

