"""Date and time utilities"""

from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Tuple


class DayOfWeek(Enum):
    """Day of week enumeration"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def get_day_of_week(d: date) -> DayOfWeek:
    """Get DayOfWeek enum from date"""
    return DayOfWeek(d.weekday())


def is_monday(d: date) -> bool:
    """Check if date is Monday"""
    return d.weekday() == 0


def is_sunday(d: date) -> bool:
    """Check if date is Sunday"""
    return d.weekday() == 6


def get_week_start(date_obj: date) -> date:
    """Get Monday of the week containing the given date"""
    days_since_monday = date_obj.weekday()
    return date_obj - timedelta(days=days_since_monday)


def get_week_end(date_obj: date) -> date:
    """Get Sunday of the week containing the given date"""
    days_until_sunday = 6 - date_obj.weekday()
    return date_obj + timedelta(days=days_until_sunday)


def get_weeks_in_range(start_date: date, end_date: date) -> List[Tuple[date, date]]:
    """Get list of (Monday, Sunday) tuples for all weeks in the date range"""
    weeks = []
    current_monday = get_week_start(start_date)
    end_sunday = get_week_end(end_date)
    
    while current_monday <= end_sunday:
        current_sunday = current_monday + timedelta(days=6)
        weeks.append((current_monday, current_sunday))
        current_monday += timedelta(days=7)
    
    return weeks


def is_first_thursday_of_month(d: date) -> bool:
    """Check if date is the first Thursday of the month"""
    if d.weekday() != 3:  # Not Thursday
        return False
    return d.day <= 7  # First week of month


def time_to_hours(t: time) -> float:
    """Convert time to hours (as float)"""
    return t.hour + t.minute / 60.0 + t.second / 3600.0


def hours_to_time(hours: float) -> time:
    """Convert hours (float) to time"""
    total_seconds = int(hours * 3600)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return time(h, m, s)


def add_hours_to_time(t: time, hours: float) -> time:
    """Add hours to a time"""
    total_minutes = t.hour * 60 + t.minute + int(hours * 60)
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return time(new_hours, new_minutes)


def time_duration(start: time, end: time) -> float:
    """Calculate duration in hours between two times"""
    start_seconds = start.hour * 3600 + start.minute * 60 + start.second
    end_seconds = end.hour * 3600 + end.minute * 60 + end.second
    
    if end_seconds < start_seconds:
        # Assume next day
        end_seconds += 24 * 3600
    
    return (end_seconds - start_seconds) / 3600.0

