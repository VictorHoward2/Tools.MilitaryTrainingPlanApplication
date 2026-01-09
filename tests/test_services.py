"""Tests for services"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.services.file_service import FileService
from src.services.subject_service import SubjectService
from src.services.auth_service import AuthService
from src.models.subject import Subject
from src.models.lesson import Lesson
from src.models.user import User


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_file_service_save_load_subject(temp_data_dir):
    """Test saving and loading subject"""
    file_service = FileService(base_data_dir=temp_data_dir)
    subject = Subject(name="Test Subject", code="TS001")
    lesson = Lesson(name="Test Lesson", duration=1.0)
    subject.lessons.append(lesson)
    
    assert file_service.save_subject(subject)
    loaded = file_service.load_subject(subject.subject_id)
    
    assert loaded is not None
    assert loaded.name == subject.name
    assert loaded.code == subject.code
    assert len(loaded.lessons) == 1


def test_subject_service_create(temp_data_dir):
    """Test subject service create"""
    file_service = FileService(base_data_dir=temp_data_dir)
    subject_service = SubjectService(file_service)
    
    subject = Subject(name="Test Subject")
    success, error = subject_service.create_subject(subject)
    
    assert success
    assert error is None


def test_subject_service_search(temp_data_dir):
    """Test subject service search"""
    file_service = FileService(base_data_dir=temp_data_dir)
    subject_service = SubjectService(file_service)
    
    subject1 = Subject(name="Mathematics", code="MATH")
    subject2 = Subject(name="Physics", code="PHY")
    
    subject_service.create_subject(subject1)
    subject_service.create_subject(subject2)
    
    results = subject_service.search_subjects("Math")
    assert len(results) == 1
    assert results[0].name == "Mathematics"


def test_auth_service(temp_data_dir):
    """Test auth service"""
    file_service = FileService(base_data_dir=temp_data_dir)
    auth_service = AuthService(file_service)
    
    # Create user
    user = auth_service.create_user("testuser", "password", "Test User")
    assert user is not None
    
    # Login
    assert auth_service.login("testuser", "password")
    assert auth_service.is_authenticated()
    
    # Wrong password
    auth_service.logout()
    assert not auth_service.login("testuser", "wrong")
    assert not auth_service.is_authenticated()

