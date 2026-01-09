"""Authentication service"""

from typing import Optional
from datetime import datetime
from ..models.user import User
from .file_service import FileService
from ..utils.logger import setup_logger

logger = setup_logger()


class AuthService:
    """Service for user authentication"""
    
    def __init__(self, file_service: Optional[FileService] = None):
        """Initialize auth service"""
        self.file_service = file_service or FileService()
        self.current_user: Optional[User] = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user"""
        try:
            user = self.file_service.load_user(username)
            if user is None:
                logger.warning(f"Login failed: User '{username}' not found")
                return False
            
            if user.verify_password(password):
                self.current_user = user
                # Update last login
                user.last_login = datetime.now()
                self.file_service.save_user(user)
                logger.info(f"User '{username}' logged in successfully")
                return True
            else:
                logger.warning(f"Login failed: Invalid password for user '{username}'")
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            logger.info(f"User '{self.current_user.username}' logged out")
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        return self.current_user
    
    def create_user(self, username: str, password: str, full_name: Optional[str] = None) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.file_service.load_user(username)
            if existing_user:
                logger.warning(f"User creation failed: User '{username}' already exists")
                return None
            
            # Create new user
            user = User(
                username=username,
                password_hash=User.hash_password(password),
                full_name=full_name
            )
            
            if self.file_service.save_user(user):
                logger.info(f"User '{username}' created successfully")
                return user
            else:
                logger.error(f"Failed to save user '{username}'")
                return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

