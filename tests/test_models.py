"""Tests for models"""

import pytest
from datetime import datetime, date, time
from src.models.subject import Subject
from src.models.lesson import Lesson
from src.models.schedule import Schedule, DaySchedule, ScheduleItem
from src.models.user import User


def test_lesson_creation():
    """Test lesson creation"""
    lesson = Lesson(name="Bài 1", duration=2.0)
    assert lesson.name == "Bài 1"
    assert lesson.duration == 2.0
    assert lesson.lesson_id is not None


def test_subject_creation():
    """Test subject creation"""
    subject = Subject(name="Môn học 1")
    assert subject.name == "Môn học 1"
    assert subject.subject_id is not None
    assert len(subject.lessons) == 0


def test_subject_with_lessons():
    """Test subject with lessons"""
    lesson1 = Lesson(name="Bài 1", duration=1.0)
    lesson2 = Lesson(name="Bài 2", duration=2.0)
    subject = Subject(name="Môn học 1", lessons=[lesson1, lesson2])
    assert len(subject.lessons) == 2


def test_subject_get_lesson_duration():
    """Test getting lesson duration"""
    subject = Subject(name="Môn học 1", default_duration=1.5)
    lesson = Lesson(name="Bài 1")  # No duration
    assert subject.get_lesson_duration(lesson) == 1.5
    
    lesson2 = Lesson(name="Bài 2", duration=2.0)
    assert subject.get_lesson_duration(lesson2) == 2.0


def test_user_password():
    """Test user password hashing"""
    user = User(username="test", password_hash=User.hash_password("password"))
    assert user.verify_password("password")
    assert not user.verify_password("wrong_password")


def test_schedule_item():
    """Test schedule item"""
    item = ScheduleItem(
        subject_id="sub1",
        lesson_id="les1",
        subject_name="Môn học",
        lesson_name="Bài học",
        start_time=time(7, 0),
        end_time=time(8, 0)
    )
    assert item.subject_id == "sub1"
    assert item.lesson_id == "les1"


def test_day_schedule():
    """Test day schedule"""
    day = DaySchedule(date=date.today())
    assert day.date == date.today()
    assert len(day.items) == 0
    assert not day.is_completed

