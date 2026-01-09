"""Subject manager widget"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional
from datetime import datetime
from src.models.subject import Subject
from src.services.subject_service import SubjectService


class SubjectManager(QWidget):
    """Widget for managing subjects"""
    
    subject_selected = Signal(Subject)
    
    def __init__(self, subject_service: SubjectService, parent=None):
        """Initialize subject manager"""
        super().__init__(parent)
        self.subject_service = subject_service
        self.subjects: List[Subject] = []
        self.setup_ui()
        self.load_subjects()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Search
        search_group = QGroupBox()
        search_layout = QHBoxLayout()
        search_label = QLabel("Tìm kiếm:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập tên hoặc mã môn học...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        toolbar.addWidget(search_group)
        
        # Sort
        sort_label = QLabel("Sắp xếp theo:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Tên", "Mã", "Thời gian thêm", "Phân loại"])
        self.sort_combo.currentIndexChanged.connect(self.apply_sort)
        toolbar.addWidget(sort_label)
        toolbar.addWidget(self.sort_combo)
        
        # Results count
        self.results_label = QLabel("0 kết quả")
        toolbar.addWidget(self.results_label)
        
        toolbar.addStretch()
        
        # Action buttons
        self.add_btn = QPushButton("Thêm môn học")
        self.add_btn.clicked.connect(self.add_subject)
        self.edit_btn = QPushButton("Sửa")
        self.edit_btn.clicked.connect(self.edit_subject)
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_subject)
        self.import_btn = QPushButton("Import Excel")
        self.import_btn.clicked.connect(self.import_from_excel)
        self.template_btn = QPushButton("Tải template Excel")
        self.template_btn.clicked.connect(self.download_template)
        
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.template_btn)
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tên môn học", "Mã môn học", "Phân loại", 
            "Số bài học", "Địa điểm", "Thời lượng mặc định"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_subjects(self):
        """Load all subjects"""
        self.subjects = self.subject_service.get_all_subjects()
        self.apply_filter_and_sort()
    
    def on_search_changed(self, text: str):
        """Handle search text change"""
        self.apply_filter_and_sort()
    
    def apply_filter_and_sort(self):
        """Apply search filter and sort"""
        # Filter
        search_text = self.search_input.text().strip()
        if search_text:
            filtered = self.subject_service.search_subjects(search_text)
        else:
            filtered = self.subjects.copy()
        
        # Sort
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:  # Name
            filtered.sort(key=lambda s: s.name.lower())
        elif sort_index == 1:  # Code
            filtered.sort(key=lambda s: (s.code or "").lower())
        elif sort_index == 2:  # Created time
            filtered.sort(key=lambda s: s.created_at or datetime.min, reverse=True)
        elif sort_index == 3:  # Category
            filtered.sort(key=lambda s: (s.category_main or "", s.category_sub or ""))
        
        # Update results count
        self.results_label.setText(f"{len(filtered)} kết quả")
        
        # Update table
        self.table.setRowCount(len(filtered))
        for row, subject in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(subject.name))
            self.table.setItem(row, 1, QTableWidgetItem(subject.code or ""))
            
            category_text = ""
            if subject.category_main:
                from src.utils.constants import SUBJECT_CATEGORY_MAIN
                category_text = SUBJECT_CATEGORY_MAIN.get(subject.category_main, "")
                if subject.category_sub:
                    if subject.category_main == "QUAN_SU":
                        from src.utils.constants import SUBJECT_CATEGORY_QUAN_SU
                        sub_cat = SUBJECT_CATEGORY_QUAN_SU.get(subject.category_sub, "")
                    elif subject.category_main == "HAU_CAN_KY_THUAT":
                        from src.utils.constants import SUBJECT_CATEGORY_HAU_CAN_KY_THUAT
                        sub_cat = SUBJECT_CATEGORY_HAU_CAN_KY_THUAT.get(subject.category_sub, "")
                    else:
                        sub_cat = ""
                    if sub_cat:
                        category_text += f" - {sub_cat}"
            
            self.table.setItem(row, 2, QTableWidgetItem(category_text))
            self.table.setItem(row, 3, QTableWidgetItem(str(len(subject.lessons))))
            self.table.setItem(row, 4, QTableWidgetItem(subject.location or ""))
            duration_text = f"{subject.default_duration} giờ" if subject.default_duration else ""
            self.table.setItem(row, 5, QTableWidgetItem(duration_text))
            
            # Store subject in item
            for col in range(6):
                item = self.table.item(row, col)
                if item:
                    item.setData(Qt.UserRole, subject)
    
    def apply_sort(self):
        """Apply sorting"""
        self.apply_filter_and_sort()
    
    def get_selected_subject(self) -> Optional[Subject]:
        """Get currently selected subject"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        item = self.table.item(current_row, 0)
        if item:
            return item.data(Qt.UserRole)
        return None
    
    def on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle item double click"""
        subject = item.data(Qt.UserRole)
        if subject:
            self.edit_subject()
    
    def add_subject(self):
        """Add new subject"""
        from .subject_form import SubjectForm
        
        form = SubjectForm()
        form.saved.connect(self.on_subject_saved)
        form.cancelled.connect(form.close)
        
        # Show in dialog or replace current widget
        from PySide6.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm môn học")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(form)
        dialog.exec()
    
    def edit_subject(self):
        """Edit selected subject"""
        subject = self.get_selected_subject()
        if not subject:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn môn học cần sửa")
            return
        
        # Load full subject
        full_subject = self.subject_service.get_subject(subject.subject_id)
        if not full_subject:
            QMessageBox.warning(self, "Lỗi", "Không thể tải thông tin môn học")
            return
        
        from .subject_form import SubjectForm
        from PySide6.QtWidgets import QDialog
        
        form = SubjectForm(full_subject)
        form.saved.connect(self.on_subject_saved)
        form.cancelled.connect(lambda: None)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Sửa môn học")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(form)
        dialog.exec()
    
    def delete_subject(self):
        """Delete selected subject"""
        subject = self.get_selected_subject()
        if not subject:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn môn học cần xóa")
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận", 
            f"Bạn có chắc chắn muốn xóa môn học '{subject.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = self.subject_service.delete_subject(subject.subject_id)
            if success:
                QMessageBox.information(self, "Thành công", "Đã xóa môn học thành công")
                self.load_subjects()
            else:
                QMessageBox.warning(self, "Lỗi", error or "Không thể xóa môn học")
    
    def import_from_excel(self):
        """Import subject from Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        
        success, subject, error = self.subject_service.import_from_excel(file_path)
        if success:
            QMessageBox.information(self, "Thành công", f"Đã import môn học '{subject.name}' thành công")
            self.load_subjects()
        else:
            QMessageBox.warning(self, "Lỗi", error or "Không thể import môn học")
    
    def download_template(self):
        """Download Excel template"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu template Excel", "subject_template.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if file_path:
            self.subject_service.create_template(file_path)
            QMessageBox.information(self, "Thành công", f"Đã tạo template tại: {file_path}")
    
    def on_subject_saved(self, subject: Subject):
        """Handle subject saved"""
        # Check if subject has ID (editing) or not (new)
        is_editing = subject.subject_id and any(
            s.subject_id == subject.subject_id for s in self.subjects
        )
        
        if is_editing:
            success, error = self.subject_service.update_subject(subject)
        else:
            success, error = self.subject_service.create_subject(subject)
        
        if success:
            QMessageBox.information(self, "Thành công", "Đã lưu môn học thành công")
            self.load_subjects()
            # Close dialog if exists
            from PySide6.QtWidgets import QDialog
            parent = self.parent()
            while parent:
                if isinstance(parent, QDialog):
                    parent.accept()
                    break
                parent = parent.parent()
        else:
            QMessageBox.warning(self, "Lỗi", error or "Không thể lưu môn học")

