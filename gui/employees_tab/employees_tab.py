from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Slot

from gui.employees_tab.employees_table import EmployeesTable
from gui.employees_tab.employee_editor import EmployeeEditor
from gui.employees_tab.employee_creator import EmployeeCreator
from gui.employees_tab.employee_importer import EmployeeImporter

from backend.backend import backend


class EmployeesTab(QWidget):
    def __init__(self):
        super().__init__()

        employees = backend.get_employees()

        self.table = EmployeesTable()
        self.table.populate_table(employees)
        self.table.cellDoubleClicked.connect(self.edit_employee_popup)

        header_layout = self._create_header_layout()
        search_bar = self._create_search_bar()

        layout = QVBoxLayout()

        layout.addLayout(header_layout)
        layout.addWidget(search_bar)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _create_header_layout(self) -> QHBoxLayout:
        title = QLabel(f"Employees")
        title.setStyleSheet("font-weight: bold; font-size: 24px")

        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.clicked.connect(self.import_csv_popup)

        add_employee_btn = QPushButton("Add Employee")
        add_employee_btn.clicked.connect(self.add_employee_popup)

        # Horizontal spacer to keep the title and buttons apart
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout()

        layout.addWidget(title)
        layout.addItem(spacer)
        layout.addWidget(import_csv_btn)
        layout.addWidget(add_employee_btn)

        return layout

    def _create_search_bar(self) -> QLineEdit:
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by name")
        search_bar.textChanged.connect(self.table.filter_table_by_name)

        return search_bar

    def launch_window(self, title: str, widget: QWidget, w: int = None, h: int = None):
        self.popup = QWidget()

        if w and h:
            self.popup.setMinimumWidth(w)
            self.popup.setMinimumHeight(h)

        container = QVBoxLayout()
        container.addWidget(widget)

        self.popup.setWindowTitle(title)
        self.popup.setLayout(container)
        self.popup.show()

    @Slot()
    def add_employee_popup(self):
        employee = backend.create_empty_employee()

        editor = EmployeeCreator(employee)
        editor.EMPLOYEE_UPDATED.connect(self.refresh_table)
        editor.DONE.connect(self.close_popup)

        self.launch_window("Add Employee", editor)

    @Slot(int, int)
    def edit_employee_popup(self, row, col):
        employee = self.table.get_employee_from_row(row)

        editor = EmployeeEditor(employee)
        editor.EMPLOYEE_UPDATED.connect(self.refresh_table)
        editor.DONE.connect(self.close_popup)

        self.launch_window("Edit Employee", editor)

    def import_csv_popup(self):
        importer = EmployeeImporter()
        importer.EMPLOYEES_UPDATED.connect(self.refresh_table)
        importer.DONE.connect(self.close_popup)

        self.launch_window("Import Employees", importer, self.width(), self.height())

    @Slot()
    def close_popup(self):
        if self.popup is not None:
            self.popup.close()
            self.popup = None

    @Slot()
    def refresh_table(self):
        employees = backend.get_employees()
        self.table.populate_table(employees)
