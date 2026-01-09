"""Subject model"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .lesson import Lesson


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


@dataclass
class Subject:
    """Represents a subject/course"""
    
    name: str  # Required
    subject_id: Optional[str] = None
    code: Optional[str] = None  # Subject code
    lessons: List[Lesson] = field(default_factory=list)
    location: Optional[str] = None  # Learning location
    default_duration: Optional[float] = None  # Default duration in hours
    prerequisites: List[str] = field(default_factory=list)  # List of subject IDs
    category_main: Optional[str] = None  # Main category
    category_sub: Optional[str] = None  # Sub category (for Quân sự and Hậu cần kỹ thuật)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps and validate"""
        if self.subject_id is None:
            self.subject_id = f"subject_{datetime.now().timestamp()}"
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        # Validate lessons count
        if len(self.lessons) > 500:
            raise ValueError("A subject can have at most 500 lessons")
    
    def get_lesson_duration(self, lesson: Lesson) -> float:
        """Get duration of a lesson, using default if lesson duration is None"""
        if lesson.duration is not None:
            return lesson.duration
        if self.default_duration is not None:
            return self.default_duration
        return 0.0
    
    def to_dict(self) -> dict:
        """Convert subject to dictionary"""
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "lessons": [lesson.to_dict() for lesson in self.lessons],
            "location": self.location,
            "default_duration": self.default_duration,
            "prerequisites": self.prerequisites,
            "category_main": self.category_main,
            "category_sub": self.category_sub,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        """Create subject from dictionary"""
        from .lesson import Lesson
        
        subject = cls(
            name=data["name"],
            subject_id=data.get("subject_id"),
            code=data.get("code"),
            lessons=[Lesson.from_dict(lesson_data) for lesson_data in data.get("lessons", [])],
            location=data.get("location"),
            default_duration=data.get("default_duration"),
            prerequisites=data.get("prerequisites", []),
            category_main=data.get("category_main"),
            category_sub=data.get("category_sub"),
        )
        if data.get("created_at"):
            subject.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            subject.updated_at = datetime.fromisoformat(data["updated_at"])
        return subject
    
    def to_summary_dict(self) -> dict:
        """Convert to summary dictionary (for subjects_summary.json)"""
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "location": self.location,
            "default_duration": self.default_duration,
            "category_main": self.category_main,
            "category_sub": self.category_sub,
            "lesson_count": len(self.lessons),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

