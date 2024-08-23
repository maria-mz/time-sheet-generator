from enum import Enum, auto

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)
from enum import Enum

from gui.employee_profile import EmployeeProfile
from gui.timesheet_editor.timesheet_editor import TimesheetEditor

from db.db_data import Employee


class EditorMode(Enum):
    EDIT = auto()
    CREATE = auto()


class EmployeeEditorUI(QWidget):
    def __init__(self, mode: EditorMode, employee: Employee):
        super().__init__()

        self.delete_employee_btn = QPushButton("Delete Employee")
        self.cancel_btn = QPushButton("Cancel")
        self.save_employee_btn = QPushButton("Save")
        self.add_employee_btn = QPushButton("Add Employee")

        self._profile_widget = EmployeeProfile(employee)
        self._profile_widget.setTitle("Employee Details")

        self._timesheet_editor = TimesheetEditor(employee)
 
        self._init_ui(mode)

    def _init_ui(self, mode: EditorMode) -> QVBoxLayout:
        btns_layout = QHBoxLayout()
        btns_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        if mode == EditorMode.CREATE:
            btns_layout.addItem(btns_spacer)
            btns_layout.addWidget(self.cancel_btn)
            btns_layout.addWidget(self.add_employee_btn)

        elif mode == EditorMode.EDIT:
            btns_layout.addWidget(self.delete_employee_btn)
            btns_layout.addItem(btns_spacer)
            btns_layout.addWidget(self.cancel_btn)
            btns_layout.addWidget(self.save_employee_btn)

            self._profile_widget.set_id_enabled(False)

        layout = QVBoxLayout()

        layout.addWidget(self._profile_widget)
        layout.addWidget(self._timesheet_editor)
        layout.addLayout(btns_layout)

        self.setLayout(layout)

    def get_employee(self) -> Employee:
        return Employee(
            employee_id=self._profile_widget.employee_id,
            first_name=self._profile_widget.first_name,
            last_name=self._profile_widget.last_name,
            position=self._profile_widget.position,
            contract=self._profile_widget.contract,
            shifts=self._timesheet_editor.get_shifts()
        )

    @property
    def employee_id(self) -> str:
        return self._profile_widget.employee_id
