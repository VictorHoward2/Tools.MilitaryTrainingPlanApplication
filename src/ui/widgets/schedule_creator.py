"""Schedule creator widget"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QGroupBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date, time
from typing import Optional, List
from src.models.schedule import Schedule, DaySchedule
from src.models.subject import Subject
from src.models.lesson import Lesson
from src.services.schedule_service import ScheduleService
from src.services.subject_service import SubjectService
from src.utils.constants import (
    SUBJECT_CATEGORY_MAIN, SUBJECT_CATEGORY_QUAN_SU,
    SUBJECT_CATEGORY_HAU_CAN_KY_THUAT
)


class ScheduleCreator(QWidget):
    """Widget for creating schedules"""
    
    schedule_created = Signal(Schedule)
    
    def __init__(self, schedule_service: ScheduleService, 
                 subject_service: SubjectService, parent=None):
        """Initialize schedule creator"""
        super().__init__(parent)
        self.schedule_service = schedule_service
        self.subject_service = subject_service
        self.current_schedule: Optional[Schedule] = None
        self.current_week_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Date selection
        date_group = QGroupBox("Chọn thời gian")
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("Ngày bắt đầu (Thứ Hai):"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("Ngày kết thúc (Chủ Nhật):"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(6))
        date_layout.addWidget(self.end_date_edit)
        
        self.create_schedule_btn = QPushButton("Tạo thời khóa biểu")
        self.create_schedule_btn.clicked.connect(self.create_schedule)
        date_layout.addWidget(self.create_schedule_btn)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Week navigation
        week_nav_layout = QHBoxLayout()
        self.prev_week_btn = QPushButton("← Tuần trước")
        self.prev_week_btn.clicked.connect(self.prev_week)
        self.prev_week_btn.setEnabled(False)
        
        self.week_label = QLabel("Tuần 1")
        self.week_label.setAlignment(Qt.AlignCenter)
        
        self.next_week_btn = QPushButton("Tuần tiếp →")
        self.next_week_btn.clicked.connect(self.next_week)
        self.next_week_btn.setEnabled(False)
        
        week_nav_layout.addWidget(self.prev_week_btn)
        week_nav_layout.addWidget(self.week_label)
        week_nav_layout.addWidget(self.next_week_btn)
        layout.addLayout(week_nav_layout)
        
        # Schedule table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setRowCount(20)  # Enough rows for lessons
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.add_lesson_btn = QPushButton("Thêm bài học")
        self.add_lesson_btn.clicked.connect(self.add_lesson)
        self.add_lesson_btn.setEnabled(False)
        
        self.validate_btn = QPushButton("Kiểm tra")
        self.validate_btn.clicked.connect(self.validate_current_week)
        self.validate_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Lưu thời khóa biểu")
        self.save_btn.clicked.connect(self.save_schedule)
        self.save_btn.setEnabled(False)
        
        action_layout.addWidget(self.add_lesson_btn)
        action_layout.addWidget(self.validate_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.save_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def create_schedule(self):
        """Create new schedule"""
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        
        # Validate dates
        if start_date.weekday() != 0:
            QMessageBox.warning(self, "Lỗi", "Ngày bắt đầu phải là Thứ Hai")
            return
        
        if end_date.weekday() != 6:
            QMessageBox.warning(self, "Lỗi", "Ngày kết thúc phải là Chủ Nhật")
            return
        
        if start_date >= end_date:
            QMessageBox.warning(self, "Lỗi", "Ngày bắt đầu phải trước ngày kết thúc")
            return
        
        try:
            self.current_schedule = self.schedule_service.create_schedule(
                start_date, end_date, f"Thời khóa biểu {start_date} - {end_date}"
            )
            self.current_week_index = 0
            self.update_ui()
            QMessageBox.information(self, "Thành công", "Đã tạo thời khóa biểu")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tạo thời khóa biểu: {str(e)}")
    
    def update_ui(self):
        """Update UI with current week"""
        if not self.current_schedule:
            return
        
        if self.current_week_index >= len(self.current_schedule.weeks):
            return
        
        week = self.current_schedule.weeks[self.current_week_index]
        self.week_label.setText(f"Tuần {week.week_number} ({week.start_date} - {week.end_date})")
        
        # Enable/disable navigation
        self.prev_week_btn.setEnabled(self.current_week_index > 0)
        self.next_week_btn.setEnabled(
            self.current_week_index < len(self.current_schedule.weeks) - 1
        )
        
        # Enable action buttons
        self.add_lesson_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        # Clear table
        self.table.clearContents()
        
        # Display schedule for each day
        for day_index, day in enumerate(week.days):
            col = day_index
            row = 0
            
            for item in day.items:
                if row >= self.table.rowCount():
                    self.table.setRowCount(row + 1)
                
                text = f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}\n"
                text += f"{item.subject_name}\n{item.lesson_name}"
                
                table_item = QTableWidgetItem(text)
                table_item.setData(Qt.UserRole, (day_index, item))
                self.table.setItem(row, col, table_item)
                row += 1
    
    def prev_week(self):
        """Go to previous week"""
        if self.current_week_index > 0:
            self.current_week_index -= 1
            self.update_ui()
    
    def next_week(self):
        """Go to next week"""
        if self.current_schedule and \
           self.current_week_index < len(self.current_schedule.weeks) - 1:
            self.current_week_index += 1
            self.update_ui()
    
    def add_lesson(self):
        """Add lesson to current week"""
        if not self.current_schedule:
            return
        
        dialog = AddLessonDialog(
            self.subject_service, self.current_schedule, 
            self.schedule_service, self
        )
        if dialog.exec():
            week_num, day_index, subject, lesson, start_time = dialog.get_selection()
            
            if week_num != self.current_week_index + 1:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ngày trong tuần hiện tại")
                return
            
            success, error = self.schedule_service.add_lesson_to_day(
                self.current_schedule, week_num, day_index, subject, lesson, start_time
            )
            
            if success:
                self.update_ui()
                # Validate after adding
                self.validate_current_week()
            else:
                QMessageBox.warning(self, "Lỗi", error or "Không thể thêm bài học")
    
    def validate_current_week(self):
        """Validate current week schedule"""
        if not self.current_schedule:
            return
        
        week = self.current_schedule.weeks[self.current_week_index]
        issues = []
        
        for day_index, day in enumerate(week.days):
            is_valid, total_hours, suggestion = self.schedule_service.validate_day_schedule(day)
            if not is_valid:
                day_name = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"][day_index]
                issues.append(f"{day_name}: {suggestion}")
        
        if issues:
            message = "Các vấn đề phát hiện:\n\n" + "\n".join(issues)
            QMessageBox.warning(self, "Cảnh báo", message)
        else:
            QMessageBox.information(self, "Thành công", "Thời khóa biểu tuần này hợp lệ!")
    
    def save_schedule(self):
        """Save schedule"""
        if not self.current_schedule:
            return
        
        success, error = self.schedule_service.save_schedule(self.current_schedule)
        if success:
            QMessageBox.information(self, "Thành công", "Đã lưu thời khóa biểu")
            self.schedule_created.emit(self.current_schedule)
        else:
            QMessageBox.warning(self, "Lỗi", error or "Không thể lưu thời khóa biểu")


class AddLessonDialog(QDialog):
    """Dialog for adding a lesson to schedule"""
    
    def __init__(self, subject_service: SubjectService, schedule: Schedule, 
                 schedule_service: Optional[ScheduleService] = None, parent=None):
        """Initialize dialog"""
        super().__init__(parent)
        self.subject_service = subject_service
        self.schedule = schedule
        self.schedule_service = schedule_service
        self.selected_week_num = None
        self.selected_day_index = None
        self.selected_subject = None
        self.selected_lesson = None
        self.selected_start_time = None
        self.setWindowTitle("Thêm bài học")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Week and day selection
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel("Tuần:"))
        self.week_combo = QComboBox()
        for i, week in enumerate(self.schedule.weeks):
            self.week_combo.addItem(f"Tuần {week.week_number} ({week.start_date})", i)
        self.week_combo.currentIndexChanged.connect(self.on_week_changed)
        week_layout.addWidget(self.week_combo)
        layout.addLayout(week_layout)
        
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Ngày:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"])
        day_layout.addWidget(self.day_combo)
        layout.addLayout(day_layout)
        
        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Phân loại chính:"))
        self.category_main_combo = QComboBox()
        self.category_main_combo.addItem("", None)
        for key, value in SUBJECT_CATEGORY_MAIN.items():
            self.category_main_combo.addItem(value, key)
        self.category_main_combo.currentIndexChanged.connect(self.on_category_main_changed)
        category_layout.addWidget(self.category_main_combo)
        layout.addLayout(category_layout)
        
        sub_category_layout = QHBoxLayout()
        sub_category_layout.addWidget(QLabel("Phân loại phụ:"))
        self.category_sub_combo = QComboBox()
        sub_category_layout.addWidget(self.category_sub_combo)
        layout.addLayout(sub_category_layout)
        
        # Subject selection
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Môn học:"))
        self.subject_combo = QComboBox()
        self.subject_combo.currentIndexChanged.connect(self.on_subject_changed)
        subject_layout.addWidget(self.subject_combo)
        layout.addLayout(subject_layout)
        
        # Lesson selection
        lesson_layout = QHBoxLayout()
        lesson_layout.addWidget(QLabel("Bài học:"))
        self.lesson_combo = QComboBox()
        lesson_layout.addWidget(self.lesson_combo)
        layout.addLayout(lesson_layout)
        
        # Time selection
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Giờ bắt đầu:"))
        self.time_combo = QComboBox()
        # Add time slots
        for hour in range(7, 17):
            for minute in [0, 30]:
                if hour == 7 and minute == 0:
                    continue  # Skip 7:00 (Chào cờ)
                time_str = f"{hour:02d}:{minute:02d}"
                self.time_combo.addItem(time_str, time(hour, minute))
        time_layout.addWidget(self.time_combo)
        layout.addLayout(time_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.on_week_changed(0)
    
    def on_week_changed(self, index):
        """Handle week change"""
        self.selected_week_num = index + 1
    
    def on_category_main_changed(self, index):
        """Handle main category change"""
        self.category_sub_combo.clear()
        self.category_sub_combo.addItem("", None)
        
        category_main = self.category_main_combo.currentData()
        if category_main == "QUAN_SU":
            for key, value in SUBJECT_CATEGORY_QUAN_SU.items():
                self.category_sub_combo.addItem(value, key)
        elif category_main == "HAU_CAN_KY_THUAT":
            for key, value in SUBJECT_CATEGORY_HAU_CAN_KY_THUAT.items():
                self.category_sub_combo.addItem(value, key)
        
        self.filter_subjects()
    
    def filter_subjects(self):
        """Filter subjects by category"""
        self.subject_combo.clear()
        self.subject_combo.addItem("", None)
        
        category_main = self.category_main_combo.currentData()
        category_sub = self.category_sub_combo.currentData()
        
        all_subjects = self.subject_service.get_all_subjects()
        for subject in all_subjects:
            if category_main and subject.category_main != category_main:
                continue
            if category_sub and subject.category_sub != category_sub:
                continue
            self.subject_combo.addItem(subject.name, subject)
    
    def on_subject_changed(self, index):
        """Handle subject change"""
        self.lesson_combo.clear()
        self.lesson_combo.addItem("", None)
        
        subject = self.subject_combo.currentData()
        if not subject:
            return
        
        # Get available lessons (not yet scheduled)
        if self.schedule_service:
            try:
                available_lessons = self.schedule_service.get_available_lessons(
                    self.schedule, subject
                )
            except:
                available_lessons = subject.lessons
        else:
            available_lessons = subject.lessons
        
        for lesson in available_lessons:
            duration = subject.get_lesson_duration(lesson)
            text = f"{lesson.name} ({duration:.1f}h)"
            self.lesson_combo.addItem(text, lesson)
    
    def get_selection(self):
        """Get selected values"""
        week_num = self.selected_week_num
        day_index = self.day_combo.currentIndex()
        subject = self.subject_combo.currentData()
        lesson = self.lesson_combo.currentData()
        start_time = self.time_combo.currentData()
        
        return week_num, day_index, subject, lesson, start_time
    
    def accept(self):
        """Validate before accepting"""
        if not self.subject_combo.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn môn học")
            return
        if not self.lesson_combo.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn bài học")
            return
        if not self.time_combo.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn giờ bắt đầu")
            return
        
        super().accept()

