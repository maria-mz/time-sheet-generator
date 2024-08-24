from typing import Protocol

from PySide6.QtWidgets import QWidget, QPushButton, QMessageBox, QLayout
from PySide6.QtCore import Signal

from gui import gui_utils
from gui import gui_constants
from gui.employee_editor.employee_editor_ui import EmployeeEditorUI, EditorMode
from gui.employee_editor.employee_editor import EmployeeEditor
from gui.employee_importer.employee_importer_ui import EmployeeImporterUI
from gui.employee_importer.employee_importer import EmployeeImporter
from gui.employees_table import EmployeesTable

from db.db_data import Employee


# -------------------- INTERFACES [START] --------------------


class EmployeeService(Protocol):
    def update_employee(self, employee: Employee) -> None:
        ...

    def delete_employee(self, employee_id: str) -> None:
        ...

    def add_employee(self, employee: Employee) -> None:
        ...

    def add_employees(self, employees: list[Employee]) -> None:
        ...

    def generate_employees_from_csv(self, file_path: str) -> list[Employee]:
        ...

    def delete_employees(self) -> None:
        ...

    def get_employees(self) -> list[Employee]:
        ...

    def create_blank_employee(self) -> Employee:
        ...
    
    def save_timesheet(self, employees: list[Employee], file_path: str) -> None:
        ...


class TimesheetTabUI(Protocol):
    @property
    def table(self) -> EmployeesTable:
        ...

    @property
    def pdf_filename_selected(self) -> Signal:
        ...

    @property
    def delete_all_employees_btn(self) -> QPushButton:
        ...

    @property
    def import_btn(self) -> QPushButton:
        ...

    @property
    def add_employee_btn(self) -> QPushButton:
        ...

    def layout(self) -> QLayout:
        ...


# -------------------- INTERFACES [END] --------------------


class TimesheetTab(QWidget):
    def __init__(self, ui: TimesheetTabUI, service: EmployeeService):
        super().__init__()

        self.window_popup = None # Need to hold onto any windows created otherwise
        # they will get deleted immediately
        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

        self.refresh_tab()

    def _init_conns(self) -> None:
        self._ui.table.cellDoubleClicked.connect(self._handle_edit_employee)
        self._ui.pdf_filename_selected.connect(self._handle_download_pdf)
        self._ui.delete_all_employees_btn.clicked.connect(self._handle_delete_employees)
        self._ui.import_btn.clicked.connect(self._handle_import_employees)
        self._ui.add_employee_btn.clicked.connect(self._handle_add_employee)

    def _handle_edit_employee(self, row: int, _: int) -> None:
        employee = self._ui.table.get_employee_from_row(row)

        editor_ui = EmployeeEditorUI(EditorMode.EDIT, employee)
        editor = EmployeeEditor(editor_ui, self._service)

        self.window_popup = gui_utils.create_window("Edit Employee", editor)

        editor.saved_edits.connect(self.refresh_tab)
        editor.saved_edits.connect(self.window_popup.close)
        editor.edit_cancelled.connect(self.window_popup.close)

        self.window_popup.show()

    def _handle_add_employee(self) -> None:
        employee = self._service.create_blank_employee()

        editor_ui = EmployeeEditorUI(EditorMode.CREATE, employee)
        editor = EmployeeEditor(editor_ui, self._service)

        self.window_popup = gui_utils.create_window("Add Employee", editor)

        editor.saved_edits.connect(self.refresh_tab)
        editor.saved_edits.connect(self.window_popup.close)
        editor.edit_cancelled.connect(self.window_popup.close)

        self.window_popup.show()

    def _handle_import_employees(self) -> None:
        importer_ui = EmployeeImporterUI()
        importer = EmployeeImporter(importer_ui, self._service)

        self.window_popup = gui_utils.create_window(
            "Import Employees", importer, self.width(), self.height()
        )

        importer.imported_employees.connect(self.refresh_tab)
        importer.imported_employees.connect(self.window_popup.close)
        importer.cancelled_import.connect(self.window_popup.close)

        self.window_popup.show()

    def _handle_delete_employees(self) -> None:
        choice = gui_utils.show_dialog(
            gui_utils.DialogType.CONFIRM,
            "Delete all employees?",
            "This cannot be undone!"
        )

        if choice != QMessageBox.Yes:
            return

        try:
            self._service.delete_employees()
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            self.refresh_tab()
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Employees deleted.")

    def _handle_download_pdf(self, file_path: str) -> None:
        if file_path == "":
            return

        employees = self._ui.table.get_employees_matching_filter()

        try:
            self._service.save_timesheet(employees, file_path)
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
            return

        choice = gui_utils.show_dialog(
            gui_utils.DialogType.INFO,
            "PDF saved.",
            buttons=[
                ("View File", QMessageBox.AcceptRole),
                ("Ok", QMessageBox.ActionRole)
            ]
        )

        if choice == 0:
            try:
                gui_utils.open_file_in_native_file_gui(file_path)
            except Exception:
                gui_utils.show_dialog(
                    gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
                )

    def refresh_tab(self) -> None:
        try:
            employees = self._service.get_employees()
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            self._ui.table.populate_table(employees)
