from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy,
    QSpacerItem
)
from PySide6.QtCore import Signal

import gui.constants
from gui import qutils
from gui.employees_tab.employee_profile import EmployeeProfile
from gui.employees_tab.timesheet_editor import TimesheetEditor

from backend.backend import backend
from backend.errors import InternalError
from db.db_handler import EmployeeAlreadyExistsError
from db.db_data import Employee


class EmployeeCreator(QWidget):
    EMPLOYEE_UPDATED = Signal()
    DONE = Signal()

    def __init__(self, employee: Employee):
        super().__init__()

        self.profile_widget = EmployeeProfile(employee)
        self.timesheet_editor = TimesheetEditor(employee)
 
        layout = self._create_layout()

        self.setLayout(layout)

    def _create_layout(self) -> QVBoxLayout:
        line1 = self._create_sunken_hline()
        line2 = self._create_sunken_hline()

        bottom_buttons_row = self._create_bottom_buttons_row()
 
        layout = QVBoxLayout()

        layout.addWidget(self.profile_widget)
        layout.addWidget(line1)
        layout.addWidget(self.timesheet_editor)
        layout.addWidget(line2)
        layout.addLayout(bottom_buttons_row)

        return layout

    def _create_sunken_hline(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        return line

    def _create_bottom_buttons_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        add_btn = QPushButton("Add Employee")
        add_btn.clicked.connect(self._on_add_employee)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)

        # Horizontal spacer to keep buttons apart
        spacer = QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        layout.addItem(spacer)
        layout.addWidget(cancel_btn)
        layout.addWidget(add_btn)

        return layout

    def _on_add_employee(self) -> None:
        employee = self._extract_employee()

        try:
            backend.add_employee(employee)
        except EmployeeAlreadyExistsError as e:
            dialog = qutils.create_error_dialog("Failed to add employee.", str(e))
            dialog.exec()
        except InternalError:
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.EMPLOYEE_UPDATED.emit()

            dialog = qutils.create_info_dialog("Employee added successfully.")
            dialog.exec()

            self.DONE.emit()

    def _on_cancel(self) -> None:
        self.DONE.emit()

    def _extract_employee(self) -> Employee:
        employee_id = self.profile_widget.get_employee_id()
        full_name = self.profile_widget.get_full_name()
        position = self.profile_widget.get_position()
        shifts = self.timesheet_editor.get_shifts()

        return Employee(
            employee_id=employee_id,
            full_name=full_name,
            position=position,
            shifts=shifts
        )
