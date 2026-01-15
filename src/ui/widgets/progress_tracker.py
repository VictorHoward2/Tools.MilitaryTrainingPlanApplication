"""Progress tracker widget"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QGroupBox,
    QCalendarWidget, QMessageBox, QCheckBox, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date, datetime
from typing import List, Optional, Dict
from src.models.schedule import Schedule, DaySchedule, ScheduleItem
from src.services.schedule_service import ScheduleService


class ProgressTracker(QWidget):
    """Widget for tracking teaching progress"""
    
    def __init__(self, schedule_service: ScheduleService, parent=None):
        """Initialize progress tracker"""
        super().__init__(parent)
        self.schedule_service = schedule_service
        self.current_schedule: Optional[Schedule] = None
        self.setup_ui()
        self.load_schedules()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Schedule selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Chọn thời khóa biểu:"))
        self.schedule_combo = QComboBox()
        self.schedule_combo.currentIndexChanged.connect(self.on_schedule_changed)
        selection_layout.addWidget(self.schedule_combo)
        
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.load_schedules)
        selection_layout.addWidget(self.refresh_btn)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Two column layout
        main_layout = QHBoxLayout()
        
        # Left: Calendar and history
        left_layout = QVBoxLayout()
        
        # Calendar
        calendar_group = QGroupBox("Lịch")
        calendar_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
        calendar_group.setLayout(calendar_layout)
        left_layout.addWidget(calendar_group)
        
        # Today's schedule
        today_group = QGroupBox("Hôm nay")
        today_layout = QVBoxLayout()
        self.today_label = QLabel("Chưa có lịch")
        today_layout.addWidget(self.today_label)
        self.mark_complete_btn = QPushButton("Đánh dấu đã hoàn thành")
        self.mark_complete_btn.clicked.connect(self.mark_today_complete)
        self.mark_complete_btn.setEnabled(False)
        today_layout.addWidget(self.mark_complete_btn)
        today_group.setLayout(today_layout)
        left_layout.addWidget(today_group)
        
        main_layout.addLayout(left_layout, 1)
        
        # Right: Progress table
        right_layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Hiển thị:"))
        self.show_completed_check = QCheckBox("Đã hoàn thành")
        self.show_completed_check.setChecked(True)
        self.show_completed_check.stateChanged.connect(self.update_progress_table)
        self.show_pending_check = QCheckBox("Chưa hoàn thành")
        self.show_pending_check.setChecked(True)
        self.show_pending_check.stateChanged.connect(self.update_progress_table)
        filter_layout.addWidget(self.show_completed_check)
        filter_layout.addWidget(self.show_pending_check)
        filter_layout.addStretch()
        
        # Button to mark all past dates as completed
        self.mark_all_past_complete_btn = QPushButton("Đánh dấu tất cả ngày quá khứ")
        self.mark_all_past_complete_btn.clicked.connect(self.mark_all_past_dates_complete)
        self.mark_all_past_complete_btn.setEnabled(False)
        filter_layout.addWidget(self.mark_all_past_complete_btn)
        
        right_layout.addLayout(filter_layout)
        
        # Progress table
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(5)
        self.progress_table.setHorizontalHeaderLabels([
            "Ngày", "Thời gian", "Môn học", "Bài học", "Trạng thái"
        ])
        header = self.progress_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.progress_table)
        
        main_layout.addLayout(right_layout, 2)
        layout.addLayout(main_layout)
        
        self.setLayout(layout)
    
    def load_schedules(self):
        """Load all schedules"""
        self.schedule_combo.clear()
        schedules = self.schedule_service.get_all_schedules()
        
        for schedule in schedules:
            name = schedule.name or f"Thời khóa biểu {schedule.start_date}"
            self.schedule_combo.addItem(name, schedule)
        
        if schedules:
            self.on_schedule_changed(0)
    
    def on_schedule_changed(self, index):
        """Handle schedule selection change"""
        if index < 0:
            return
        
        self.current_schedule = self.schedule_combo.itemData(index)
        if self.current_schedule:
            self.update_calendar()
            self.update_today_schedule()
            self.update_progress_table()
            self.mark_all_past_complete_btn.setEnabled(True)
        else:
            self.mark_all_past_complete_btn.setEnabled(False)
    
    def update_calendar(self):
        """Update calendar with schedule dates"""
        if not self.current_schedule:
            return
        
        # Mark dates with schedule
        for week in self.current_schedule.weeks:
            for day in week.days:
                qdate = QDate(day.date.year, day.date.month, day.date.day)
                if day.is_completed:
                    # Mark completed days differently
                    self.calendar.setDateTextFormat(qdate, 
                        self.calendar.dateTextFormat(qdate))  # Could add custom format
    
    def update_today_schedule(self):
        """Update today's schedule display"""
        today = date.today()
        
        if not self.current_schedule:
            self.today_label.setText("Chưa có lịch")
            self.mark_complete_btn.setEnabled(False)
            return
        
        # Find today's schedule
        today_schedule = None
        for week in self.current_schedule.weeks:
            for day in week.days:
                if day.date == today:
                    today_schedule = day
                    break
            if today_schedule:
                break
        
        if not today_schedule or not today_schedule.items:
            self.today_label.setText("Hôm nay không có lịch")
            self.mark_complete_btn.setEnabled(False)
            return
        
        # Build schedule text
        text = f"<b>Hôm nay ({today.strftime('%d/%m/%Y')}):</b><br>"
        for item in today_schedule.items:
            text += f"• {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}: "
            text += f"{item.subject_name} - {item.lesson_name}<br>"
        
        self.today_label.setText(text)
        self.mark_complete_btn.setEnabled(not today_schedule.is_completed)
    
    def on_date_selected(self, qdate: QDate):
        """Handle date selection"""
        selected_date = qdate.toPython()
        self.show_date_schedule(selected_date)
    
    def show_date_schedule(self, selected_date: date):
        """Show schedule for selected date"""
        if not self.current_schedule:
            return
        
        # Find schedule for date
        day_schedule = None
        for week in self.current_schedule.weeks:
            for day in week.days:
                if day.date == selected_date:
                    day_schedule = day
                    break
            if day_schedule:
                break
        
        if not day_schedule:
            QMessageBox.information(
                self, "Thông tin", 
                f"Ngày {selected_date.strftime('%d/%m/%Y')} không có lịch"
            )
            return
        
        # Show schedule
        text = f"<b>Lịch ngày {selected_date.strftime('%d/%m/%Y')}:</b><br>"
        if day_schedule.is_completed:
            text += "<b style='color: green;'>✓ Đã hoàn thành</b><br><br>"
        
        for item in day_schedule.items:
            text += f"• {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}: "
            text += f"{item.subject_name} - {item.lesson_name}<br>"
        
        QMessageBox.information(self, "Lịch giảng dạy", text)
    
    def mark_today_complete(self):
        """Mark today's schedule as completed"""
        today = date.today()
        
        if not self.current_schedule:
            return
        
        # Find today's schedule
        today_schedule = None
        week_index = None
        day_index = None
        
        for w_idx, week in enumerate(self.current_schedule.weeks):
            for d_idx, day in enumerate(week.days):
                if day.date == today:
                    today_schedule = day
                    week_index = w_idx
                    day_index = d_idx
                    break
            if today_schedule:
                break
        
        if not today_schedule:
            QMessageBox.warning(self, "Cảnh báo", "Hôm nay không có lịch")
            return
        
        if today_schedule.is_completed:
            QMessageBox.information(self, "Thông tin", "Ngày này đã được đánh dấu hoàn thành")
            return
        
        # Mark as completed
        today_schedule.is_completed = True
        
        # Save schedule
        success, error = self.schedule_service.save_schedule(self.current_schedule)
        if success:
            QMessageBox.information(self, "Thành công", "Đã đánh dấu hoàn thành")
            self.update_today_schedule()
            self.update_progress_table()
        else:
            QMessageBox.warning(self, "Lỗi", error or "Không thể lưu")
    
    def update_progress_table(self):
        """Update progress table"""
        if not self.current_schedule:
            self.progress_table.setRowCount(0)
            return
        
        # Collect all schedule items
        items_data = []
        for week in self.current_schedule.weeks:
            for day in week.days:
                for item in day.items:
                    items_data.append({
                        "date": day.date,
                        "item": item,
                        "completed": day.is_completed
                    })
        
        # Filter
        show_completed = self.show_completed_check.isChecked()
        show_pending = self.show_pending_check.isChecked()
        
        filtered_data = [
            data for data in items_data
            if (data["completed"] and show_completed) or 
               (not data["completed"] and show_pending)
        ]
        
        # Sort by date
        filtered_data.sort(key=lambda x: x["date"])
        
        # Update table
        self.progress_table.setRowCount(len(filtered_data))
        for row, data in enumerate(filtered_data):
            day_date = data["date"]
            item = data["item"]
            completed = data["completed"]
            
            self.progress_table.setItem(
                row, 0, QTableWidgetItem(day_date.strftime("%d/%m/%Y"))
            )
            time_str = f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}"
            self.progress_table.setItem(row, 1, QTableWidgetItem(time_str))
            self.progress_table.setItem(row, 2, QTableWidgetItem(item.subject_name))
            self.progress_table.setItem(row, 3, QTableWidgetItem(item.lesson_name))
            
            status = "✓ Đã hoàn thành" if completed else "⏳ Chưa hoàn thành"
            status_item = QTableWidgetItem(status)
            if completed:
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.progress_table.setItem(row, 4, status_item)
    
    def mark_all_past_dates_complete(self):
        """Mark all past dates as completed"""
        if not self.current_schedule:
            return
        
        today = date.today()
        marked_count = 0
        
        # Iterate through all weeks and days
        for week in self.current_schedule.weeks:
            for day in week.days:
                # Check if date is in the past and not already completed
                if day.date < today and not day.is_completed:
                    day.is_completed = True
                    marked_count += 1
        
        if marked_count == 0:
            QMessageBox.information(
                self, "Thông tin", 
                "Không có ngày quá khứ nào cần đánh dấu hoàn thành"
            )
            return
        
        # Save schedule
        success, error = self.schedule_service.save_schedule(self.current_schedule)
        if success:
            QMessageBox.information(
                self, "Thành công", 
                f"Đã đánh dấu {marked_count} ngày quá khứ là hoàn thành"
            )
            self.update_calendar()
            self.update_today_schedule()
            self.update_progress_table()
        else:
            QMessageBox.warning(self, "Lỗi", error or "Không thể lưu")

