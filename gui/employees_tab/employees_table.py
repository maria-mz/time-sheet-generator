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

    def filter_by_first_name(self, name: str):
        relaxed_name = name.lower().strip()

        def query(employee: Employee) -> bool:
            return employee.first_name.lower().startswith(relaxed_name)

        self._filter(query)
    
    def filter_by_last_name(self, name: str):
        relaxed_name = name.lower().strip()

        def query(employee: Employee) -> bool:
            return employee.last_name.lower().startswith(relaxed_name)

        self._filter(query)

    def filter_by_position(self, position: str):
        relaxed_position = position.lower().strip()

        def query(employee: Employee) -> bool:
            return employee.position.lower().startswith(relaxed_position)

        self._filter(query)

    def filter_by_contract(self, contract: str):
        relaxed_contract = contract.lower().strip()

        def query(employee: Employee) -> bool:
            return employee.contract.lower().startswith(relaxed_contract)

        self._filter(query)

    def _filter(self, query) -> None:
        self.setCurrentItem(None) # Clear the current selection

        for row in range(self.rowCount()):
            employee = self.get_employee_from_row(row)

            if query(employee):
                self.setRowHidden(row, False)
            else:
                self.setRowHidden(row, True)

    def get_employee_from_row(self, row: int) -> Employee:
        return self.employees[row]
