from typing import Protocol

from PySide6.QtWidgets import QWidget, QLayout
from PySide6.QtCore import Signal

from gui.gui_utils import show_dialog, DialogType
from gui import gui_constants

from db.db_data import Employee


FILE_SUCCESS_STYLE = "color: green;"
FILE_ERR_STYLE = "color: red;"


# -------------------- INTERFACES [START] --------------------


class EmployeeImporterUI(Protocol):
    @property
    def file_selected(self) -> Signal:
        ...

    @property
    def import_employees_btn_clicked(self) -> Signal:
        ...

    @property
    def cancel_btn_clicked(self) -> Signal:
        ...

    def layout(self) -> QLayout:
        ...

    def set_import_btn_enabled(self, enabled: bool) -> None:
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


class CSVReadError(Exception):
    pass


class DuplicateEmployeeNumber(Exception):
    pass


# -------------------- INTERFACES [END] --------------------


class EmployeeImporter(QWidget):
    imported_employees = Signal()
    cancelled_import = Signal()

    def __init__(self, ui: EmployeeImporterUI, service: EmployeeService):
        super().__init__()

        self._employees = []
        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

    def _init_conns(self) -> None:
        self._ui.cancel_btn_clicked.connect(self.cancelled_import.emit)
        self._ui.file_selected.connect(self._handle_file_selected)
        self._ui.import_employees_btn_clicked.connect(self._handle_import)

    def _handle_file_selected(self, file_path: str) -> None:
        if not file_path:
            return

        self._employees = []
        self._ui.populate_table([])
        self._ui.set_import_btn_enabled(False)

        try:
            employees = self._service.generate_employees_from_csv(file_path)

        except CSVReadError as e:
            self._ui.set_filename(file_path, FILE_ERR_STYLE)
            show_dialog(DialogType.ERR, "Failed to read CSV.", str(e))

        except Exception:
            self._ui.set_filename(file_path, FILE_ERR_STYLE)
            show_dialog(DialogType.ERR, gui_constants.INTERNAL_ERR_MSG)

        else:
            if len(employees) > 0:
                self._ui.set_import_btn_enabled(True)
                self._ui.populate_table(employees)

            self._ui.set_filename(file_path, FILE_SUCCESS_STYLE)
            show_dialog(DialogType.INFO, "Read successful.")

        self._employees = employees

    def _handle_import(self) -> None:
        try:
            self._service.add_employees(self._employees)
        except DuplicateEmployeeNumber:
            show_dialog(
                DialogType.ERR,
                "Employee number already exists.",
                "Please enter a unique employee number."
            )
        except Exception:
            show_dialog(DialogType.ERR, gui_constants.INTERNAL_ERR_MSG)
        else:
            show_dialog(DialogType.INFO, "Employees imported successfully.")
            self.imported_employees.emit()
