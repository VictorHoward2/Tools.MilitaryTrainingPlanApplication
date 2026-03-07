"""Schedule creator widget"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QGroupBox, QDialog, QDialogButtonBox,
    QStackedWidget, QHeaderView, QListView
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date, time
from typing import Optional, List, Tuple
from src.models.schedule import Schedule
from src.models.schedule import DaySchedule, ScheduleItem
from src.models.subject import (
    Subject, SUBJECT_CATEGORY_MAIN, 
    SUBJECT_CATEGORY_QUAN_SU, SUBJECT_CATEGORY_HAU_CAN_KY_THUAT
)
from src.models.lesson import Lesson
from src.services.schedule_service import ScheduleService
from src.services.subject_service import SubjectService
from src.utils.i18n import tr
from src.utils.logger import setup_logger

logger = setup_logger()


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
        self.current_step_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Date selection
        date_group = QGroupBox(tr("choose_time"))
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel(tr("start_date_monday")))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel(tr("end_date_sunday")))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(6))
        date_layout.addWidget(self.end_date_edit)
        
        self.create_schedule_btn = QPushButton(tr("create_schedule_button"))
        self.create_schedule_btn.clicked.connect(self.create_schedule)
        date_layout.addWidget(self.create_schedule_btn)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Week navigation
        week_nav_layout = QHBoxLayout()
        self.prev_week_btn = QPushButton(tr("prev_week"))
        self.prev_week_btn.clicked.connect(self.prev_week)
        self.prev_week_btn.setEnabled(False)
        
        self.week_label = QLabel(f"{tr('week')} 1")
        self.week_label.setAlignment(Qt.AlignCenter)
        
        self.next_week_btn = QPushButton(tr("next_week"))
        self.next_week_btn.clicked.connect(self.next_week)
        self.next_week_btn.setEnabled(False)
        
        week_nav_layout.addWidget(self.prev_week_btn)
        week_nav_layout.addWidget(self.week_label)
        week_nav_layout.addWidget(self.next_week_btn)
        layout.addLayout(week_nav_layout)
        
        # Step label
        self.step_label = QLabel("Bước 1/3: Chọn môn học theo ngày")
        layout.addWidget(self.step_label)

        # Step content
        self.step_stack = QStackedWidget()
        layout.addWidget(self.step_stack)

        # Step 1 - Select subjects
        self.subject_table = self._create_schedule_table()
        self.subject_table.cellDoubleClicked.connect(self.on_subject_table_double_clicked)
        step1_container = QWidget()
        step1_layout = QVBoxLayout()
        step1_layout.addWidget(self.subject_table)
        step1_container.setLayout(step1_layout)
        self.step_stack.addWidget(step1_container)

        # Step 2 - Order subjects and set time
        self.order_table = self._create_schedule_table()
        step2_container = QWidget()
        step2_layout = QVBoxLayout()
        step2_layout.addWidget(self.order_table)
        step2_container.setLayout(step2_layout)
        self.step_stack.addWidget(step2_container)

        # Step 3 - Pick lessons
        self.lesson_table = self._create_schedule_table()
        self.lesson_table.cellDoubleClicked.connect(self.on_lesson_table_double_clicked)
        step3_container = QWidget()
        step3_layout = QVBoxLayout()
        step3_layout.addWidget(self.lesson_table)
        step3_container.setLayout(step3_layout)
        self.step_stack.addWidget(step3_container)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.add_subject_btn = QPushButton("Thêm môn học")
        self.add_subject_btn.clicked.connect(self.add_subject_to_day)
        self.add_subject_btn.setEnabled(False)

        self.remove_subject_btn = QPushButton("Xóa môn học")
        self.remove_subject_btn.clicked.connect(self.remove_subject_from_day)
        self.remove_subject_btn.setEnabled(False)

        self.copy_prev_week_btn = QPushButton("Xếp môn học giống tuần trước")
        self.copy_prev_week_btn.clicked.connect(self.copy_previous_week_subjects)
        self.copy_prev_week_btn.setEnabled(False)

        self.move_up_btn = QPushButton("Lên")
        self.move_up_btn.clicked.connect(self.move_subject_up)
        self.move_up_btn.setEnabled(False)

        self.move_down_btn = QPushButton("Xuống")
        self.move_down_btn.clicked.connect(self.move_subject_down)
        self.move_down_btn.setEnabled(False)

        self.choose_lesson_btn = QPushButton("Chọn bài học")
        self.choose_lesson_btn.clicked.connect(self.choose_lesson_for_subject)
        self.choose_lesson_btn.setEnabled(False)

        self.auto_fill_btn = QPushButton(tr("auto_fill_times_lessons"))
        self.auto_fill_btn.clicked.connect(self.auto_fill_week_times_and_lessons)
        self.auto_fill_btn.setEnabled(False)

        self.prev_step_btn = QPushButton("Quay lại")
        self.prev_step_btn.clicked.connect(self.prev_step)
        self.prev_step_btn.setEnabled(False)

        self.next_step_btn = QPushButton("Tiếp theo")
        self.next_step_btn.clicked.connect(self.next_step)
        self.next_step_btn.setEnabled(False)

        self.validate_btn = QPushButton(tr("validate"))
        self.validate_btn.clicked.connect(self.validate_current_week)
        self.validate_btn.setEnabled(False)

        self.save_btn = QPushButton("Lưu thời khóa biểu")
        self.save_btn.clicked.connect(self.save_schedule)
        self.save_btn.setEnabled(False)

        action_layout.addWidget(self.add_subject_btn)
        action_layout.addWidget(self.remove_subject_btn)
        action_layout.addWidget(self.copy_prev_week_btn)
        action_layout.addWidget(self.move_up_btn)
        action_layout.addWidget(self.move_down_btn)
        action_layout.addWidget(self.choose_lesson_btn)
        action_layout.addWidget(self.auto_fill_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.prev_step_btn)
        action_layout.addWidget(self.next_step_btn)
        action_layout.addWidget(self.validate_btn)
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
            QMessageBox.warning(self, tr("error"), tr("end_date_must_be_sunday"))
            return
        
        if start_date >= end_date:
            QMessageBox.warning(self, tr("error"), tr("start_date_before_end_date"))
            return
        
        try:
            self.current_schedule = self.schedule_service.create_schedule(
                start_date, end_date, f"{tr('schedule')} {start_date} - {end_date}"
            )
            self.current_week_index = 0
            self.current_step_index = 0
            self.update_ui()
            QMessageBox.information(self, tr("success"), tr("schedule_created"))
        except Exception as e:
            QMessageBox.warning(self, tr("error"), tr("cannot_create_schedule").format(error=str(e)))
    
    def update_ui(self):
        """Update UI with current week"""
        if not self.current_schedule:
            return
        
        if self.current_week_index >= len(self.current_schedule.weeks):
            return
        
        week = self.current_schedule.weeks[self.current_week_index]
        self.week_label.setText(f"{tr('week')} {week.week_number} ({week.start_date} - {week.end_date})")
        
        # Enable/disable navigation
        self.prev_week_btn.setEnabled(self.current_week_index > 0)
        self.next_week_btn.setEnabled(
            self.current_week_index < len(self.current_schedule.weeks) - 1
        )
        
        # Enable action buttons
        self.add_subject_btn.setEnabled(True)
        self.remove_subject_btn.setEnabled(True)
        self.copy_prev_week_btn.setEnabled(self.current_week_index > 0)
        self.prev_step_btn.setEnabled(self.current_step_index > 0)
        self.next_step_btn.setEnabled(self.current_step_index < 2)
        self.validate_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        self.update_step_ui()
    
    def prev_week(self):
        """Go to previous week"""
        if self.current_week_index > 0:
            self.current_week_index -= 1
            self.current_step_index = 0
            self.update_ui()
    
    def next_week(self):
        """Go to next week"""
        if self.current_schedule and \
           self.current_week_index < len(self.current_schedule.weeks) - 1:
            self.current_week_index += 1
            self.current_step_index = 0
            self.update_ui()

    def _create_schedule_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            tr("monday"), tr("tuesday"), tr("wednesday"),
            tr("thursday"), tr("friday"), tr("saturday")
        ])
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(20)
        return table

    def update_step_ui(self):
        if not self.current_schedule:
            return

        step_text = [
            "Bước 1/3: Chọn môn học theo ngày",
            "Bước 2/3: Sắp xếp thứ tự môn học",
            "Bước 3/3: Chọn bài học và giờ học cho từng môn",
        ]
        self.step_label.setText(step_text[self.current_step_index])
        self.step_stack.setCurrentIndex(self.current_step_index)

        in_step1 = self.current_step_index == 0
        in_step2 = self.current_step_index == 1
        in_step3 = self.current_step_index == 2

        self.add_subject_btn.setEnabled(in_step1)
        self.remove_subject_btn.setEnabled(in_step1)
        self.copy_prev_week_btn.setEnabled(in_step1 and self.current_week_index > 0)

        self.move_up_btn.setEnabled(in_step2)
        self.move_down_btn.setEnabled(in_step2)
        self.choose_lesson_btn.setEnabled(in_step3)
        has_any_subjects = any(
            len(day.selected_subject_ids) > 0
            for day in self.current_schedule.weeks[self.current_week_index].days
        )
        self.auto_fill_btn.setEnabled((in_step2 or in_step3) and has_any_subjects)

        self.refresh_subject_table()
        self.refresh_order_table()
        self.refresh_lesson_table()

    def next_step(self):
        if self.current_step_index < 2:
            self.current_step_index += 1
            self.prev_step_btn.setEnabled(self.current_step_index > 0)
            self.next_step_btn.setEnabled(self.current_step_index < 2)
            self.update_step_ui()

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.prev_step_btn.setEnabled(self.current_step_index > 0)
            self.next_step_btn.setEnabled(self.current_step_index < 2)
            self.update_step_ui()

    def refresh_subject_table(self):
        if not self.current_schedule:
            return
        week = self.current_schedule.weeks[self.current_week_index]
        self.subject_table.clearContents()
        for day_index, day in enumerate(week.days):
            row = 0
            for fixed_item in self._get_fixed_items(day):
                if row >= self.subject_table.rowCount():
                    self.subject_table.setRowCount(row + 1)
                table_item = QTableWidgetItem(self._format_fixed_item_display(fixed_item))
                table_item.setFlags(Qt.ItemIsEnabled)
                self.subject_table.setItem(row, day_index, table_item)
                row += 1
            for subject_id in day.selected_subject_ids:
                if row >= self.subject_table.rowCount():
                    self.subject_table.setRowCount(row + 1)
                subject = self.subject_service.get_subject(subject_id)
                subject_name = subject.name if subject else "Môn học"
                table_item = QTableWidgetItem(subject_name)
                table_item.setData(Qt.UserRole, subject_id)
                self.subject_table.setItem(row, day_index, table_item)
                row += 1

    def refresh_order_table(self):
        if not self.current_schedule:
            return
        week = self.current_schedule.weeks[self.current_week_index]
        self.order_table.clearContents()
        for day_index, day in enumerate(week.days):
            row = 0
            for fixed_item in self._get_fixed_items(day):
                if row >= self.order_table.rowCount():
                    self.order_table.setRowCount(row + 1)
                table_item = QTableWidgetItem(self._format_fixed_item_display(fixed_item))
                table_item.setFlags(Qt.ItemIsEnabled)
                self.order_table.setItem(row, day_index, table_item)
                row += 1
            for subject_id in day.selected_subject_ids:
                if row >= self.order_table.rowCount():
                    self.order_table.setRowCount(row + 1)
                subject = self.subject_service.get_subject(subject_id)
                subject_name = subject.name if subject else "Môn học"
                table_item = QTableWidgetItem(subject_name)
                table_item.setData(Qt.UserRole, subject_id)
                self.order_table.setItem(row, day_index, table_item)
                row += 1

    def refresh_lesson_table(self):
        if not self.current_schedule:
            return
        week = self.current_schedule.weeks[self.current_week_index]
        self.lesson_table.clearContents()
        for day_index, day in enumerate(week.days):
            row = 0
            for fixed_item in self._get_fixed_items(day):
                if row >= self.lesson_table.rowCount():
                    self.lesson_table.setRowCount(row + 1)
                table_item = QTableWidgetItem(self._format_fixed_item_display(fixed_item))
                table_item.setFlags(Qt.ItemIsEnabled)
                self.lesson_table.setItem(row, day_index, table_item)
                row += 1
            for subject_id in day.selected_subject_ids:
                lesson_ids = day.get_lesson_ids(subject_id)
                time_slots = day.get_time_slots(subject_id)
                slot_count = max(len(lesson_ids), len(time_slots), 1)
                for slot_index in range(slot_count):
                    if row >= self.lesson_table.rowCount():
                        self.lesson_table.setRowCount(row + 1)
                    subject = self.subject_service.get_subject(subject_id)
                    subject_name = subject.name if subject else "Môn học"
                    lesson_id = lesson_ids[slot_index] if slot_index < len(lesson_ids) else None
                    lesson_name = ""
                    if subject and lesson_id:
                        lesson = next((l for l in subject.lessons if l.lesson_id == lesson_id), None)
                        lesson_name = lesson.name if lesson else ""
                    time_str = time_slots[slot_index] if slot_index < len(time_slots) else ""
                    text = subject_name
                    if time_str and lesson_name and subject:
                        try:
                            hour, minute = map(int, time_str.split(":"))
                            start_time = time(hour, minute)
                            les = next((l for l in subject.lessons if l.lesson_id == lesson_id), None) if lesson_id else None
                            duration = subject.get_lesson_duration(les) if les else (subject.default_duration or 0)
                            if duration:
                                from src.utils.date_utils import add_hours_to_time
                                end_time = add_hours_to_time(start_time, duration)
                                text = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}: {subject_name}: {lesson_name}"
                            else:
                                text = f"{time_str}: {subject_name}: {lesson_name}"
                        except Exception:
                            text = f"{time_str}: {subject_name}: {lesson_name}" if time_str or lesson_name else subject_name
                    elif lesson_name:
                        text = f"{subject_name}: {lesson_name}"
                    table_item = QTableWidgetItem(text)
                    table_item.setData(Qt.UserRole, (subject_id, slot_index))
                    self.lesson_table.setItem(row, day_index, table_item)
                    row += 1

    def on_subject_table_double_clicked(self, row: int, col: int):
        self.add_subject_to_day(preselected_day=col)

    def on_lesson_table_double_clicked(self, row: int, col: int):
        self.choose_lesson_for_subject()

    def add_subject_to_day(self, preselected_day: Optional[int] = None):
        if not self.current_schedule:
            return

        dialog = AddSubjectDialog(self.subject_service, preselected_day, self)
        if not dialog.exec():
            return
        day_index, subject = dialog.get_selection()
        if subject is None:
            return

        week_num = self.current_week_index + 1
        week = self.current_schedule.weeks[self.current_week_index]
        day = week.days[day_index]
        if subject.subject_id in day.selected_subject_ids:
            QMessageBox.warning(self, tr("error"), "Môn học đã được chọn trong ngày")
            return

        new_subjects = list(day.selected_subject_ids)
        new_subjects.append(subject.subject_id)
        success, error = self.schedule_service.set_day_subjects(
            self.current_schedule, week_num, day_index, new_subjects
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or "Không thể thêm môn học")
            return
        self.update_step_ui()

    def remove_subject_from_day(self):
        if not self.current_schedule:
            return
        table = self.subject_table
        current = table.currentItem()
        if not current:
            QMessageBox.warning(self, tr("error"), "Vui lòng chọn môn học để xóa")
            return
        subject_id = current.data(Qt.UserRole)
        if not subject_id:
            QMessageBox.warning(self, tr("error"), "Không thể xóa môn học cố định")
            return
        day_index = current.column()
        week = self.current_schedule.weeks[self.current_week_index]
        day = week.days[day_index]
        if subject_id not in day.selected_subject_ids:
            return
        new_subjects = list(day.selected_subject_ids)
        new_subjects.remove(subject_id)
        success, error = self.schedule_service.set_day_subjects(
            self.current_schedule, self.current_week_index + 1, day_index, new_subjects
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or "Không thể xóa môn học")
            return
        self.update_step_ui()

    def move_subject_up(self):
        self._move_subject_in_order(-1)

    def move_subject_down(self):
        self._move_subject_in_order(1)

    def _move_subject_in_order(self, delta: int):
        if not self.current_schedule:
            return
        table = self.order_table
        current = table.currentItem()
        if not current:
            QMessageBox.warning(self, tr("error"), "Vui lòng chọn môn học để sắp xếp")
            return
        subject_id = current.data(Qt.UserRole)
        if not subject_id:
            QMessageBox.warning(self, tr("error"), "Không thể sắp xếp môn học cố định")
            return
        day_index = current.column()
        week = self.current_schedule.weeks[self.current_week_index]
        day = week.days[day_index]
        if subject_id not in day.selected_subject_ids:
            return
        current_index = day.selected_subject_ids.index(subject_id)
        new_index = current_index + delta
        if new_index < 0 or new_index >= len(day.selected_subject_ids):
            return
        
        # Calculate number of fixed items for this day (needed to determine correct row)
        fixed_items_count = len(self._get_fixed_items(day))
        
        new_subjects = list(day.selected_subject_ids)
        subject_id = new_subjects.pop(current_index)
        new_subjects.insert(new_index, subject_id)
        success, error = self.schedule_service.set_day_subjects(
            self.current_schedule, self.current_week_index + 1, day_index, new_subjects
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or "Không thể sắp xếp môn học")
            return
        self.update_step_ui()
        
        # Calculate the actual row number: fixed items + new_index in selected_subject_ids
        actual_row = fixed_items_count + new_index
        table.setCurrentCell(actual_row, day_index)
        # Ensure the selected cell is visible
        item = table.item(actual_row, day_index)
        if item:
            table.scrollToItem(item)


    def choose_lesson_for_subject(self):
        if not self.current_schedule:
            return
        table = self.lesson_table
        current = table.currentItem()
        if not current:
            QMessageBox.warning(self, tr("error"), "Vui lòng chọn môn học để chọn bài")
            return
        role_data = current.data(Qt.UserRole)
        if isinstance(role_data, tuple):
            subject_id, slot_index = role_data
        else:
            subject_id, slot_index = role_data, 0
        if not subject_id:
            QMessageBox.warning(self, tr("error"), "Không thể chọn bài cho môn học cố định")
            return
        day_index = current.column()
        week = self.current_schedule.weeks[self.current_week_index]
        day = week.days[day_index]
        if subject_id not in day.selected_subject_ids:
            return
        subject = self.subject_service.get_subject(subject_id)
        if not subject:
            QMessageBox.warning(self, tr("error"), "Không tìm thấy môn học")
            return

        default_start_time = self._calculate_default_start_time(day, subject_id, slot_index)
        time_slots = day.get_time_slots(subject_id)
        current_time = None
        if slot_index < len(time_slots) and time_slots[slot_index]:
            try:
                hour, minute = map(int, time_slots[slot_index].split(":"))
                current_time = time(hour, minute)
            except Exception:
                pass
        lesson_ids = day.get_lesson_ids(subject_id)
        current_lesson_id = lesson_ids[slot_index] if slot_index < len(lesson_ids) else None

        dialog = ChooseLessonDialog(
            subject,
            current_lesson_id,
            default_start_time,
            current_time,
            day.date,
            self.schedule_service,
            self
        )
        if not dialog.exec():
            return
        lesson, selected_time = dialog.get_selection()
        if not lesson:
            return

        if selected_time:
            success, error = self.schedule_service.set_day_subject_time(
                self.current_schedule, self.current_week_index + 1, day_index, subject_id, selected_time, slot_index
            )
            if not success:
                QMessageBox.warning(self, tr("error"), error or "Không thể đặt giờ")
                return
        success, error = self.schedule_service.set_day_subject_lesson(
            self.current_schedule, self.current_week_index + 1, day_index, subject_id, lesson.lesson_id, slot_index
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or "Không thể chọn bài học")
            return
        self.update_step_ui()
    
    def _calculate_default_start_time(self, day: 'DaySchedule', subject_id: str, slot_index: int) -> time:
        """Calculate default start time for a subject slot (uses season times for this day)."""
        from src.utils.date_utils import add_hours_to_time
        times = self.schedule_service.get_schedule_times_for_date(day.date)
        morning_start = times["morning_start"]

        if slot_index == 0:
            try:
                idx = day.selected_subject_ids.index(subject_id)
            except ValueError:
                idx = 0
            if idx == 0:
                return morning_start
            prev_id = day.selected_subject_ids[idx - 1]
            slots = day.get_time_slots(prev_id)
            lessons = day.get_lesson_ids(prev_id)
            if not slots:
                return morning_start
            last_start_str = slots[-1]
            try:
                h, m = map(int, last_start_str.split(":"))
                last_start = time(h, m)
            except Exception:
                return morning_start
            prev_subject = self.subject_service.get_subject(prev_id)
            if not prev_subject:
                return morning_start
            if lessons and len(lessons) <= len(slots):
                last_lesson_id = lessons[-1]
                last_lesson = next((l for l in prev_subject.lessons if l.lesson_id == last_lesson_id), None)
                dur = prev_subject.get_lesson_duration(last_lesson) if last_lesson else (prev_subject.default_duration or 0)
            else:
                dur = prev_subject.default_duration or 0
            return add_hours_to_time(last_start, dur)

        time_slots = day.get_time_slots(subject_id)
        lesson_ids = day.get_lesson_ids(subject_id)
        if slot_index > 0 and slot_index <= len(time_slots) and slot_index <= len(lesson_ids):
            prev_start_str = time_slots[slot_index - 1]
            prev_lesson_id = lesson_ids[slot_index - 1]
            try:
                h, m = map(int, prev_start_str.split(":"))
                prev_start = time(h, m)
            except Exception:
                return morning_start
            subj = self.subject_service.get_subject(subject_id)
            if subj:
                prev_lesson = next((l for l in subj.lessons if l.lesson_id == prev_lesson_id), None)
                dur = subj.get_lesson_duration(prev_lesson) if prev_lesson else (subj.default_duration or 0)
                return add_hours_to_time(prev_start, dur)
        return morning_start

    def copy_previous_week_subjects(self):
        if not self.current_schedule or self.current_week_index <= 0:
            return
        success, error = self.schedule_service.copy_week_subjects_and_times(
            self.current_schedule, self.current_week_index, self.current_week_index + 1
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or "Không thể sao chép tuần trước")
            return
        self.current_step_index = 2
        self.update_step_ui()

    def auto_fill_week_times_and_lessons(self):
        """Auto-fill subject_time_slots and subject_lesson_map for current week."""
        if not self.current_schedule:
            return
        success, error, days_with_issues = self.schedule_service.auto_fill_week_times_and_lessons(
            self.current_schedule, self.current_week_index + 1
        )
        if not success:
            QMessageBox.warning(self, tr("error"), error or tr("auto_fill_failed"))
            return
        self.update_step_ui()
        if days_with_issues:
            lines = [f"{name} ({date}): {suggestion}" for name, date, suggestion in days_with_issues]
            message = (
                tr("auto_fill_done")
                + "\n\n"
                + tr("auto_fill_some_days_short")
                + "\n\n"
                + "\n".join(lines)
            )
            QMessageBox.warning(self, tr("validate_warning_title"), message)
        else:
            QMessageBox.information(self, tr("success"), tr("auto_fill_done"))

    def validate_current_week(self):
        """Validate current week schedule. Gom tất cả kiểm tra (thiếu thông tin, trùng giờ, không đủ tổng giờ) vào một."""
        if not self.current_schedule:
            return

        week_num = self.current_week_index + 1
        schedule_label = self.current_schedule.name or getattr(self.current_schedule, "schedule_id", "") or "TKB"

        is_valid, issues = self.schedule_service.validate_week_schedule(
            self.current_schedule, week_num
        )

        if not is_valid:
            logger.error(
                "[Kiểm tra TKB] Tuần %s (%s): phát hiện %s vấn đề.\n%s",
                week_num, schedule_label, len(issues), "\n".join(issues)
            )
            message = (
                f"Tuần {week_num}: phát hiện {len(issues)} vấn đề.\n\n"
                + "\n\n".join(issues)
                + "\n\nChi tiết đã ghi trong file log (thư mục logs/)."
            )
            QMessageBox.warning(self, tr("validate_warning_title"), message)
        else:
            QMessageBox.information(self, tr("success"), tr("week_schedule_valid"))
    
    def save_schedule(self):
        """Save schedule"""
        if not self.current_schedule:
            return

        for week_index in range(len(self.current_schedule.weeks)):
            success, error, _ = self.schedule_service.build_week_items(
                self.current_schedule, week_index + 1
            )
            if not success:
                QMessageBox.warning(self, tr("error"), error or "Không thể tạo kế hoạch huấn luyện")
                return

        success, error = self.schedule_service.save_schedule(self.current_schedule)
        if success:
            QMessageBox.information(self, tr("success"), tr("schedule_saved"))
            self.schedule_created.emit(self.current_schedule)
        else:
            QMessageBox.warning(self, tr("error"), error or tr("cannot_save_schedule"))

    def _get_fixed_items(self, day: 'DaySchedule') -> List['ScheduleItem']:
        """Get fixed items for display (no subject/lesson ids)."""
        return [
            item for item in day.items 
            if not item.subject_id and not item.lesson_id 
            and item.subject_name != "Nghỉ trưa"
        ]

    def _format_fixed_item_display(self, item: 'ScheduleItem') -> str:
        """Format fixed item text."""
        return (
            f"{item.start_time.strftime('%H:%M')} - "
            f"{item.end_time.strftime('%H:%M')}: {item.subject_name}"
        )


class AddSubjectDialog(QDialog):
    """Dialog for adding a subject to a day"""
    
    def __init__(self, subject_service: SubjectService,
                 preselected_day: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.subject_service = subject_service
        self.selected_day_index = preselected_day if preselected_day is not None else 0
        self.selected_subject = None
        self.all_subjects = []  # Store all subjects for filtering
        self.setWindowTitle("Thêm môn học")
        self.setModal(True)
        self.setup_ui()
        self._expand_width()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Lock combo widths and allow horizontal scroll for long items
        combo_fixed_width = 300
        
        def apply_combo_style(combo: QComboBox):
            combo.setFixedWidth(combo_fixed_width)
            view = QListView()
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            combo.setView(view)
        
        # Day selection
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Ngày:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"])
        self.day_combo.setCurrentIndex(self.selected_day_index)
        apply_combo_style(self.day_combo)
        day_layout.addWidget(self.day_combo)
        layout.addLayout(day_layout)

        # Category filters
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Phân loại môn học:"))
        self.category_main_combo = QComboBox()
        self.category_main_combo.addItem("Tất cả", None)
        for key, value in SUBJECT_CATEGORY_MAIN.items():
            self.category_main_combo.addItem(value, key)
        self.category_main_combo.currentIndexChanged.connect(self.on_category_main_changed)
        apply_combo_style(self.category_main_combo)
        category_layout.addWidget(self.category_main_combo)
        layout.addLayout(category_layout)

        subcategory_layout = QHBoxLayout()
        subcategory_layout.addWidget(QLabel("Phân loại phụ:"))
        self.category_sub_combo = QComboBox()
        self.category_sub_combo.addItem("Tất cả", None)
        self.category_sub_combo.currentIndexChanged.connect(self.on_category_sub_changed)
        apply_combo_style(self.category_sub_combo)
        subcategory_layout.addWidget(self.category_sub_combo)
        layout.addLayout(subcategory_layout)

        # Subject selection
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Môn học:"))
        self.subject_combo = QComboBox()
        apply_combo_style(self.subject_combo)
        subject_layout.addWidget(self.subject_combo)
        layout.addLayout(subject_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.load_subjects()

    def _expand_width(self):
        hint = self.sizeHint()
        self.resize(hint.width() + 50, hint.height())

    def load_subjects(self):
        """Load all subjects and populate the combo box"""
        self.all_subjects = self.subject_service.get_all_subjects()
        self.filter_subjects()

    def on_category_main_changed(self):
        """Handle main category selection change"""
        # Update sub-category dropdown based on main category
        self.category_sub_combo.clear()
        self.category_sub_combo.addItem("Tất cả", None)
        
        main_category = self.category_main_combo.currentData()
        if main_category == "QUAN_SU":
            for key, value in SUBJECT_CATEGORY_QUAN_SU.items():
                self.category_sub_combo.addItem(value, key)
        elif main_category == "HAU_CAN_KY_THUAT":
            for key, value in SUBJECT_CATEGORY_HAU_CAN_KY_THUAT.items():
                self.category_sub_combo.addItem(value, key)
        
        # Filter subjects when category changes
        self.filter_subjects()

    def on_category_sub_changed(self):
        """Handle sub-category selection change"""
        self.filter_subjects()

    def filter_subjects(self):
        """Filter subjects based on selected categories"""
        self.subject_combo.clear()
        self.subject_combo.addItem("", None)
        
        main_category = self.category_main_combo.currentData()
        sub_category = self.category_sub_combo.currentData()
        
        filtered_subjects = []
        for subject in self.all_subjects:
            # Filter by main category
            if main_category is not None:
                if subject.category_main != main_category:
                    continue
            
            # Filter by sub category
            if sub_category is not None:
                if subject.category_sub != sub_category:
                    continue
            
            filtered_subjects.append(subject)
        
        # Add filtered subjects to combo box
        for subject in filtered_subjects:
            self.subject_combo.addItem(subject.name, subject)

    def get_selection(self):
        day_index = self.day_combo.currentIndex()
        subject = self.subject_combo.currentData()
        return day_index, subject
    
    def accept(self):
        """Validate before accepting"""
        if not self.subject_combo.currentData():
            QMessageBox.warning(self, tr("error"), tr("please_select_subject"))
            return
        super().accept()


class ChooseLessonDialog(QDialog):
    """Dialog for choosing lesson and time for a subject (time range by season)."""

    def __init__(self, subject: Subject, current_lesson_id: Optional[str] = None,
                 default_start_time: Optional[time] = None, current_time: Optional[time] = None,
                 day_date: Optional[date] = None, schedule_service=None, parent=None):
        super().__init__(parent)
        self.subject = subject
        self.selected_lesson = None
        self.current_lesson_id = current_lesson_id
        self.day_date = day_date
        self.schedule_service = schedule_service
        self._times = None
        if day_date and schedule_service:
            self._times = schedule_service.get_schedule_times_for_date(day_date)
        self.default_start_time = default_start_time or (self._times["morning_start"] if self._times else time(7, 0))
        self.current_time = current_time
        self.setWindowTitle("Chọn bài học và giờ học")
        self.setModal(True)
        self.setup_ui()
        self._expand_width()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        combo_fixed_width = 300
        
        def apply_combo_style(combo: QComboBox):
            combo.setFixedWidth(combo_fixed_width)
            view = QListView()
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            combo.setView(view)
        
        start_time_layout = QHBoxLayout()
        start_time_layout.addWidget(QLabel("Giờ bắt đầu dự kiến:"))
        self.start_time_combo = QComboBox()
        # Time range by season: morning_start to afternoon_end (30-min steps)
        if self._times:
            start_t = self._times["morning_start"]
            end_t = self._times["afternoon_end"]
        else:
            start_t = time(7, 0)
            end_t = time(16, 30)
        start_minutes = start_t.hour * 60 + start_t.minute
        end_minutes = end_t.hour * 60 + end_t.minute
        for m in range(start_minutes, end_minutes + 1, 30):
            h, mn = divmod(m, 60)
            if h >= 24:
                break
            time_obj = time(h, mn)
            self.start_time_combo.addItem(time_obj.strftime("%H:%M"), time_obj)
        apply_combo_style(self.start_time_combo)
        start_time_layout.addWidget(self.start_time_combo)
        layout.addLayout(start_time_layout)
        
        start_time_to_use = self.current_time if self.current_time else self.default_start_time
        for i in range(self.start_time_combo.count()):
            if self.start_time_combo.itemData(i) == start_time_to_use:
                self.start_time_combo.setCurrentIndex(i)
                break
        else:
            # Clamp to nearest option
            for i in range(self.start_time_combo.count()):
                if self.start_time_combo.itemData(i) >= start_time_to_use:
                    self.start_time_combo.setCurrentIndex(i)
                    break
        
        # Lesson selection
        lesson_layout = QHBoxLayout()
        lesson_layout.addWidget(QLabel("Bài học:"))
        self.lesson_combo = QComboBox()
        self.lesson_combo.addItem("", None)
        for lesson in self.subject.lessons:
            duration = self.subject.get_lesson_duration(lesson)
            text = f"{lesson.name} ({duration:.1f}h)"
            self.lesson_combo.addItem(text, lesson)
            if self.current_lesson_id and lesson.lesson_id == self.current_lesson_id:
                self.lesson_combo.setCurrentIndex(self.lesson_combo.count() - 1)
        self.lesson_combo.currentIndexChanged.connect(self.on_lesson_changed)
        apply_combo_style(self.lesson_combo)
        lesson_layout.addWidget(self.lesson_combo)
        layout.addLayout(lesson_layout)
        
        # End time display (read-only)
        end_time_layout = QHBoxLayout()
        end_time_layout.addWidget(QLabel("Giờ kết thúc dự kiến:"))
        self.end_time_label = QLabel("")
        self.end_time_label.setStyleSheet("font-weight: bold;")
        end_time_layout.addWidget(self.end_time_label)
        layout.addLayout(end_time_layout)
        
        # Update end time when start time changes
        self.start_time_combo.currentIndexChanged.connect(self.update_end_time)
        
        # Initial end time calculation
        self.update_end_time()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _expand_width(self):
        hint = self.sizeHint()
        self.resize(hint.width() + 50, hint.height())
    
    def on_lesson_changed(self):
        """Update end time when lesson selection changes"""
        self.update_end_time()
    
    def update_end_time(self):
        """Calculate and display end time based on start time and lesson duration"""
        start_time = self.start_time_combo.currentData()
        if not start_time:
            self.end_time_label.setText("")
            return
        
        # Get duration from selected lesson or default duration
        duration = None
        selected_lesson = self.lesson_combo.currentData()
        if selected_lesson:
            duration = self.subject.get_lesson_duration(selected_lesson)
        elif self.subject.default_duration:
            duration = self.subject.default_duration
        
        if duration:
            from src.utils.date_utils import add_hours_to_time
            end_time = add_hours_to_time(start_time, duration)
            self.end_time_label.setText(end_time.strftime("%H:%M"))
        else:
            self.end_time_label.setText("")

    def get_selection(self) -> Tuple[Optional[Lesson], Optional[time]]:
        lesson = self.lesson_combo.currentData()
        start_time = self.start_time_combo.currentData()
        return lesson, start_time

    def accept(self):
        if not self.lesson_combo.currentData():
            QMessageBox.warning(self, tr("error"), tr("please_select_lesson"))
            return
        super().accept()

