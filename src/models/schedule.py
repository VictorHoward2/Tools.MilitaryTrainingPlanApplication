"""Schedule model"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union
from datetime import datetime, date, time
from enum import Enum


class DayOfWeek(Enum):
    """Day of week enumeration"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class ScheduleItem:
    """Represents a single scheduled lesson"""
    
    subject_id: str
    lesson_id: str
    subject_name: str
    lesson_name: str
    start_time: time
    end_time: time
    location: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "subject_id": self.subject_id,
            "lesson_id": self.lesson_id,
            "subject_name": self.subject_name,
            "lesson_name": self.lesson_name,
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "location": self.location,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScheduleItem":
        """Create from dictionary"""
        return cls(
            subject_id=data["subject_id"],
            lesson_id=data["lesson_id"],
            subject_name=data["subject_name"],
            lesson_name=data["lesson_name"],
            start_time=time.fromisoformat(data["start_time"]),
            end_time=time.fromisoformat(data["end_time"]),
            location=data.get("location"),
        )


def _normalize_to_list(value: Union[str, List[str], None]) -> List[str]:
    """Convert legacy single value to list for multi-lesson-per-day support."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return list(value) if value else []


def _normalize_duration_list(value: Optional[List], length: int) -> List[Optional[float]]:
    """Return list of optional float (duration in hours per slot). None = use full lesson duration."""
    if value is None or not isinstance(value, list):
        return [None] * length
    return list(value) + [None] * (length - len(value)) if len(value) < length else value[:length]


@dataclass
class DaySchedule:
    """Represents schedule for a single day.
    subject_lesson_map: subject_id -> list of lesson_id (one or more per subject).
    subject_time_slots: subject_id -> list of "HH:MM" start times (same order as lessons).
    subject_slot_durations: optional subject_id -> list of float (hours per slot); None at index = use full lesson duration. Used for split lessons (same lesson in morning + afternoon).
    """

    date: date
    items: List[ScheduleItem] = field(default_factory=list)
    is_completed: bool = False
    selected_subject_ids: List[str] = field(default_factory=list)
    subject_time_slots: Dict[str, List[str]] = field(default_factory=dict)
    subject_lesson_map: Dict[str, List[str]] = field(default_factory=dict)
    subject_slot_durations: Dict[str, List[Optional[float]]] = field(default_factory=dict)

    def get_lesson_ids(self, subject_id: str) -> List[str]:
        """Return list of lesson_ids for this subject (never None)."""
        return _normalize_to_list(self.subject_lesson_map.get(subject_id))

    def get_time_slots(self, subject_id: str) -> List[str]:
        """Return list of start time strings for this subject (never None)."""
        return _normalize_to_list(self.subject_time_slots.get(subject_id))

    def get_slot_duration(self, subject_id: str, slot_index: int) -> Optional[float]:
        """Return duration in hours for this slot if set (for split lessons); else None = use full lesson duration."""
        lst = self.subject_slot_durations.get(subject_id)
        if not lst or slot_index >= len(lst):
            return None
        return lst[slot_index]

    def to_dict(self) -> dict:
        """Convert to dictionary. Always serializes slots/map as lists."""
        return {
            "date": self.date.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "is_completed": self.is_completed,
            "selected_subject_ids": list(self.selected_subject_ids),
            "subject_time_slots": {k: list(v) for k, v in self.subject_time_slots.items()},
            "subject_lesson_map": {k: list(v) for k, v in self.subject_lesson_map.items()},
            "subject_slot_durations": {k: list(v) for k, v in self.subject_slot_durations.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DaySchedule":
        """Create from dictionary. Accepts legacy format (value is string) and converts to list."""
        raw_slots = data.get("subject_time_slots", {}) or {}
        raw_map = data.get("subject_lesson_map", {}) or {}
        subject_time_slots = {
            k: _normalize_to_list(v) for k, v in raw_slots.items()
        }
        subject_lesson_map = {
            k: _normalize_to_list(v) for k, v in raw_map.items()
        }
        raw_dur = data.get("subject_slot_durations", {}) or {}
        subject_slot_durations = {}
        for k, v in raw_dur.items():
            if isinstance(v, list):
                subject_slot_durations[k] = [float(x) if x is not None else None for x in v]
        return cls(
            date=date.fromisoformat(data["date"]),
            items=[ScheduleItem.from_dict(item_data) for item_data in data.get("items", [])],
            is_completed=data.get("is_completed", False),
            selected_subject_ids=data.get("selected_subject_ids", []) or [],
            subject_time_slots=subject_time_slots,
            subject_lesson_map=subject_lesson_map,
            subject_slot_durations=subject_slot_durations,
        )


@dataclass
class WeekSchedule:
    """Represents schedule for a week"""
    
    week_number: int
    start_date: date  # Monday
    end_date: date  # Sunday
    days: List[DaySchedule] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "week_number": self.week_number,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "days": [day.to_dict() for day in self.days],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WeekSchedule":
        """Create from dictionary"""
        return cls(
            week_number=data["week_number"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            days=[DaySchedule.from_dict(day_data) for day_data in data.get("days", [])],
        )


@dataclass
class Schedule:
    """Represents a complete training schedule"""
    
    schedule_id: Optional[str] = None
    name: Optional[str] = None
    start_date: Optional[date] = None  # Must be Monday
    end_date: Optional[date] = None  # Must be Sunday
    weeks: List[WeekSchedule] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps"""
        if self.schedule_id is None:
            self.schedule_id = f"schedule_{datetime.now().timestamp()}"
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert schedule to dictionary"""
        return {
            "schedule_id": self.schedule_id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "weeks": [week.to_dict() for week in self.weeks],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        """Create schedule from dictionary"""
        schedule = cls(
            schedule_id=data.get("schedule_id"),
            name=data.get("name"),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            weeks=[WeekSchedule.from_dict(week_data) for week_data in data.get("weeks", [])],
        )
        if data.get("created_at"):
            schedule.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            schedule.updated_at = datetime.fromisoformat(data["updated_at"])
        return schedule
    
    def to_summary_dict(self) -> dict:
        """Convert to summary dictionary (for schedules_summary.json)"""
        return {
            "schedule_id": self.schedule_id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "week_count": len(self.weeks),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

