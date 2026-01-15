"""Application constants"""

from datetime import time
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

# Subject categories
SUBJECT_CATEGORY_MAIN = {
    "CHINH_TRI": "Chính trị",
    "QUAN_SU": "Quân sự",
    "HAU_CAN_KY_THUAT": "Hậu cần kỹ thuật"
}

SUBJECT_CATEGORY_QUAN_SU = {
    "THONG_TIN": "Thông tin",
    "CHIEN_THUAT": "Chiến thuật",
    "VU_KHI": "Vũ khí",
    "DIEU_LENH": "Điều lệnh",
    "THE_LUC": "Thể lực"
}

SUBJECT_CATEGORY_HAU_CAN_KY_THUAT = {
    "HAU_CAN": "Hậu cần",
    "KY_THUAT": "Kỹ thuật"
}

# Schedule constants
SCHEDULE_MORNING_START = time(7, 0)  # 7:00 AM
SCHEDULE_MORNING_END = time(11, 30)  # 11:30 AM
SCHEDULE_AFTERNOON_START = time(12, 30)  # 12:30 PM
SCHEDULE_AFTERNOON_END = time(16, 0)  # 4:00 PM

# Daily schedule: 8 hours total
# Morning: 7:00 - 11:30 (4.5 hours)
# Afternoon: 12:30 - 16:00 (3.5 hours)
DAILY_TOTAL_HOURS = 8.0
MORNING_HOURS = 4.5
AFTERNOON_HOURS = 3.5

# Fixed schedule items
FIXED_SCHEDULE_ITEMS = {
    "CHAO_CO": {
        "name": "Chào cờ",
        "day": DayOfWeek.MONDAY,
        "start_time": time(7, 0),
        "end_time": time(8, 0),
        "duration": 1.0
    },
    "HANH_QUAN": {
        "name": "Hành quân",
        "day": DayOfWeek.WEDNESDAY,
        "start_time": time(19, 0),
        "end_time": time(21, 0),
        "duration": 2.0
    },
    "VAN_HOA_CHINH_TRI": {
        "name": "Văn hóa chính trị tinh thần",
        "day": DayOfWeek.THURSDAY,
        "start_time": None,  # Use time_ranges
        "end_time": None,
        "duration": 8.0,
        "time_ranges": [
            {
                "start": time(7, 0),
                "end": time(11, 30)
            },
            {
                "start": time(12, 30),
                "end": time(16, 0)
            }
        ],
        "first_thursday_of_month": True
    },
    "NGHI_TRUA": {
        "name": "Nghỉ trưa",
        "day": None,
        "start_time": time(11, 30),
        "end_time": time(12, 30),
        "duration": 1.0,
        "daily": True,
        "is_break": True
    }
}

# Days of week (Monday = 0, Sunday = 6)
SCHEDULE_DAYS = [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                 DayOfWeek.THURSDAY, DayOfWeek.FRIDAY, DayOfWeek.SATURDAY]

# Business rules
MAX_LESSONS_PER_SUBJECT = 500
MIN_SUBJECT_NAME_LENGTH = 1

# File paths
DEFAULT_DATA_DIR = "src/data"
DEFAULT_LOG_DIR = "logs"

# Application settings
APP_NAME = "Ứng dụng Quản lý Kế hoạch Huấn luyện"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Victor Howard"

