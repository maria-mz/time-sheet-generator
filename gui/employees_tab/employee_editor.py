from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QMessageBox
)
from PySide6.QtCore import Signal, Qt
from enum import Enum

import gui.constants
from gui import qutils
from gui.employees_tab.employee_profile import EmployeeProfile
from gui.employees_tab.timesheet_editor import TimesheetEditor

from backend.backend import backend
from backend.errors import InternalError
from db.db_handler import EmployeeAlreadyExistsError
from db.db_data import Employee


class EditorMode(Enum):
    EDIT: int = 0
    CREATE: int = 1


class EmployeeEditor(QWidget):
    EMPLOYEE_UPDATED = Signal()
    DONE = Signal()

    def __init__(self, employee: Employee, mode: EditorMode):
        super().__init__()

        self.profile_widget = EmployeeProfile(employee)
        self.mode = mode

        if self.mode == EditorMode.EDIT:
            self.profile_widget.set_id_editable(False)

        self.timesheet_editor = TimesheetEditor(employee)
 
        layout = self._create_layout()

        self.setLayout(layout)

    def _create_layout(self) -> QVBoxLayout:
        if self.mode == EditorMode.CREATE:
            buttons = self._create_buttons_for_create_mode()
        else:
            buttons = self._create_buttons_for_edit_mode()
 
        layout = QVBoxLayout()

        layout.addWidget(self.profile_widget)
        layout.addWidget(self.timesheet_editor)
        layout.addLayout(buttons)

        return layout

    def _create_buttons_for_edit_mode(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Employee")
        delete_btn.clicked.connect(self._delete_employee)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._cancel)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._update_employee)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addWidget(delete_btn)
        layout.addItem(spacer)
        layout.addWidget(cancel_btn)
        layout.addWidget(save_btn)

        return layout

    def _create_buttons_for_create_mode(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._cancel)

        add_btn = QPushButton("Add Employee")
        add_btn.clicked.connect(self._add_employee)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addItem(spacer)
        layout.addWidget(cancel_btn)
        layout.addWidget(add_btn)

        return layout

    def _update_employee(self) -> None:
        employee = self._extract_employee()

        try:
            backend.update_employee(employee)
        except InternalError:
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.EMPLOYEE_UPDATED.emit()

            dialog = qutils.create_info_dialog("Employee saved.")
            dialog.exec()

            self.DONE.emit()

    def _add_employee(self) -> None:
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

    def _delete_employee(self) -> None:
        dialog = qutils.create_confirm_dialog("Delete employee?", "This cannot be undone.")

        choice = dialog.exec()

        if choice != QMessageBox.Yes:
            return

        employee = self._extract_employee()

        try:
            backend.delete_employee(employee)
        except InternalError:
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.EMPLOYEE_UPDATED.emit()

            dialog = qutils.create_info_dialog("Employee deleted.")
            choice = dialog.exec()

            self.DONE.emit()

    def _cancel(self) -> None:
        self.DONE.emit()

    def _extract_employee(self) -> Employee:
        return Employee(
            employee_id=self.profile_widget.employee_id(),
            first_name=self.profile_widget.first_name(),
            last_name=self.profile_widget.last_name(),
            position=self.profile_widget.position(),
            contract=self.profile_widget.contract(),
            shifts=self.timesheet_editor.get_shifts()
        )
