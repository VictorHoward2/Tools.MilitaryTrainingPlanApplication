"""File service for JSON operations and directory management"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.subject import Subject
from ..models.schedule import Schedule
from ..models.user import User


class FileService:
    """Service for file operations"""
    
    def __init__(self, base_data_dir: Optional[str] = None):
        """Initialize file service with base data directory"""
        if base_data_dir is None:
            # Default to src/data relative to project root
            base_data_dir = Path(__file__).parent.parent.parent / "src" / "data"
        
        self.base_dir = Path(base_data_dir)
        self.subjects_dir = self.base_dir / "subjects"
        self.schedules_dir = self.base_dir / "schedules"
        self.materials_dir = self.base_dir / "materials"
        self.users_file = self.base_dir / "users.json"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.subjects_dir.mkdir(parents=True, exist_ok=True)
        self.schedules_dir.mkdir(parents=True, exist_ok=True)
        self.materials_dir.mkdir(parents=True, exist_ok=True)
    
    # Subject operations
    def save_subject(self, subject: Subject) -> bool:
        """Save subject to JSON files"""
        try:
            # Save detailed subject file
            subject_file = self.subjects_dir / f"{subject.subject_id}.json"
            with open(subject_file, 'w', encoding='utf-8') as f:
                json.dump(subject.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Update summary file
            self._update_subjects_summary(subject)
            
            return True
        except Exception as e:
            print(f"Error saving subject: {e}")
            return False
    
    def load_subject(self, subject_id: str) -> Optional[Subject]:
        """Load subject from JSON file"""
        try:
            subject_file = self.subjects_dir / f"{subject_id}.json"
            if not subject_file.exists():
                return None
            
            with open(subject_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Subject.from_dict(data)
        except Exception as e:
            print(f"Error loading subject: {e}")
            return None
    
    def load_all_subjects(self) -> List[Subject]:
        """Load all subjects"""
        subjects = []
        summary_file = self.subjects_dir / "subjects_summary.json"
        
        if not summary_file.exists():
            return subjects
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            for subject_summary in summary_data.get("subjects", []):
                subject_id = subject_summary.get("subject_id")
                if subject_id:
                    subject = self.load_subject(subject_id)
                    if subject:
                        subjects.append(subject)
        except Exception as e:
            print(f"Error loading all subjects: {e}")
        
        return subjects
    
    def delete_subject(self, subject_id: str) -> bool:
        """Delete subject and its files"""
        try:
            # Delete subject file
            subject_file = self.subjects_dir / f"{subject_id}.json"
            if subject_file.exists():
                subject_file.unlink()
            
            # Delete materials directory
            materials_subject_dir = self.materials_dir / subject_id
            if materials_subject_dir.exists():
                import shutil
                shutil.rmtree(materials_subject_dir)
            
            # Update summary
            self._update_subjects_summary_after_delete(subject_id)
            
            return True
        except Exception as e:
            print(f"Error deleting subject: {e}")
            return False
    
    def _update_subjects_summary(self, subject: Subject):
        """Update subjects summary file"""
        summary_file = self.subjects_dir / "subjects_summary.json"
        
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"subjects": []}
        
        # Find and update or add subject
        subjects = data.get("subjects", [])
        found = False
        for i, subj in enumerate(subjects):
            if subj.get("subject_id") == subject.subject_id:
                subjects[i] = subject.to_summary_dict()
                found = True
                break
        
        if not found:
            subjects.append(subject.to_summary_dict())
        
        data["subjects"] = subjects
        data["updated_at"] = datetime.now().isoformat()
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _update_subjects_summary_after_delete(self, subject_id: str):
        """Remove subject from summary after deletion"""
        summary_file = self.subjects_dir / "subjects_summary.json"
        
        if not summary_file.exists():
            return
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            subjects = data.get("subjects", [])
            data["subjects"] = [s for s in subjects if s.get("subject_id") != subject_id]
            data["updated_at"] = datetime.now().isoformat()
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error updating summary after delete: {e}")
    
    # Schedule operations
    def save_schedule(self, schedule: Schedule) -> bool:
        """Save schedule to JSON files"""
        try:
            # Save detailed schedule file
            schedule_file = self.schedules_dir / f"{schedule.schedule_id}.json"
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Update summary file
            self._update_schedules_summary(schedule)
            
            return True
        except Exception as e:
            print(f"Error saving schedule: {e}")
            return False
    
    def load_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Load schedule from JSON file"""
        try:
            schedule_file = self.schedules_dir / f"{schedule_id}.json"
            if not schedule_file.exists():
                return None
            
            with open(schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Schedule.from_dict(data)
        except Exception as e:
            print(f"Error loading schedule: {e}")
            return None
    
    def load_all_schedules(self) -> List[Schedule]:
        """Load all schedules"""
        schedules = []
        summary_file = self.schedules_dir / "schedules_summary.json"
        
        if not summary_file.exists():
            return schedules
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            for schedule_summary in summary_data.get("schedules", []):
                schedule_id = schedule_summary.get("schedule_id")
                if schedule_id:
                    schedule = self.load_schedule(schedule_id)
                    if schedule:
                        schedules.append(schedule)
        except Exception as e:
            print(f"Error loading all schedules: {e}")
        
        return schedules
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete schedule"""
        try:
            schedule_file = self.schedules_dir / f"{schedule_id}.json"
            if schedule_file.exists():
                schedule_file.unlink()
            
            # Update summary
            self._update_schedules_summary_after_delete(schedule_id)
            
            return True
        except Exception as e:
            print(f"Error deleting schedule: {e}")
            return False
    
    def _update_schedules_summary(self, schedule: Schedule):
        """Update schedules summary file"""
        summary_file = self.schedules_dir / "schedules_summary.json"
        
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"schedules": []}
        
        schedules = data.get("schedules", [])
        found = False
        for i, sched in enumerate(schedules):
            if sched.get("schedule_id") == schedule.schedule_id:
                schedules[i] = schedule.to_summary_dict()
                found = True
                break
        
        if not found:
            schedules.append(schedule.to_summary_dict())
        
        data["schedules"] = schedules
        data["updated_at"] = datetime.now().isoformat()
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _update_schedules_summary_after_delete(self, schedule_id: str):
        """Remove schedule from summary after deletion"""
        summary_file = self.schedules_dir / "schedules_summary.json"
        
        if not summary_file.exists():
            return
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            schedules = data.get("schedules", [])
            data["schedules"] = [s for s in schedules if s.get("schedule_id") != schedule_id]
            data["updated_at"] = datetime.now().isoformat()
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error updating schedule summary after delete: {e}")
    
    # Material operations
    def get_material_path(self, subject_id: str, lesson_id: str) -> Path:
        """Get path for lesson materials"""
        return self.materials_dir / subject_id / lesson_id
    
    def save_material(self, subject_id: str, lesson_id: str, file_path: str) -> Optional[str]:
        """Save a material file for a lesson"""
        try:
            material_dir = self.get_material_path(subject_id, lesson_id)
            material_dir.mkdir(parents=True, exist_ok=True)
            
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            dest_path = material_dir / source_path.name
            import shutil
            shutil.copy2(source_path, dest_path)
            
            return str(dest_path)
        except Exception as e:
            print(f"Error saving material: {e}")
            return None
    
    def get_materials(self, subject_id: str, lesson_id: str) -> List[str]:
        """Get list of material file paths for a lesson"""
        material_dir = self.get_material_path(subject_id, lesson_id)
        if not material_dir.exists():
            return []
        
        return [str(f) for f in material_dir.iterdir() if f.is_file()]
    
    # User operations
    def save_user(self, user: User) -> bool:
        """Save user to JSON file"""
        try:
            users = self.load_all_users()
            
            # Update or add user
            found = False
            for i, u in enumerate(users):
                if u.user_id == user.user_id or u.username == user.username:
                    users[i] = user
                    found = True
                    break
            
            if not found:
                users.append(user)
            
            # Save all users
            data = {
                "users": [u.to_dict() for u in users],
                "updated_at": datetime.now().isoformat()
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def load_user(self, username: str) -> Optional[User]:
        """Load user by username"""
        users = self.load_all_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    def load_all_users(self) -> List[User]:
        """Load all users"""
        if not self.users_file.exists():
            return []
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return [User.from_dict(user_data) for user_data in data.get("users", [])]
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

