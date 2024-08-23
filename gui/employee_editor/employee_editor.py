from typing import Protocol

from PySide6.QtWidgets import QWidget, QLayout, QPushButton, QMessageBox
from PySide6.QtCore import Signal

from gui import gui_constants
from gui.gui_utils import show_dialog, DialogType

from db.db_data import Employee


INVALID_FIELDS_MSG = "Please correct the highlighted fields and try again."


# -------------------- INTERFACES [START] --------------------


class EmployeeEditorUI(Protocol):
    @property
    def layout(self) -> QLayout:
        ...

    @property
    def delete_employee_btn(self) -> QPushButton:
        ...

    @property
    def cancel_btn(self) -> QPushButton:
        ...

    @property
    def save_employee_btn(self) -> QPushButton:
        ...

    @property
    def add_employee_btn(self) -> QPushButton:
        ...

    @property
    def employee_id(self) -> str:
        ...


class EmployeeService(Protocol):
    def update_employee(self, employee: Employee) -> None:
        ...

    def delete_employee(self, employee_id: str) -> None:
        ...

    def add_employee(self, employee: Employee) -> None:
        ...


class DuplicateEmployeeNumber(Exception):
    pass


# -------------------- INTERFACES [END] --------------------


class EmployeeEditor(QWidget):
    saved_changes = Signal()
    cancelled = Signal()

    def __init__(self, ui: EmployeeEditorUI, service: EmployeeService):
        super().__init__()

        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

    def _init_conns(self) -> None:
        self._ui.delete_employee_btn.clicked.connect(self._handle_delete_employee)
        self._ui.cancel_btn.clicked.connect(self._handle_cancel)
        self._ui.save_employee_btn.clicked.connect(self._handle_save_employee)
        self._ui.add_employee_btn.clicked.connect(self._handle_add_employee)

    def _handle_save_employee(self) -> None:
        try:
            employee = self.get_employee()
        except ValueError:
            show_dialog(DialogType.WARN, INVALID_FIELDS_MSG)
            return

        try:
            self._service.update_employee(employee)
        except Exception:
            show_dialog(DialogType.ERR, gui_constants.INTERNAL_ERR_MSG)
        else:
            show_dialog(DialogType.INFO, "Employee saved.")
            self.saved_changes.emit()

    def _handle_add_employee(self) -> None:
        try:
            employee = self.get_employee()
        except ValueError:
            show_dialog(DialogType.WARN, INVALID_FIELDS_MSG)
            return

        try:
            self._service.add_employee(employee)
        except DuplicateEmployeeNumber:
            self._dialog_handler.show_error_dialog(
                "Employee number already exists.",
                "Please enter a unique employee number."
            )
        except Exception:
            show_dialog(DialogType.ERR, gui_constants.INTERNAL_ERR_MSG)
        else:
            show_dialog(DialogType.INFO, "Employee added.")
            self.saved_changes.emit()

    def _handle_delete_employee(self) -> None:
        choice = self._dialog_handler.show_confirm_dialog(
            "Delete this employee?", "This cannot be undone!"
        )

        if choice != QMessageBox.Yes:
            return

        try:
            self._service.delete_employee(self._ui.employee_id)
        except Exception:
            show_dialog(DialogType.ERR, gui_constants.INTERNAL_ERR_MSG)
        else:
            show_dialog(DialogType.INFO, "Employee deleted.")
            self.saved_changes.emit()

    def _handle_cancel(self) -> None:
        self.cancelled.emit()
