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
from PySide6.QtCore import Qt

from db.db_data import Employee


@dataclass
class QProfile:
    id_edit: QLineEdit
    name_edit: QLineEdit
    position_edit: QLineEdit


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
        name_edit = QLineEdit(employee.full_name)
        position_edit = QLineEdit(employee.position)

        return QProfile(
            id_edit=id_edit,
            name_edit=name_edit,
            position_edit=position_edit
        )

    def _create_profile_box(self) -> QGroupBox:
        box = QGroupBox("Employee Profile")

        grid = QGridLayout()

        name_label = QLabel("Full Name")
        id_label = QLabel("Employee #")
        position_label = QLabel("Job Title")
    
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self._qprofile.name_edit, 0, 1)
        grid.addWidget(id_label, 0, 2)
        grid.addWidget(self._qprofile.id_edit, 0, 3)
        grid.addWidget(position_label, 1, 0)
        grid.addWidget(self._qprofile.position_edit, 1, 1)

        container = QVBoxLayout()
        container.addLayout(grid)
        container.setAlignment(Qt.AlignTop)

        box.setLayout(container)

        return box

    def get_full_name(self) -> str:
        return self._qprofile.name_edit.text()

    def get_employee_id(self) -> str:
        return self._qprofile.id_edit.text()

    def get_position(self) -> str:
        return self._qprofile.position_edit.text()

    def set_id_editable(self, editable: bool) -> None:
        self._qprofile.id_edit.setEnabled(editable)
