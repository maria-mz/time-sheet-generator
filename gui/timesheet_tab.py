from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
    QFrame,
    QFileDialog,
)
from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtGui import QIcon

from gui import gui_utils
from gui import gui_constants
from gui.employees_table import EmployeesTable
from gui.employee_editor import EmployeeEditor, EditorMode
from gui.employee_importer import EmployeeImporter
from gui.employee_profile import EmployeeProfile

import utils
from backend.backend import backend
from backend.errors import InternalError


class TimesheetTab(QWidget):
    def __init__(self):
        super().__init__()

        employees = backend.get_employees()

        self.table = EmployeesTable()
        self.table.populate_table(employees)
        self.table.cellDoubleClicked.connect(self._open_edit_employee_window)

        self.window_popup = None

        layout = self._create_main_layout()

        self.setLayout(layout)

    def _create_main_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        header_layout = self._create_header_layout()
        filter_section = self._create_filter_section()
        pdf_button = self._create_pdf_button()

        employee_buttons = self._create_employee_buttons()

        # Create this container for custom spacing between search bar and table
        container = QVBoxLayout()
        container.setSpacing(16)
        container.addWidget(filter_section)
        container.addWidget(pdf_button, alignment=Qt.AlignRight)
        container.addWidget(self.table)

        layout.addLayout(header_layout)
        layout.addLayout(container)
        layout.addLayout(employee_buttons)

        return layout

    def _create_header_layout(self) -> QHBoxLayout:
        title = QLabel("Timesheet")
        title.setStyleSheet("font-weight: bold; font-size: 24px")

        subtitle = QLabel(
            "Edit employee details and timesheet information here. " + \
            "Click an employee to open the editor."
        )

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(line)

        return layout

    def _create_filter_section(self) -> EmployeeProfile:
        section = EmployeeProfile()
        section.setTitle("Filter")

        section.first_name_edit.textChanged.connect(self.table.filter_by_first_name)
        section.last_name_edit.textChanged.connect(self.table.filter_by_last_name)
        section.id_edit.textChanged.connect(self.table.filter_by_id)
        section.position_edit.textChanged.connect(self.table.filter_by_position)
        section.contract_edit.textChanged.connect(self.table.filter_by_contract)

        return section

    def _create_pdf_button(self) -> QPushButton:
        btn = QPushButton("Download Timesheet")
        btn.setToolTip(
            "Generate the timesheet PDF for employees matching the current filter."
        )
        btn.clicked.connect(self._generate_pdf)
        btn.setIcon(QIcon(utils.load_file("assets/icons/arrow-down-solid.svg"))) # TODO: constant
        btn.setIconSize(QSize(14, 14))

        return btn

    def _create_employee_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        delete_btn = QPushButton("Delete All Employees")
        delete_btn.clicked.connect(self._delete_employees)

        import_btn = QPushButton("Import Employees")
        import_btn.clicked.connect(self._open_import_employees_window)

        add_btn = QPushButton("Add Employee")
        add_btn.clicked.connect(self._open_add_employee_window)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addWidget(delete_btn)
        layout.addItem(spacer)
        layout.addWidget(import_btn)
        layout.addWidget(add_btn)

        return layout

    def launch_window(self, title: str, widget: QWidget, w: int = None, h: int = None):
        self.window_popup = QWidget()

        if w and h:
            self.window_popup.setMinimumWidth(w)
            self.window_popup.setMinimumHeight(h)

        container = QVBoxLayout()
        container.addWidget(widget)

        self.window_popup.setWindowTitle(title)
        self.window_popup.setLayout(container)
        self.window_popup.show()

    @Slot()
    def _open_add_employee_window(self):
        employee = backend.create_empty_employee()

        editor = EmployeeEditor(employee, EditorMode.CREATE)
        editor.EMPLOYEE_UPDATED.connect(self.refresh_tab)
        editor.DONE.connect(self.close_window_popup)

        self.launch_window("Add Employee", editor)

    @Slot(int, int)
    def _open_edit_employee_window(self, row, col):
        employee = self.table.get_employee_from_row(row)

        editor = EmployeeEditor(employee, EditorMode.EDIT)
        editor.EMPLOYEE_UPDATED.connect(self.refresh_tab)
        editor.DONE.connect(self.close_window_popup)

        self.launch_window("Edit Employee", editor)

    def _open_import_employees_window(self):
        importer = EmployeeImporter()
        importer.EMPLOYEES_UPDATED.connect(self.refresh_tab)
        importer.DONE.connect(self.close_window_popup)

        self.launch_window("Import Employees", importer, self.width(), self.height())

    def _delete_employees(self):
        dialog = gui_utils.create_confirm_dialog("Delete all employees?", "This cannot be undone.")

        choice = dialog.exec()

        if choice != QMessageBox.Yes:
            return

        try:
            backend.delete_employees()
        except InternalError:
            dialog = gui_utils.create_error_dialog(gui_constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.refresh_tab()
            dialog = gui_utils.create_info_dialog("Employees deleted.")
            choice = dialog.exec()

    def _open_save_file_window(self) -> str:
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save PDF",
            dir=backend.get_home_dir(),
            filter="Adobe Acrobat Document (*.pdf)"
        )

        file_path = response[0]

        return file_path

    def _view_output_location(self, file_path: str) -> None:
        try:
            backend.open_explorer(file_path)
        except InternalError:
            dialog = gui_utils.create_error_dialog(gui_constants.INTERNAL_ERR_MSG)
            dialog.exec()

    @Slot()
    def _generate_pdf(self):
        file_path = self._open_save_file_window()

        if file_path == "": # User cancelled
            return

        try:
            backend.save_timesheet(
                employees=self.table.get_employees_matching_filter(),
                file_path=file_path
            )
        except InternalError:
            dialog = gui_utils.create_error_dialog(gui_constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            dialog = gui_utils.create_yes_no_dialog("PDF saved. View output location?")
            choice = dialog.exec()

            if choice == QMessageBox.Yes:
                self._view_output_location(file_path)

    @Slot()
    def close_window_popup(self):
        if self.window_popup is not None:
            self.window_popup.close()
            self.window_popup = None

    @Slot()
    def refresh_tab(self):
        employees = backend.get_employees()
        self.table.populate_table(employees)
