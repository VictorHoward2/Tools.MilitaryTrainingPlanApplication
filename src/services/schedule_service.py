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
        
        # Chào cờ - Every Monday 7:00-8:00
        if day_of_week == DayOfWeek.MONDAY:
            item = ScheduleItem(
                subject_id="",
                lesson_id="",
                subject_name="Chào cờ",
                lesson_name="Chào cờ",
                start_time=time(7, 0),
                end_time=time(8, 0)
            )
            day_schedule.items.append(item)
        
        # Hành quân - Every Wednesday 19:00-21:00
        if day_of_week == DayOfWeek.WEDNESDAY:
            item = ScheduleItem(
                subject_id="",
                lesson_id="",
                subject_name="Hành quân",
                lesson_name="Hành quân",
                start_time=time(19, 0),
                end_time=time(21, 0)
            )
            day_schedule.items.append(item)
        
        # Văn hóa chính trị tinh thần - First Thursday of month
        if day_of_week == DayOfWeek.THURSDAY and is_first_thursday_of_month(day_date):
            # Will be scheduled during normal hours
            pass
    
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
        for item in day.items:
            # Check overlap
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

