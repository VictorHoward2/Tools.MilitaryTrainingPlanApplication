"""Lesson model"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Lesson:
    """Represents a lesson within a subject"""
    
    name: str
    duration: Optional[float] = None  # Duration in hours
    materials: List[str] = field(default_factory=list)  # List of file paths
    lesson_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if self.lesson_id is None:
            self.lesson_id = f"lesson_{datetime.now().timestamp()}"
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert lesson to dictionary"""
        return {
            "lesson_id": self.lesson_id,
            "name": self.name,
            "duration": self.duration,
            "materials": self.materials,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Lesson":
        """Create lesson from dictionary"""
        lesson = cls(
            name=data["name"],
            duration=data.get("duration"),
            materials=data.get("materials", []),
            lesson_id=data.get("lesson_id"),
        )
        if data.get("created_at"):
            lesson.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            lesson.updated_at = datetime.fromisoformat(data["updated_at"])
        return lesson

