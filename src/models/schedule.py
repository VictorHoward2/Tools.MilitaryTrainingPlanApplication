"""Schedule model"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
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


@dataclass
class DaySchedule:
    """Represents schedule for a single day"""
    
    date: date
    items: List[ScheduleItem] = field(default_factory=list)
    is_completed: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "date": self.date.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "is_completed": self.is_completed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DaySchedule":
        """Create from dictionary"""
        return cls(
            date=date.fromisoformat(data["date"]),
            items=[ScheduleItem.from_dict(item_data) for item_data in data.get("items", [])],
            is_completed=data.get("is_completed", False),
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

