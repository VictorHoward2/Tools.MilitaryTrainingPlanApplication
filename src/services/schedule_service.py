"""Schedule service for creating and managing schedules"""

from typing import List, Optional, Tuple, Dict
from datetime import date, time, timedelta
from ..models.schedule import (
    Schedule, WeekSchedule, DaySchedule, ScheduleItem, DayOfWeek
)
from ..models.subject import Subject
from ..models.lesson import Lesson
from .file_service import FileService
from .subject_service import SubjectService
from ..utils.logger import setup_logger
from ..utils.constants import (
    SCHEDULE_MORNING_START, SCHEDULE_MORNING_END,
    SCHEDULE_AFTERNOON_START, SCHEDULE_AFTERNOON_END,
    DAILY_TOTAL_HOURS, MORNING_HOURS, AFTERNOON_HOURS,
    FIXED_SCHEDULE_ITEMS
)
from ..utils.date_utils import (
    get_week_start, get_week_end, get_weeks_in_range,
    is_first_thursday_of_month, time_duration, add_hours_to_time
)

logger = setup_logger()


class ScheduleService:
    """Service for schedule management"""
    
    def __init__(self, file_service: Optional[FileService] = None, 
                 subject_service: Optional[SubjectService] = None):
        """Initialize schedule service"""
        self.file_service = file_service or FileService()
        self.subject_service = subject_service or SubjectService(self.file_service)
        self.fixed_subjects = self.file_service.load_fixed_subjects()
        self.break_subject_names = {
            subject.get("name")
            for subject in self.fixed_subjects
            if subject.get("is_break")
        }
        if not self.fixed_subjects and not self.break_subject_names:
            self.break_subject_names = {
                data.get("name")
                for data in FIXED_SCHEDULE_ITEMS.values()
                if data.get("is_break")
            }
    
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
        """Add fixed schedule items to a day"""
        day_of_week = DayOfWeek(day_date.weekday())

        for subject in self._get_fixed_subjects():
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

    def _get_fixed_subjects(self) -> List[Dict]:
        """Get fixed subjects configuration (from file or fallback constants)."""
        if self.fixed_subjects:
            return self.fixed_subjects

        fallback_subjects = []
        for data in FIXED_SCHEDULE_ITEMS.values():
            day = data.get("day")
            time_ranges = data.get("time_ranges")
            if not time_ranges and data.get("start_time") and data.get("end_time"):
                time_ranges = [
                    {
                        "start": data["start_time"].strftime("%H:%M"),
                        "end": data["end_time"].strftime("%H:%M")
                    }
                ]
            elif time_ranges:
                time_ranges = [
                    {
                        "start": tr["start"].strftime("%H:%M"),
                        "end": tr["end"].strftime("%H:%M")
                    }
                    for tr in time_ranges
                ]

            fallback_subjects.append({
                "name": data.get("name", "Môn học"),
                "rule": "daily" if data.get("daily") else "weekly",
                "day_of_week": day.name if day else None,
                "first_thursday_of_month": data.get("first_thursday_of_month", False),
                "time_ranges": time_ranges or [],
                "is_break": data.get("is_break", False)
            })

        return fallback_subjects

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
        day.subject_time_slots = {
            subject_id: time_str
            for subject_id, time_str in day.subject_time_slots.items()
            if subject_id in seen
        }
        day.subject_lesson_map = {
            subject_id: lesson_id
            for subject_id, lesson_id in day.subject_lesson_map.items()
            if subject_id in seen
        }
        return True, None

    def set_day_subject_time(self, schedule: Schedule, week_num: int, day_index: int,
                             subject_id: str, start_time: Optional[time]) -> Tuple[bool, Optional[str]]:
        """Set start time for a subject in a day"""
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
            day.subject_time_slots[subject_id] = start_time.strftime("%H:%M")
        return True, None

    def set_day_subject_lesson(self, schedule: Schedule, week_num: int, day_index: int,
                               subject_id: str, lesson_id: str) -> Tuple[bool, Optional[str]]:
        """Set lesson for a subject in a day"""
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
            day.subject_lesson_map[subject_id] = lesson_id
        return True, None

    def copy_week_subjects_and_times(self, schedule: Schedule, from_week_num: int,
                                     to_week_num: int) -> Tuple[bool, Optional[str]]:
        """Copy subject order and time slots from previous week"""
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
            to_day.subject_time_slots = dict(from_day.subject_time_slots)
            to_day.subject_lesson_map = {}
        return True, None

    def build_week_items(self, schedule: Schedule, week_num: int) -> Tuple[bool, Optional[str]]:
        """Build schedule items for a week based on selected subjects, times, and lessons"""
        if week_num < 1 or week_num > len(schedule.weeks):
            return False, "Số tuần không hợp lệ"

        week = schedule.weeks[week_num - 1]
        errors = []

        for day in week.days:
            fixed_items = [item for item in day.items if not item.subject_id and not item.lesson_id]
            new_items = list(fixed_items)

            for subject_id in day.selected_subject_ids:
                subject = self.subject_service.get_subject(subject_id)
                if not subject:
                    errors.append(f"{day.date}: Không tìm thấy môn học")
                    continue

                lesson_id = day.subject_lesson_map.get(subject_id)
                if not lesson_id:
                    errors.append(f"{day.date}: Chưa chọn bài học cho môn {subject.name}")
                    continue

                lesson = next((l for l in subject.lessons if l.lesson_id == lesson_id), None)
                if not lesson:
                    errors.append(f"{day.date}: Bài học không hợp lệ cho môn {subject.name}")
                    continue

                time_str = day.subject_time_slots.get(subject_id)
                if not time_str:
                    errors.append(f"{day.date}: Chưa chọn giờ cho môn {subject.name}")
                    continue

                start_time = time.fromisoformat(time_str)
                duration = subject.get_lesson_duration(lesson)
                end_time = add_hours_to_time(start_time, duration)

                conflict = self._check_time_conflict_items(new_items, start_time, end_time)
                if conflict:
                    errors.append(f"{day.date}: Xung đột thời gian với {conflict}")
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
            return False, "\n".join(errors)

        from datetime import datetime
        schedule.updated_at = datetime.now()
        return True, None
    
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
        """Check if time conflicts with existing items list"""
        for item in items:
            if not (end <= item.start_time or start >= item.end_time):
                return f"{item.subject_name} - {item.lesson_name}"
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
    
    def get_available_lessons(self, schedule: Schedule, subject: Subject) -> List[Lesson]:
        """Get lessons that haven't been scheduled yet"""
        scheduled_lesson_ids = set()
        for week in schedule.weeks:
            for day in week.days:
                for item in day.items:
                    if item.subject_id == subject.subject_id:
                        scheduled_lesson_ids.add(item.lesson_id)
        
        return [lesson for lesson in subject.lessons 
                if lesson.lesson_id not in scheduled_lesson_ids]
    
    def validate_day_schedule(self, day: DaySchedule) -> Tuple[bool, float, Optional[str]]:
        """Validate if day schedule meets 8 hours requirement
        
        Returns: (is_valid, total_hours, suggestion_message)
        """
        total_hours = 0.0
        
        # Calculate morning hours (7:00 - 11:30)
        morning_hours = 0.0
        afternoon_hours = 0.0
        
        for item in day.items:
            if (
                not item.subject_id
                and not item.lesson_id
                and item.subject_name in self.break_subject_names
            ):
                continue
            # Skip fixed items outside normal hours
            if item.start_time < SCHEDULE_MORNING_START or item.end_time > SCHEDULE_AFTERNOON_END:
                continue
            
            duration = time_duration(item.start_time, item.end_time)
            total_hours += duration
            
            # Check if in morning or afternoon
            if item.start_time >= SCHEDULE_MORNING_START and item.end_time <= SCHEDULE_MORNING_END:
                morning_hours += duration
            elif item.start_time >= SCHEDULE_AFTERNOON_START and item.end_time <= SCHEDULE_AFTERNOON_END:
                afternoon_hours += duration
        
        is_valid = abs(total_hours - DAILY_TOTAL_HOURS) < 0.1  # Allow small tolerance
        
        suggestion = None
        if not is_valid:
            if total_hours < DAILY_TOTAL_HOURS:
                shortage = DAILY_TOTAL_HOURS - total_hours
                suggestion = f"Thiếu {shortage:.1f} giờ. Đề xuất thêm bài học hoặc đổi sang bài có thời lượng dài hơn."
            else:
                excess = total_hours - DAILY_TOTAL_HOURS
                suggestion = f"Thừa {excess:.1f} giờ. Đề xuất đổi sang bài có thời lượng ngắn hơn."
        
        return is_valid, total_hours, suggestion
    
    def suggest_adjustments(self, day: DaySchedule, subject: Subject) -> List[Dict]:
        """Suggest lesson adjustments to meet 8 hours requirement"""
        suggestions = []
        is_valid, total_hours, _ = self.validate_day_schedule(day)
        
        if is_valid:
            return suggestions
        
        shortage = DAILY_TOTAL_HOURS - total_hours
        
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

