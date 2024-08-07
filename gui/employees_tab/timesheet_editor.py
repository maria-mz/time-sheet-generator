"""
TimesheetEditor widget for editing a single employee's timesheet.
"""
import datetime
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QTimeEdit,
    QGridLayout,
    QGroupBox,
    QComboBox,
    QStackedLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from gui import qutils
from db.db_data import Employee, Shift


MAX_ENTRIES_TO_SHOW = 7


@dataclass
class QShift:
    """
    Represents a single shift's UI components.
    """
    date: datetime.date
    date_label: QLabel
    time_in_field: QTimeEdit
    time_out_field: QTimeEdit
    hours_reg_field: QLineEdit
    hours_ot_field: QLineEdit


@dataclass
class TimesheetView:
    """
    Represents a piece of the timesheet over a contiguous date range.
    """
    start_date: datetime.date
    end_date: datetime.date
    qshifts: list[QShift]


class TimesheetEditor(QWidget):
    """
    Widget for editing an employee's time sheet.
    """

    def __init__(self, employee: Employee):
        super().__init__()

        self.employee = employee
        self.timesheet_views = self._build_timesheet_views(employee.shifts)
        self.timesheet_layout = self._create_timesheet_layout()

        dropdown = self._create_dropdown(self.timesheet_views)

        layout = QVBoxLayout()
        layout.addWidget(dropdown, alignment=Qt.AlignLeft)
        layout.addLayout(self.timesheet_layout)
        layout.setAlignment(Qt.AlignLeft)

        container = QVBoxLayout()
        container.addLayout(layout)
        container.setAlignment(Qt.AlignTop)

        self.setLayout(container)

    def _build_timesheet_views(self, shifts: list[Shift]) -> list[TimesheetView]:
        """
        Constructs a list of Timesheet Views given the list of shifts. The 
        number of views depends on the max number of days (shifts) that can
        be shown at a time.
        """
        timesheet_views = []
        total_shifts = len(shifts)

        for start_idx in range(0, total_shifts, MAX_ENTRIES_TO_SHOW):
            end_idx = min(start_idx + MAX_ENTRIES_TO_SHOW, total_shifts) - 1
            
            timesheet_view = TimesheetView(
                start_date=shifts[start_idx].date,
                end_date=shifts[end_idx].date,
                qshifts=self._create_qshifts(shifts[start_idx:end_idx + 1])
            )

            timesheet_views.append(timesheet_view)

        return timesheet_views

    def _create_dropdown(self, timesheet_views: list[TimesheetView]) -> QComboBox:
        """
        Create a dropdown menu for selecting different views of the timesheet.
        """
        dropdown = QComboBox()

        if len(timesheet_views) == 0:
            dropdown.addItem("No shifts available")
            return dropdown

        for timesheet_view in timesheet_views:
            option = f"{timesheet_view.start_date} to {timesheet_view.end_date} " + \
                     f"({len(timesheet_view.qshifts)} days)"

            dropdown.addItem(option)

        dropdown.currentIndexChanged.connect(self._switch_timesheet)

        return dropdown

    def _create_timesheet_layout(self) -> QStackedLayout:
        """
        Creates a stacked layout for displaying multiple timesheet views.
        """
        layout = QStackedLayout()

        for timesheet_view in self.timesheet_views:
            timesheet_box = self._create_timesheet_box(timesheet_view)
            layout.addWidget(timesheet_box)

        return layout

    def _create_qshifts(self, shifts: list[Shift]) -> list[QShift]:
        """
        Turn a list of Shifts into the corresponding QShifts.
        """
        return [self._create_qshift(shift) for shift in shifts]

    def _create_qshift(self, shift: Shift) -> QShift:
        """
        Turn a Shift into the corresponding QShift.
        """
        date_label = QLabel(str(shift.date))
        date_label.setContentsMargins(0, 0, 50, 0)

        time_in_field = QTimeEdit(qutils.time_to_qtime(shift.time_in))
        time_out_field = QTimeEdit(qutils.time_to_qtime(shift.time_out))

        time_in_field.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        time_out_field.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        hours_reg_field = QLineEdit(shift.hours_reg)
        hours_ot_field = QLineEdit(shift.hours_ot)

        hours_reg_field.setValidator(self._create_hours_validator())
        hours_ot_field.setValidator(self._create_hours_validator())

        hours_reg_field_formatter = self._get_hours_formatter(hours_reg_field)
        hours_ot_field_formatter = self._get_hours_formatter(hours_ot_field)

        hours_reg_field.editingFinished.connect(hours_reg_field_formatter)
        hours_ot_field.editingFinished.connect(hours_ot_field_formatter)

        return QShift(
            date=shift.date,
            date_label=date_label,
            time_in_field=time_in_field,
            time_out_field=time_out_field,
            hours_reg_field=hours_reg_field,
            hours_ot_field=hours_ot_field
        )

    def _create_hours_validator(self) -> QRegularExpressionValidator:
        regex = QRegularExpression("^\d{0,2}(\.\d{0,2})?$")
        return QRegularExpressionValidator(regex)

    def _get_hours_formatter(self, edit: QLineEdit) -> None:
        def formatter():
            hours = edit.text()
            formatted_hours = "0.00" if hours in {"", "."} else "{:.2f}".format(float(hours))
            edit.setText(formatted_hours)

        return formatter

    def _create_timesheet_box(self, timesheet_view: TimesheetView) -> QGroupBox:
        """
        Creates a widget showing the timesheet view.
        """
        box = QGroupBox("Time Sheet")

        grid = QGridLayout()

        titles = ["Date", "Time In", "Time Out", "Regular Hours", "Overtime Hours"]

        for i, title in enumerate(titles):
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold;")
            grid.addWidget(title_label, 0, i)

        for i, qshift in enumerate(timesheet_view.qshifts):
            grid.addWidget(qshift.date_label, i + 1, 0)
            grid.addWidget(qshift.time_in_field, i + 1, 1)
            grid.addWidget(qshift.time_out_field, i + 1, 2)
            grid.addWidget(qshift.hours_reg_field, i + 1, 3)
            grid.addWidget(qshift.hours_ot_field, i + 1, 4)

        grid.setContentsMargins(12, 12, 12, 12)

        # Very important! Makes sure all items stay at the top and
        # don't "stretch" when window is expanded vertically
        grid.setAlignment(Qt.AlignTop)

        box.setLayout(grid)

        return box

    def _switch_timesheet(self, idx: int) -> None:
        self.timesheet_layout.setCurrentIndex(idx)

    def get_shifts(self) -> list[Shift]:
        """
        Save the employee's shifts persistently. Involves creating a new list
        of Shifts from all the QShifts, updating the Employee object, then
        calling the backend.
        """
        shifts = []

        for timesheet_view in self.timesheet_views:
            shifts.extend(self._create_shifts(timesheet_view.qshifts))

        return shifts

    def _create_shifts(self, qshifts: list[QShift]) -> list[Shift]:
        """
        Turn a list of QShifts into the corresponding Shifts.
        """
        return [self._create_shift(qshift) for qshift in qshifts]

    def _create_shift(self, qshift: QShift) -> Shift:
        """
        Turn a QShift into the corresponding Shift.
        """
        return Shift(
            date=qshift.date,
            time_in=qutils.qtime_to_time(qshift.time_in_field.time()),
            time_out=qutils.qtime_to_time(qshift.time_out_field.time()),
            hours_reg=qshift.hours_reg_field.text(),
            hours_ot=qshift.hours_ot_field.text()
        )
