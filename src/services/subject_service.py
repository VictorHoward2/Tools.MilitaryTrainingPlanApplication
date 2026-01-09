"""Subject service for CRUD operations"""

from typing import List, Optional
from ..models.subject import Subject
from ..models.lesson import Lesson
from .file_service import FileService
from .excel_service import ExcelService
from ..utils.logger import setup_logger
from ..utils.constants import MAX_LESSONS_PER_SUBJECT, MIN_SUBJECT_NAME_LENGTH

logger = setup_logger()


class SubjectService:
    """Service for subject management"""
    
    def __init__(self, file_service: Optional[FileService] = None):
        """Initialize subject service"""
        self.file_service = file_service or FileService()
        self.excel_service = ExcelService()
    
    def create_subject(self, subject: Subject) -> tuple[bool, Optional[str]]:
        """Create a new subject"""
        try:
            # Validation
            error = self._validate_subject(subject)
            if error:
                return False, error
            
            # Save subject
            if self.file_service.save_subject(subject):
                logger.info(f"Created subject: {subject.name} ({subject.subject_id})")
                return True, None
            else:
                return False, "Lỗi khi lưu môn học"
                
        except Exception as e:
            logger.error(f"Error creating subject: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def update_subject(self, subject: Subject) -> tuple[bool, Optional[str]]:
        """Update an existing subject"""
        try:
            # Check if subject exists
            existing = self.file_service.load_subject(subject.subject_id)
            if not existing:
                return False, "Môn học không tồn tại"
            
            # Validation
            error = self._validate_subject(subject)
            if error:
                return False, error
            
            # Update timestamp
            from datetime import datetime
            subject.updated_at = datetime.now()
            
            # Save subject
            if self.file_service.save_subject(subject):
                logger.info(f"Updated subject: {subject.name} ({subject.subject_id})")
                return True, None
            else:
                return False, "Lỗi khi lưu môn học"
                
        except Exception as e:
            logger.error(f"Error updating subject: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def delete_subject(self, subject_id: str) -> tuple[bool, Optional[str]]:
        """Delete a subject"""
        try:
            subject = self.file_service.load_subject(subject_id)
            if not subject:
                return False, "Môn học không tồn tại"
            
            if self.file_service.delete_subject(subject_id):
                logger.info(f"Deleted subject: {subject_id}")
                return True, None
            else:
                return False, "Lỗi khi xóa môn học"
                
        except Exception as e:
            logger.error(f"Error deleting subject: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def get_subject(self, subject_id: str) -> Optional[Subject]:
        """Get subject by ID"""
        return self.file_service.load_subject(subject_id)
    
    def get_all_subjects(self) -> List[Subject]:
        """Get all subjects"""
        return self.file_service.load_all_subjects()
    
    def search_subjects(self, query: str) -> List[Subject]:
        """Search subjects by name or code"""
        query_lower = query.lower().strip()
        if not query_lower:
            return self.get_all_subjects()
        
        all_subjects = self.get_all_subjects()
        results = []
        
        for subject in all_subjects:
            if (query_lower in subject.name.lower() or 
                (subject.code and query_lower in subject.code.lower())):
                results.append(subject)
        
        return results
    
    def import_from_excel(self, file_path: str) -> tuple[bool, Optional[Subject], Optional[str]]:
        """Import subject from Excel file"""
        try:
            subject = self.excel_service.import_subject_from_excel(file_path)
            if not subject:
                return False, None, "Không thể đọc file Excel hoặc dữ liệu không hợp lệ"
            
            # Validate imported subject
            error = self._validate_subject(subject)
            if error:
                return False, None, error
            
            # Save subject
            success, error = self.create_subject(subject)
            if success:
                return True, subject, None
            else:
                return False, None, error
                
        except Exception as e:
            logger.error(f"Error importing subject from Excel: {e}")
            return False, None, f"Lỗi khi import: {str(e)}"
    
    def create_template(self, file_path: str):
        """Create Excel template for subject import"""
        self.excel_service.create_subject_template(file_path)
    
    def _validate_subject(self, subject: Subject) -> Optional[str]:
        """Validate subject data"""
        # Name is required
        if not subject.name or len(subject.name.strip()) < MIN_SUBJECT_NAME_LENGTH:
            return "Tên môn học là bắt buộc"
        
        # Check lesson count
        if len(subject.lessons) > MAX_LESSONS_PER_SUBJECT:
            return f"Một môn học chỉ có tối đa {MAX_LESSONS_PER_SUBJECT} bài học"
        
        return None

