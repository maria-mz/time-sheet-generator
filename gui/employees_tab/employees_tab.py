from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QFrame
)
from PySide6.QtCore import Slot

from gui.employees_tab.employees_table import EmployeesTable
from gui.employees_tab.employee_editor import EmployeeEditor, EditorMode
from gui.employees_tab.employee_importer import EmployeeImporter

from backend.backend import backend


class EmployeesTab(QWidget):
    def __init__(self):
        super().__init__()

        employees = backend.get_employees()

        self.title = QLabel()
        self._update_title(len(employees))
        self.title.setStyleSheet("font-weight: bold; font-size: 24px")

        self.table = EmployeesTable()
        self.table.populate_table(employees)
        self.table.cellDoubleClicked.connect(self._open_edit_employee_window)

        self.search_bar = self._create_search_bar()

        self.window_popup = None

        layout = self._create_main_layout()

        self.setLayout(layout)

    def _create_main_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        header_layout = self._create_header_layout()
        buttons = self._create_buttons()

        # Create this container for custom spacing between search bar and table
        container = QVBoxLayout()
        container.setSpacing(16)
        container.addWidget(self.search_bar)
        container.addWidget(self.table)

        layout.addLayout(header_layout)
        layout.addLayout(container)
        layout.addLayout(buttons)

        return layout

    def _create_header_layout(self) -> QHBoxLayout:
        subtitle = QLabel(
            "Edit employee details and timesheet information here. " + \
            "Click an employee to open the editor."
        )

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout()

        layout.addWidget(self.title)
        layout.addWidget(subtitle)
        layout.addWidget(line)

        return layout

    def _create_search_bar(self) -> QLineEdit:
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by first name")
        search_bar.textChanged.connect(self.table.filter_table_by_first_name)

        return search_bar

    def _create_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        import_btn = QPushButton("Import Employees")
        import_btn.clicked.connect(self._open_import_employees_window)

        add_btn = QPushButton("Add Employee")
        add_btn.clicked.connect(self._open_add_employee_window)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

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

    def clear_search_bar(self) -> None:
        self.search_bar.setText("")
    
    def _update_title(self, num_employees: int) -> None:
        self.title.setText(f"Employees ({num_employees})")

    @Slot()
    def close_window_popup(self):
        if self.window_popup is not None:
            self.window_popup.close()
            self.window_popup = None

    @Slot()
    def refresh_tab(self):
        employees = backend.get_employees()
        self.table.populate_table(employees)
        self._update_title(len(employees))
        self.clear_search_bar()
