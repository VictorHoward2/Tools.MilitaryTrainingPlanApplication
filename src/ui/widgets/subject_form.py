"""Subject form for adding/editing subjects"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QDoubleSpinBox, QComboBox, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from typing import Optional, List
from src.models.subject import Subject
from src.models.lesson import Lesson
from src.utils.constants import (
    SUBJECT_CATEGORY_MAIN, SUBJECT_CATEGORY_QUAN_SU, 
    SUBJECT_CATEGORY_HAU_CAN_KY_THUAT
)


class SubjectForm(QWidget):
    """Form for adding/editing subjects"""
    
    saved = Signal(Subject)
    cancelled = Signal()
    
    def __init__(self, subject: Optional[Subject] = None, parent=None):
        """Initialize subject form"""
        super().__init__(parent)
        self.subject = subject
        self.is_editing = subject is not None
        self.setup_ui()
        
        if subject:
            self.load_subject(subject)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Basic info group
        basic_group = QGroupBox("Thông tin cơ bản")
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên môn học (bắt buộc)")
        basic_layout.addRow("Tên môn học:", self.name_input)
        
        self.code_input = QLineEdit()
        basic_layout.addRow("Mã môn học:", self.code_input)
        
        self.location_input = QLineEdit()
        basic_layout.addRow("Địa điểm:", self.location_input)
        
        self.default_duration_input = QDoubleSpinBox()
        self.default_duration_input.setMinimum(0.0)
        self.default_duration_input.setMaximum(24.0)
        self.default_duration_input.setSuffix(" giờ")
        self.default_duration_input.setDecimals(1)
        basic_layout.addRow("Thời lượng mặc định:", self.default_duration_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Category group
        category_group = QGroupBox("Phân loại")
        category_layout = QFormLayout()
        
        self.category_main_combo = QComboBox()
        self.category_main_combo.addItem("", None)
        for key, value in SUBJECT_CATEGORY_MAIN.items():
            self.category_main_combo.addItem(value, key)
        self.category_main_combo.currentIndexChanged.connect(self.on_category_main_changed)
        category_layout.addRow("Phân loại chính:", self.category_main_combo)
        
        self.category_sub_combo = QComboBox()
        category_layout.addRow("Phân loại phụ:", self.category_sub_combo)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # Lessons group
        lessons_group = QGroupBox("Bài học")
        lessons_layout = QVBoxLayout()
        
        # Lesson list
        self.lessons_list = QListWidget()
        lessons_layout.addWidget(self.lessons_list)
        
        # Lesson buttons
        lesson_buttons = QHBoxLayout()
        self.add_lesson_btn = QPushButton("Thêm bài học")
        self.add_lesson_btn.clicked.connect(self.add_lesson)
        self.edit_lesson_btn = QPushButton("Sửa bài học")
        self.edit_lesson_btn.clicked.connect(self.edit_lesson)
        self.remove_lesson_btn = QPushButton("Xóa bài học")
        self.remove_lesson_btn.clicked.connect(self.remove_lesson)
        lesson_buttons.addWidget(self.add_lesson_btn)
        lesson_buttons.addWidget(self.edit_lesson_btn)
        lesson_buttons.addWidget(self.remove_lesson_btn)
        lessons_layout.addLayout(lesson_buttons)
        
        lessons_group.setLayout(lessons_layout)
        layout.addWidget(lessons_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Lưu")
        self.save_btn.clicked.connect(self.save_subject)
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
    
    def add_lesson(self):
        """Add a new lesson"""
        from src.ui.dialogs.lesson_dialog import LessonDialog
        
        dialog = LessonDialog(self)
        if dialog.exec():
            lesson = dialog.get_lesson()
            if lesson:
                item = QListWidgetItem(lesson.name)
                item.setData(Qt.UserRole, lesson)
                self.lessons_list.addItem(item)
    
    def edit_lesson(self):
        """Edit selected lesson"""
        current_item = self.lessons_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn bài học cần sửa")
            return
        
        from src.ui.dialogs.lesson_dialog import LessonDialog
        
        lesson = current_item.data(Qt.UserRole)
        dialog = LessonDialog(self, lesson)
        if dialog.exec():
            updated_lesson = dialog.get_lesson()
            if updated_lesson:
                current_item.setData(Qt.UserRole, updated_lesson)
                current_item.setText(updated_lesson.name)
    
    def remove_lesson(self):
        """Remove selected lesson"""
        current_item = self.lessons_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn bài học cần xóa")
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc chắn muốn xóa bài học này?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.lessons_list.takeItem(self.lessons_list.row(current_item))
    
    def load_subject(self, subject: Subject):
        """Load subject data into form"""
        self.name_input.setText(subject.name)
        if subject.code:
            self.code_input.setText(subject.code)
        if subject.location:
            self.location_input.setText(subject.location)
        if subject.default_duration:
            self.default_duration_input.setValue(subject.default_duration)
        
        # Set category
        if subject.category_main:
            index = self.category_main_combo.findData(subject.category_main)
            if index >= 0:
                self.category_main_combo.setCurrentIndex(index)
                if subject.category_sub:
                    sub_index = self.category_sub_combo.findData(subject.category_sub)
                    if sub_index >= 0:
                        self.category_sub_combo.setCurrentIndex(sub_index)
        
        # Load lessons
        for lesson in subject.lessons:
            item = QListWidgetItem(lesson.name)
            item.setData(Qt.UserRole, lesson)
            self.lessons_list.addItem(item)
    
    def save_subject(self):
        """Save subject"""
        # Validation
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên môn học là bắt buộc")
            return
        
        # Get lessons
        lessons = []
        for i in range(self.lessons_list.count()):
            item = self.lessons_list.item(i)
            lesson = item.data(Qt.UserRole)
            if lesson:
                lessons.append(lesson)
        
        # Create or update subject
        from datetime import datetime
        from src.models.subject import Subject
        
        if self.is_editing and self.subject:
            subject = self.subject
            subject.name = name
            subject.code = self.code_input.text().strip() or None
            subject.location = self.location_input.text().strip() or None
            default_duration = self.default_duration_input.value()
            subject.default_duration = default_duration if default_duration > 0 else None
            subject.category_main = self.category_main_combo.currentData()
            subject.category_sub = self.category_sub_combo.currentData()
            subject.lessons = lessons
            subject.updated_at = datetime.now()
        else:
            subject = Subject(
                name=name,
                code=self.code_input.text().strip() or None,
                location=self.location_input.text().strip() or None,
                default_duration=self.default_duration_input.value() if self.default_duration_input.value() > 0 else None,
                category_main=self.category_main_combo.currentData(),
                category_sub=self.category_sub_combo.currentData(),
                lessons=lessons
            )
        
        self.saved.emit(subject)

