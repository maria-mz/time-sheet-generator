"""
TimesheetEditor widget for editing a single employee's timesheet.
"""
from datetime import datetime
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QComboBox,
    QStackedLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from db.db_data import Employee, Shift
from gui.employees_tab.timesheet.qshift import QShift


MAX_ENTRIES_TO_SHOW = 7


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

        timesheet_box = self._create_timesheet_box()

        layout = QVBoxLayout()
        layout.addWidget(timesheet_box)
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

    def _create_paginator(self, timesheet_views: list[TimesheetView]) -> QComboBox:
        """
        Create a dropdown menu for selecting different views of the timesheet.
        """
        paginator = QComboBox()

        if len(timesheet_views) == 0:
            paginator.addItem("No weeks available")
            return paginator

        for i in range(len(timesheet_views)):
            paginator.addItem(f"Week {i + 1}")

        paginator.currentIndexChanged.connect(self._switch_timesheet)

        return paginator

    def _create_timesheet_layout(self) -> QStackedLayout:
        """
        Creates a stacked layout for displaying multiple timesheet views.
        """
        layout = QStackedLayout()

        for timesheet_view in self.timesheet_views:
            timesheet_box = self._create_timesheet_widget(timesheet_view)
            layout.addWidget(timesheet_box)

        return layout

    def _create_qshifts(self, shifts: list[Shift]) -> list[QShift]:
        """
        Turn a list of Shifts into the corresponding QShifts.
        """
        return [QShift(shift) for shift in shifts]

    def _create_timesheet_widget(self, timesheet_view: TimesheetView) -> QWidget:
        """
        Creates a widget showing the timesheet view.
        """
        widget = QWidget()

        grid = QGridLayout()

        titles = ["Date", "", "Time In", "Time Out", "Regular Hours", "Overtime Hours"]

        for i, title in enumerate(titles):
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")
            grid.addWidget(title_label, 0, i)

        for i, qshift in enumerate(timesheet_view.qshifts):
            grid.addWidget(QLabel(qshift.date.strftime("%a")), i + 1, 0)
            grid.addWidget(qshift.date_label, i + 1, 1)
            grid.addWidget(qshift.time_in_edit, i + 1, 2)
            grid.addWidget(qshift.time_out_edit, i + 1, 3)
            grid.addWidget(qshift.hours_reg_edit, i + 1, 4)
            grid.addWidget(qshift.hours_ot_edit, i + 1, 5)

        grid.setContentsMargins(12, 12, 12, 12)

        # Very important! Makes sure all items stay at the top and
        # don't "stretch" when window is expanded vertically
        grid.setAlignment(Qt.AlignTop)

        widget.setLayout(grid)

        return widget

    def _create_timesheet_box(self) -> QGroupBox:
        box = QGroupBox("Timesheet")

        paginator = self._create_paginator(self.timesheet_views)

        layout = QVBoxLayout()
        layout.addLayout(self.timesheet_layout)
        layout.addWidget(paginator, alignment=Qt.AlignRight)

        box.setLayout(layout)

        return box

    def _switch_timesheet(self, idx: int) -> None:
        self.timesheet_layout.setCurrentIndex(idx)

    def get_shifts(self) -> list[Shift]:
        """
        Get all the shift data. Raises InvalidShiftValue if any shift values are
        currently invalid.
        """
        shifts = []

        for timesheet_view in self.timesheet_views:
            for qshift in timesheet_view.qshifts:
                qshift.handle_input() # To handle edge case where saving while editing

            shifts.extend(self._create_shifts(timesheet_view.qshifts))

        return shifts

    def _create_shifts(self, qshifts: list[QShift]) -> list[Shift]:
        """
        Turn a list of QShifts into the corresponding Shifts.
        """
        return [qshift.to_shift() for qshift in qshifts]
