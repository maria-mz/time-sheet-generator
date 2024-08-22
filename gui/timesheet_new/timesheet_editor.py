"""
TimesheetEditor widget for editing a single employee's timesheet.
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    QStackedLayout
)
from PySide6.QtCore import Qt

from db.db_data import Employee, Shift
from gui.gui_data import ShiftText
from gui.timesheet_new.timesheet_page import TimesheetPage


SHIFTS_PER_PAGE = 7


class TimesheetEditor(QWidget):
    """
    Widget for editing an employee's time sheet.
    """

    def __init__(self, employee: Employee):
        super().__init__()

        self._pages = self._build_pages(employee.shifts)
        self._page_layout = self._create_page_layout()

        self._init_ui()

    def _build_pages(self, shifts: list[Shift]) -> list[TimesheetPage]:
        pages = []
        total_shifts = len(shifts)

        for start_idx in range(0, total_shifts, SHIFTS_PER_PAGE):
            end_idx = min(start_idx + SHIFTS_PER_PAGE, total_shifts) - 1
            
            page = TimesheetPage(shifts[start_idx:end_idx + 1])

            pages.append(page)

        return pages

    def _create_paginator(self) -> QComboBox:
        paginator = QComboBox()

        if len(self._pages) == 0:
            paginator.addItem("No weeks available")
            return paginator

        for i in range(len(self._pages)):
            paginator.addItem(f"Week {i + 1}")

        paginator.currentIndexChanged.connect(self._switch_page)

        return paginator

    def _create_page_layout(self) -> QStackedLayout:
        """
        Creates a stacked layout for displaying multiple timesheet views.
        """
        layout = QStackedLayout()

        for page in self._pages:
            layout.addWidget(page)

        return layout

    def _init_ui(self) -> None:
        box = QGroupBox("Timesheet")

        paginator = self._create_paginator()

        layout = QVBoxLayout()
        layout.addLayout(self._page_layout)
        layout.addWidget(paginator, alignment=Qt.AlignRight)

        box.setLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(box)
        layout.setAlignment(Qt.AlignLeft)

        container = QVBoxLayout()
        container.addLayout(layout)
        container.setAlignment(Qt.AlignTop)

        self.setLayout(container)

    def _switch_page(self, idx: int) -> None:
        self._page_layout.setCurrentIndex(idx)

    @property
    def shifts(self) -> list[ShiftText]:
        return [shift for page in self._pages for shift in page.shifts]
