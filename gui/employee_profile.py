from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QGridLayout,
    QGroupBox,
    QGridLayout
)
from PySide6.QtGui import QFont

from db.db_data import Employee


class EmployeeProfile(QGroupBox):
    def __init__(self, employee: Employee = None):
        super().__init__()

        self.id_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.position_edit = QLineEdit()
        self.contract_edit = QLineEdit()

        if employee:
            self.populate_profile(employee)

        layout = self._create_layout()

        self.setLayout(layout)

    def populate_profile(self, employee: Employee) -> None:
        self.id_edit.setText(employee.employee_id)
        self.first_name_edit.setText(employee.first_name)
        self.last_name_edit.setText(employee.last_name)
        self.position_edit.setText(employee.position)
        self.contract_edit.setText(employee.contract)

    def _create_layout(self) -> QGridLayout:
        grid = QGridLayout()

        grid.addWidget(self._create_field_label("First Name"), 0, 0)
        grid.addWidget(self._create_field_label("Last Name"), 0, 2)
        grid.addWidget(self._create_field_label("Employee No"), 1, 2)
        grid.addWidget(self._create_field_label("Job Title"), 2, 0)
        grid.addWidget(self._create_field_label("Contract"), 2, 2)

        grid.addWidget(self.first_name_edit, 0, 1)
        grid.addWidget(self.last_name_edit, 0, 3)
        grid.addWidget(self.id_edit, 1, 3)
        grid.addWidget(self.position_edit, 2, 1)
        grid.addWidget(self.contract_edit, 2, 3)

        return grid

    def _create_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")

        return label

    @property
    def first_name(self) -> str:
        return self.first_name_edit.text()

    @property
    def last_name(self) -> str:
        return self.last_name_edit.text()

    @property
    def employee_id(self) -> str:
        return self.id_edit.text()

    @property
    def position(self) -> str:
        return self.position_edit.text()

    @property
    def contract(self) -> str:
        return self.contract_edit.text()
