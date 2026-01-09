"""Dialog for adding/editing lessons"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDoubleSpinBox, QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from typing import Optional
from src.models.lesson import Lesson


class LessonDialog(QDialog):
    """Dialog for adding/editing a lesson"""
    
    def __init__(self, parent=None, lesson: Optional[Lesson] = None):
        """Initialize lesson dialog"""
        super().__init__(parent)
        self.lesson = lesson
        self.setWindowTitle("Thêm/Sửa bài học" if lesson else "Thêm bài học")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
        
        if lesson:
            self.load_lesson(lesson)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên bài học:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Thời lượng (giờ):")
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setMinimum(0.0)
        self.duration_input.setMaximum(24.0)
        self.duration_input.setDecimals(1)
        self.duration_input.setSpecialValueText("Dùng thời lượng mặc định")
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)
        
        # Materials
        materials_label = QLabel("Tài liệu:")
        layout.addWidget(materials_label)
        
        self.materials_list = QListWidget()
        layout.addWidget(self.materials_list)
        
        materials_buttons = QHBoxLayout()
        self.add_material_btn = QPushButton("Thêm tài liệu")
        self.add_material_btn.clicked.connect(self.add_material)
        self.remove_material_btn = QPushButton("Xóa tài liệu")
        self.remove_material_btn.clicked.connect(self.remove_material)
        materials_buttons.addWidget(self.add_material_btn)
        materials_buttons.addWidget(self.remove_material_btn)
        layout.addLayout(materials_buttons)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_material(self):
        """Add material file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn tài liệu", "", "All Files (*.*)"
        )
        if file_path:
            item = QListWidgetItem(file_path)
            self.materials_list.addItem(item)
    
    def remove_material(self):
        """Remove selected material"""
        current_item = self.materials_list.currentItem()
        if current_item:
            self.materials_list.takeItem(self.materials_list.row(current_item))
    
    def load_lesson(self, lesson: Lesson):
        """Load lesson data"""
        self.name_input.setText(lesson.name)
        if lesson.duration:
            self.duration_input.setValue(lesson.duration)
        for material in lesson.materials:
            self.materials_list.addItem(QListWidgetItem(material))
    
    def get_lesson(self) -> Optional[Lesson]:
        """Get lesson from dialog"""
        name = self.name_input.text().strip()
        if not name:
            return None
        
        duration = self.duration_input.value()
        if duration == 0.0:
            duration = None
        
        materials = []
        for i in range(self.materials_list.count()):
            item = self.materials_list.item(i)
            materials.append(item.text())
        
        if self.lesson:
            # Update existing lesson
            self.lesson.name = name
            self.lesson.duration = duration
            self.lesson.materials = materials
            from datetime import datetime
            self.lesson.updated_at = datetime.now()
            return self.lesson
        else:
            # Create new lesson
            return Lesson(name=name, duration=duration, materials=materials)

