from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QGridLayout,
    QGroupBox,
    QGridLayout
)
from PySide6.QtGui import QFont

from db.db_data import Employee


@dataclass
class QProfile:
    id_edit: QLineEdit
    first_name_edit: QLineEdit
    last_name_edit: QLineEdit
    position_edit: QLineEdit
    contract_edit: QLineEdit


class EmployeeProfile(QWidget):
    def __init__(self, employee: Employee):
        super().__init__()

        self._employee = employee
        self._qprofile = self._create_qprofile(employee)

        layout = QVBoxLayout()
        layout.addWidget(self._create_profile_box())

        self.setLayout(layout)

    def _create_qprofile(self, employee: Employee) -> QProfile:
        id_edit = QLineEdit(employee.employee_id)
        first_name_edit = QLineEdit(employee.first_name)
        last_name_edit = QLineEdit(employee.last_name)
        position_edit = QLineEdit(employee.position)
        contract_edit = QLineEdit(employee.contract)

        return QProfile(
            id_edit=id_edit,
            first_name_edit=first_name_edit,
            last_name_edit=last_name_edit,
            position_edit=position_edit,
            contract_edit=contract_edit
        )

    def _create_profile_box(self) -> QGroupBox:
        box = QGroupBox("Employee Profile")

        grid = QGridLayout()

        grid.addWidget(self._create_field_label("First Name"), 0, 0)
        grid.addWidget(self._create_field_label("Last Name"), 0, 2)
        grid.addWidget(self._create_field_label("Employee No"), 1, 2)
        grid.addWidget(self._create_field_label("Job Title"), 2, 0)
        grid.addWidget(self._create_field_label("Contract"), 2, 2)

        grid.addWidget(self._qprofile.first_name_edit, 0, 1)
        grid.addWidget(self._qprofile.last_name_edit, 0, 3)
        grid.addWidget(self._qprofile.id_edit, 1, 3)
        grid.addWidget(self._qprofile.position_edit, 2, 1)
        grid.addWidget(self._qprofile.contract_edit, 2, 3)

        box.setLayout(grid)

        return box

    def _create_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")

        return label

    def first_name(self) -> str:
        return self._qprofile.first_name_edit.text()

    def last_name(self) -> str:
        return self._qprofile.last_name_edit.text()

    def employee_id(self) -> str:
        return self._qprofile.id_edit.text()

    def position(self) -> str:
        return self._qprofile.position_edit.text()

    def contract(self) -> str:
        return self._qprofile.contract_edit.text()

    def set_id_editable(self, editable: bool) -> None:
        self._qprofile.id_edit.setEnabled(editable)
