"""User model"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import hashlib


@dataclass
class User:
    """Represents a user"""
    
    username: str
    password_hash: str  # Hashed password
    full_name: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps"""
        if self.user_id is None:
            self.user_id = f"user_{datetime.now().timestamp()}"
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return self.password_hash == self.hash_password(password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary"""
        user = cls(
            username=data["username"],
            password_hash=data["password_hash"],
            full_name=data.get("full_name"),
            user_id=data.get("user_id"),
        )
        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_login"):
            user.last_login = datetime.fromisoformat(data["last_login"])
        return user

