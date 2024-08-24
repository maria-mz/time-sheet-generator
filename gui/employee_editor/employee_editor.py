from typing import Protocol

from PySide6.QtWidgets import QWidget, QLayout, QPushButton, QMessageBox
from PySide6.QtCore import Signal

from gui import gui_utils
from gui import gui_constants

from db.db_data import Employee


INVALID_FIELDS_MSG = "Please correct the highlighted fields and try again."


# -------------------- INTERFACES [START] --------------------


class EmployeeEditorUI(Protocol):
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

    def layout(self) -> QLayout:
        ...

    def get_employee(self) -> Employee:
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
    saved_edits = Signal()
    edit_cancelled = Signal()

    def __init__(self, ui: EmployeeEditorUI, service: EmployeeService):
        super().__init__()

        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

    def _init_conns(self) -> None:
        self._ui.delete_employee_btn.clicked.connect(self._handle_delete_employee)
        self._ui.cancel_btn.clicked.connect(self.edit_cancelled.emit)
        self._ui.save_employee_btn.clicked.connect(self._handle_save_employee)
        self._ui.add_employee_btn.clicked.connect(self._handle_add_employee)

    def _handle_save_employee(self) -> None:
        try:
            employee = self._ui.get_employee()
        except ValueError:
            gui_utils.show_dialog(
                gui_utils.DialogType.WARN, "Couldn't save employee.", INVALID_FIELDS_MSG
            )
            return

        try:
            self._service.update_employee(employee)
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Employee saved.")
            self.saved_edits.emit()

    def _handle_add_employee(self) -> None:
        try:
            employee = self._ui.get_employee()
        except ValueError:
            gui_utils.show_dialog(
                gui_utils.DialogType.WARN, "Couldn't add employee.", INVALID_FIELDS_MSG
            )
            return

        try:
            self._service.add_employee(employee)
        except DuplicateEmployeeNumber:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR,
                "Employee number already exists.",
                "Please enter a unique employee number."
            )
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Employee added.")
            self.saved_edits.emit()

    def _handle_delete_employee(self) -> None:
        choice = gui_utils.show_dialog(
            gui_utils.DialogType.CONFIRM, "Delete employee?", "This cannot be undone!"
        )

        if choice != QMessageBox.Yes:
            return

        try:
            self._service.delete_employee(self._ui.employee_id)
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Employee deleted.")
            self.saved_edits.emit()
