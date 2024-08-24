from typing import Protocol

from PySide6.QtWidgets import QWidget, QLayout, QPushButton
from PySide6.QtCore import Signal

from gui import gui_utils
from gui import gui_constants

from backend.backend import CSVReadError
from db.db_data import Employee
from db.db_handler import DuplicateEmployeeID


FILE_SUCCESS_STYLE = "color: green;"
FILE_ERR_STYLE = "color: red;"


# -------------------- INTERFACES [START] --------------------


class EmployeeImporterUI(Protocol):
    @property
    def file_selected(self) -> Signal:
        ...

    @property
    def import_employees_btn(self) -> QPushButton:
        ...

    @property
    def cancel_btn(self) -> QPushButton:
        ...

    def layout(self) -> QLayout:
        ...

    def set_filename(self, text: str, style: str = "") -> None:
        ...

    def populate_table(self, employees: list[Employee]) -> None:
        ...


class EmployeeService(Protocol):
    def add_employees(self, employees: list[Employee]) -> None:
        ...

    def generate_employees_from_csv(self, file_path: str) -> list[Employee]:
        ...


# -------------------- INTERFACES [END] --------------------


class EmployeeImporter(QWidget):
    imported_employees = Signal()
    importing_finished = Signal()

    def __init__(self, ui: EmployeeImporterUI, service: EmployeeService):
        super().__init__()

        self._employees = []
        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

    def _init_conns(self) -> None:
        self._ui.cancel_btn.clicked.connect(self.importing_finished.emit)
        self._ui.import_employees_btn.clicked.connect(self._handle_import)
        self._ui.file_selected.connect(self._handle_file_selected)

    def _handle_file_selected(self, file_path: str) -> None:
        if not file_path:
            return

        self._employees = []
        self._ui.populate_table([])
        self._ui.import_employees_btn.setEnabled(False)

        try:
            employees = self._service.generate_employees_from_csv(file_path)

        except CSVReadError as e:
            self._ui.set_filename(file_path, FILE_ERR_STYLE)
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, "Couldn't read CSV.", str(e)
            )

        except Exception:
            self._ui.set_filename(file_path, FILE_ERR_STYLE)
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )

        else:
            if len(employees) > 0:
                self._ui.import_employees_btn.setEnabled(True)
                self._ui.populate_table(employees)

            self._ui.set_filename(file_path, FILE_SUCCESS_STYLE)
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Read successful.")

            self._employees = employees

    def _handle_import(self) -> None:
        try:
            self._service.add_employees(self._employees)
        except DuplicateEmployeeID:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR,
                "Couldn't import employees.",
                "Please provide unique employee numbers for all employees."
            )
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            self.imported_employees.emit()
            gui_utils.show_dialog(
                gui_utils.DialogType.INFO, "Employees imported successfully."
            )
            self.importing_finished.emit()
