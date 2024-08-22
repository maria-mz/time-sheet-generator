from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from db.db_data import Shift
from gui.gui_data import ShiftText
from gui.timesheet_new.timesheet_shift import TimesheetShift


DATE_TXT = "Date"
TIME_IN_TXT = "Time In"
TIME_OUT_TXT = "Time Out"
HOURS_REG_TXT = "Regular Hours"
HOURS_OT_TXT = "Overtime Hours"

DAY_FORMAT = "%a"


class TimesheetPage(QWidget):
    def __init__(self, shifts: list[Shift]):
        super().__init__()

        self._timesheet_shifts = [TimesheetShift(shift) for shift in shifts]
        self._init_ui()

    def _init_ui(self) -> None:
        grid = QGridLayout()

        titles = [
            DATE_TXT, "",
            TIME_IN_TXT,
            TIME_OUT_TXT,
            HOURS_REG_TXT,
            HOURS_OT_TXT
        ]

        for i, title in enumerate(titles):
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")
            grid.addWidget(title_label, 0, i)

        for i, tshift in enumerate(self._timesheet_shifts):
            grid.addWidget(tshift.date.strftime(DAY_FORMAT), i + 1, 0)
            grid.addWidget(tshift.date_label, i + 1, 1)
            grid.addWidget(tshift.time_in_edit, i + 1, 2)
            grid.addWidget(tshift.time_out_edit, i + 1, 3)
            grid.addWidget(tshift.hours_reg_edit, i + 1, 4)
            grid.addWidget(tshift.hours_ot_edit, i + 1, 5)

        grid.setContentsMargins(12, 12, 12, 12)

        # Very important! Makes sure all items stay at the top and
        # don't "stretch" when window is expanded vertically
        grid.setAlignment(Qt.AlignTop)

        self.setLayout(grid)

    @property
    def shifts(self) -> list[ShiftText]:
        return [
            timesheet_shift.shift for timesheet_shift in self._timesheet_shifts
        ]
