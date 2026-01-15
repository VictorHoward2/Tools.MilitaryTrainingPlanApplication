"""Schedule viewer widget"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFileDialog,
    QMessageBox, QGroupBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter
from typing import Optional, List
from src.models.schedule import Schedule
from src.services.schedule_service import ScheduleService
from src.services.excel_service import ExcelService
from src.utils.i18n import tr
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import io


class ScheduleViewer(QWidget):
    """Widget for viewing and exporting schedules"""
    
    def __init__(self, schedule_service: ScheduleService, parent=None):
        """Initialize schedule viewer"""
        super().__init__(parent)
        self.schedule_service = schedule_service
        self.excel_service = ExcelService()
        self.current_schedule: Optional[Schedule] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Schedule selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel(tr("select_schedule")))
        self.schedule_combo = QComboBox()
        self.schedule_combo.currentIndexChanged.connect(self.on_schedule_changed)
        selection_layout.addWidget(self.schedule_combo)
        
        self.refresh_btn = QPushButton(tr("refresh_button"))
        self.refresh_btn.clicked.connect(self.load_schedules)
        selection_layout.addWidget(self.refresh_btn)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Week selection
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel(tr("select_week")))
        self.week_combo = QComboBox()
        self.week_combo.currentIndexChanged.connect(self.display_week)
        week_layout.addWidget(self.week_combo)
        week_layout.addStretch()
        layout.addLayout(week_layout)
        
        # Schedule table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            tr("monday"), tr("tuesday"), tr("wednesday"), 
            tr("thursday"), tr("friday"), tr("saturday")
        ])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_pdf_btn = QPushButton(tr("export_pdf"))
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        self.export_excel_btn = QPushButton(tr("export_excel"))
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.export_image_btn = QPushButton(tr("export_image"))
        self.export_image_btn.clicked.connect(self.export_to_image)
        export_layout.addWidget(self.export_pdf_btn)
        export_layout.addWidget(self.export_excel_btn)
        export_layout.addWidget(self.export_image_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        self.setLayout(layout)
        self.load_schedules()
    
    def load_schedules(self):
        """Load all schedules"""
        self.schedule_combo.clear()
        schedules = self.schedule_service.get_all_schedules()
        
        for schedule in schedules:
            name = schedule.name or f"{tr('schedule')} {schedule.start_date}"
            self.schedule_combo.addItem(name, schedule)
        
        if schedules:
            self.on_schedule_changed(0)
    
    def on_schedule_changed(self, index):
        """Handle schedule selection change"""
        if index < 0:
            return
        
        self.current_schedule = self.schedule_combo.itemData(index)
        if not self.current_schedule:
            return
        
        # Update week combo
        self.week_combo.clear()
        for week in self.current_schedule.weeks:
            self.week_combo.addItem(
                f"Tuần {week.week_number} ({week.start_date} - {week.end_date})",
                week
            )
        
        if self.current_schedule.weeks:
            self.display_week(0)
    
    def display_week(self, week_index):
        """Display schedule for selected week"""
        if not self.current_schedule or week_index < 0:
            return
        
        week = self.week_combo.itemData(week_index)
        if not week:
            return
        
        # Clear table
        self.table.setRowCount(0)
        
        # Find max number of items per day
        max_items = 0
        for day in week.days:
            max_items = max(max_items, len(day.items))
        
        if max_items == 0:
            return
        
        self.table.setRowCount(max_items)
        
        # Fill table
        for day_index, day in enumerate(week.days):
            for item_index, item in enumerate(day.items):
                text = self._format_item_display(item)
                
                table_item = QTableWidgetItem(text)
                self.table.setItem(item_index, day_index, table_item)

    def _format_item_display(self, item) -> str:
        """Format schedule item for display."""
        content = item.subject_name
        if item.lesson_name and item.lesson_name != item.subject_name:
            content = f"{item.subject_name}: {item.lesson_name}"
        return f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}: {content}"
    
    def export_to_pdf(self):
        """Export schedule to PDF"""
        if not self.current_schedule:
            QMessageBox.warning(self, tr("warning"), tr("please_select_schedule"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu PDF", f"{self.current_schedule.name or 'schedule'}.pdf",
            tr("pdf_files")
        )
        if not file_path:
            return
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(
                f"<b>{self.current_schedule.name or 'Thời khóa biểu'}</b>",
                styles['Title']
            )
            story.append(title)
            story.append(Spacer(1, 0.5*cm))
            
            # Export all weeks
            for week in self.current_schedule.weeks:
                # Week header
                week_title = Paragraph(
                    f"<b>Tuần {week.week_number}: {week.start_date} - {week.end_date}</b>",
                    styles['Heading2']
                )
                story.append(week_title)
                story.append(Spacer(1, 0.3*cm))
                
                # Create table data
                data = [["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]]
                
                # Find max items
                max_items = max(len(day.items) for day in week.days)
                
                for i in range(max_items):
                    row = []
                    for day in week.days:
                        if i < len(day.items):
                            item = day.items[i]
                            cell_text = self._format_item_display(item)
                            row.append(cell_text)
                        else:
                            row.append("")
                    data.append(row)
                
                # Create table
                table = Table(data, colWidths=[3*cm]*6)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.5*cm))
            
            doc.build(story)
            QMessageBox.information(self, "Thành công", f"Đã xuất PDF: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất PDF: {str(e)}")
    
    def export_to_excel(self):
        """Export schedule to Excel"""
        if not self.current_schedule:
            QMessageBox.warning(self, tr("warning"), tr("please_select_schedule"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Excel", f"{self.current_schedule.name or 'schedule'}.xlsx",
            tr("excel_files")
        )
        if not file_path:
            return
        
        try:
            success = self.excel_service.export_schedule_to_excel(
                self.current_schedule, file_path
            )
            if success:
                QMessageBox.information(self, "Thành công", f"Đã xuất Excel: {file_path}")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xuất Excel")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất Excel: {str(e)}")
    
    def export_to_image(self):
        """Export schedule to image"""
        if not PIL_AVAILABLE:
            QMessageBox.warning(
                self, "Lỗi", 
                "PIL/Pillow không được cài đặt. Vui lòng cài đặt: pip install Pillow"
            )
            return
        
        if not self.current_schedule:
            QMessageBox.warning(self, tr("warning"), tr("please_select_schedule"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Ảnh", f"{self.current_schedule.name or 'schedule'}.png",
            tr("image_files")
        )
        if not file_path:
            return
        
        try:
            # Get current week
            week_index = self.week_combo.currentIndex()
            if week_index < 0:
                QMessageBox.warning(self, tr("warning"), tr("please_select_week"))
                return
            
            week = self.week_combo.itemData(week_index)
            if not week:
                return
            
            # Create image
            cell_width = 200
            cell_height = 100
            header_height = 40
            row_count = max(len(day.items) for day in week.days) + 1
            
            img_width = 6 * cell_width
            img_height = header_height + row_count * cell_height
            
            img = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw header
            days = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
            for i, day_name in enumerate(days):
                x = i * cell_width
                draw.rectangle([x, 0, x + cell_width, header_height], 
                              fill='gray', outline='black')
                # Note: Font rendering would need a font file
                # For simplicity, using basic text
                draw.text((x + 10, header_height // 2 - 10), day_name, fill='white')
            
            # Draw cells
            for day_index, day in enumerate(week.days):
                for item_index, item in enumerate(day.items):
                    x = day_index * cell_width
                    y = header_height + item_index * cell_height
                    
                    draw.rectangle([x, y, x + cell_width, y + cell_height],
                                  outline='black')
                    
                    text = self._format_item_display(item)
                    draw.text((x + 5, y + 5), text, fill='black')
            
            img.save(file_path)
            QMessageBox.information(self, "Thành công", f"Đã xuất ảnh: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất ảnh: {str(e)}")

