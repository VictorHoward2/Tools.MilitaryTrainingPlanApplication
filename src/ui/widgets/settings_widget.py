"""Settings widget - season dates (dd/mm) and schedule times per season"""

from datetime import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QDateEdit, QTimeEdit
)
from PySide6.QtCore import Qt, QDate
from src.config.settings import Settings
from src.utils.i18n import tr
from src.utils.season_schedule import (
    DEFAULT_SUMMER_START_MONTH, DEFAULT_SUMMER_START_DAY,
    DEFAULT_SUMMER_END_MONTH, DEFAULT_SUMMER_END_DAY,
    SUMMER_SCHEDULE, WINTER_SCHEDULE,
)

# Year used for QDateEdit (we only care about month/day)
_DUMMY_YEAR = 2000


class SettingsWidget(QWidget):
    """Widget for app settings: season dates (dd/mm) and schedule times per season"""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_values()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Season date range: Ngày bắt đầu mùa hè: dd/mm, Ngày kết thúc mùa hè: dd/mm
        season_group = QGroupBox(tr("settings_season_dates"))
        season_layout = QFormLayout()
        season_layout.addRow(QLabel(tr("settings_summer_range_help")))

        self.summer_start_date = self._make_date_edit()
        season_layout.addRow(tr("settings_summer_start") + " (dd/mm):", self.summer_start_date)
        self.summer_end_date = self._make_date_edit()
        season_layout.addRow(tr("settings_summer_end") + " (dd/mm):", self.summer_end_date)

        season_group.setLayout(season_layout)
        layout.addWidget(season_group)

        # Editable schedule times: Mùa hè
        summer_group = QGroupBox(tr("settings_summer_times_group"))
        summer_layout = QFormLayout()
        self.summer_morning_start = QTimeEdit()
        self.summer_morning_start.setDisplayFormat("HH:mm")
        self.summer_morning_end = QTimeEdit()
        self.summer_morning_end.setDisplayFormat("HH:mm")
        self.summer_break_start = QTimeEdit()
        self.summer_break_start.setDisplayFormat("HH:mm")
        self.summer_break_end = QTimeEdit()
        self.summer_break_end.setDisplayFormat("HH:mm")
        self.summer_afternoon_start = QTimeEdit()
        self.summer_afternoon_start.setDisplayFormat("HH:mm")
        self.summer_afternoon_end = QTimeEdit()
        self.summer_afternoon_end.setDisplayFormat("HH:mm")
        summer_layout.addRow(tr("settings_morning_start"), self.summer_morning_start)
        summer_layout.addRow(tr("settings_morning_end"), self.summer_morning_end)
        summer_layout.addRow(tr("settings_break_start"), self.summer_break_start)
        summer_layout.addRow(tr("settings_break_end"), self.summer_break_end)
        summer_layout.addRow(tr("settings_afternoon_start"), self.summer_afternoon_start)
        summer_layout.addRow(tr("settings_afternoon_end"), self.summer_afternoon_end)
        summer_group.setLayout(summer_layout)
        layout.addWidget(summer_group)

        # Editable schedule times: Mùa đông
        winter_group = QGroupBox(tr("settings_winter_times_group"))
        winter_layout = QFormLayout()
        self.winter_morning_start = QTimeEdit()
        self.winter_morning_start.setDisplayFormat("HH:mm")
        self.winter_morning_end = QTimeEdit()
        self.winter_morning_end.setDisplayFormat("HH:mm")
        self.winter_break_start = QTimeEdit()
        self.winter_break_start.setDisplayFormat("HH:mm")
        self.winter_break_end = QTimeEdit()
        self.winter_break_end.setDisplayFormat("HH:mm")
        self.winter_afternoon_start = QTimeEdit()
        self.winter_afternoon_start.setDisplayFormat("HH:mm")
        self.winter_afternoon_end = QTimeEdit()
        self.winter_afternoon_end.setDisplayFormat("HH:mm")
        winter_layout.addRow(tr("settings_morning_start"), self.winter_morning_start)
        winter_layout.addRow(tr("settings_morning_end"), self.winter_morning_end)
        winter_layout.addRow(tr("settings_break_start"), self.winter_break_start)
        winter_layout.addRow(tr("settings_break_end"), self.winter_break_end)
        winter_layout.addRow(tr("settings_afternoon_start"), self.winter_afternoon_start)
        winter_layout.addRow(tr("settings_afternoon_end"), self.winter_afternoon_end)
        winter_group.setLayout(winter_layout)
        layout.addWidget(winter_group)

        # Save button
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton(tr("save"))
        self.save_btn.clicked.connect(self.save_values)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _make_date_edit(self) -> QDateEdit:
        """Create QDateEdit with dd/MM format (year = dummy)."""
        de = QDateEdit()
        de.setCalendarPopup(True)
        de.setDisplayFormat("dd/MM")
        de.setDate(QDate(_DUMMY_YEAR, 1, 1))
        return de

    def _time_to_str(self, t: time) -> str:
        return t.strftime("%H:%M")

    def _qtime_to_time(self, qte: QTimeEdit) -> time:
        q = qte.time()
        return time(q.hour(), q.minute())

    def _set_time_edit(self, qte: QTimeEdit, t: time):
        from PySide6.QtCore import QTime
        qte.setTime(QTime(t.hour, t.minute))

    def load_values(self):
        """Load season dates and times from settings or defaults."""
        # Dates: dd/mm
        self.summer_start_date.setDate(QDate(
            _DUMMY_YEAR,
            self.settings.get_summer_start_month(),
            self.settings.get_summer_start_day(),
        ))
        self.summer_end_date.setDate(QDate(
            _DUMMY_YEAR,
            self.settings.get_summer_end_month(),
            self.settings.get_summer_end_day(),
        ))
        # Summer times (settings override or default)
        s = SUMMER_SCHEDULE
        for key, qte in (
            ("morning_start", self.summer_morning_start),
            ("morning_end", self.summer_morning_end),
            ("break_start", self.summer_break_start),
            ("break_end", self.summer_break_end),
            ("afternoon_start", self.summer_afternoon_start),
            ("afternoon_end", self.summer_afternoon_end),
        ):
            val = self.settings.get_season_time("summer", key)
            if val:
                try:
                    h, m = map(int, val.split(":"))
                    self._set_time_edit(qte, time(h, m))
                except Exception:
                    self._set_time_edit(qte, s[key])
            else:
                self._set_time_edit(qte, s[key])
        # Winter times
        w = WINTER_SCHEDULE
        for key, qte in (
            ("morning_start", self.winter_morning_start),
            ("morning_end", self.winter_morning_end),
            ("break_start", self.winter_break_start),
            ("break_end", self.winter_break_end),
            ("afternoon_start", self.winter_afternoon_start),
            ("afternoon_end", self.winter_afternoon_end),
        ):
            val = self.settings.get_season_time("winter", key)
            if val:
                try:
                    h, m = map(int, val.split(":"))
                    self._set_time_edit(qte, time(h, m))
                except Exception:
                    self._set_time_edit(qte, w[key])
            else:
                self._set_time_edit(qte, w[key])

    def save_values(self):
        """Validate and save season dates and times."""
        q_start = self.summer_start_date.date()
        q_end = self.summer_end_date.date()
        sm, sd = q_start.month(), q_start.day()
        em, ed = q_end.month(), q_end.day()
        start_o = sm * 31 + sd
        end_o = em * 31 + ed
        if start_o > end_o:
            QMessageBox.warning(
                self, tr("error"),
                tr("settings_summer_start_before_end")
            )
            return

        self.settings.set_summer_range(sm, sd, em, ed)

        def collect_times(prefix, widgets):
            return {
                "morning_start": self._time_to_str(self._qtime_to_time(widgets[0])),
                "morning_end": self._time_to_str(self._qtime_to_time(widgets[1])),
                "break_start": self._time_to_str(self._qtime_to_time(widgets[2])),
                "break_end": self._time_to_str(self._qtime_to_time(widgets[3])),
                "afternoon_start": self._time_to_str(self._qtime_to_time(widgets[4])),
                "afternoon_end": self._time_to_str(self._qtime_to_time(widgets[5])),
            }

        self.settings.set_all_season_times("summer", collect_times("summer", (
            self.summer_morning_start, self.summer_morning_end,
            self.summer_break_start, self.summer_break_end,
            self.summer_afternoon_start, self.summer_afternoon_end,
        )))
        self.settings.set_all_season_times("winter", collect_times("winter", (
            self.winter_morning_start, self.winter_morning_end,
            self.winter_break_start, self.winter_break_end,
            self.winter_afternoon_start, self.winter_afternoon_end,
        )))

        QMessageBox.information(self, tr("success"), tr("settings_saved"))
