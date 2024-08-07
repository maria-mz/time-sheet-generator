from PySide6.QtWidgets import (
    QWidget, 
    QAbstractItemView,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt

from db.db_data import Employee


HEADER_LABELS = ["First Name", "Last Name", "Employee No", "Job Title", "Contract"]


class EmployeesTable(QTableWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.employees = []

        self.setColumnCount(len(HEADER_LABELS))
        self.setHorizontalHeaderLabels(HEADER_LABELS)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set all columns to stretch
        for i in range(len(HEADER_LABELS)):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

    def populate_table(self, employees: list[Employee]) -> None:
        self.employees = employees

        self.clearContents()
        self.setRowCount(0)

        for row, employee in enumerate(employees):
            self.insertRow(row)

            profile_items = [
                employee.first_name,
                employee.last_name,
                employee.employee_id,
                employee.position,
                employee.contract
            ]

            for col, profile_item in enumerate(profile_items):
                qitem = QTableWidgetItem(profile_item)
                qitem.setFlags(~Qt.ItemIsEditable)

                self.setItem(row, col, qitem)

    def filter_table_by_name(self, name: str):
        self.setCurrentItem(None) # Clear the current selection

        std_name = name.lower().strip()

        for row in range(self.rowCount()):
            if self.get_employee_from_row(row).full_name.lower().startswith(std_name):
                self.setRowHidden(row, False)
            else:
                self.setRowHidden(row, True)

    def get_employee_from_row(self, row: int) -> Employee:
        return self.employees[row]
