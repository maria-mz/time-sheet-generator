from enum import Enum

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


class FilterIndex(Enum):
    FIRST_NAME = 0
    LAST_NAME = 1
    EMPLOYEE_ID = 2
    POSITION = 3
    CONTRACT = 4


class EmployeesTable(QTableWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.employees = []
        self._filter_queries = [None] * len(FilterIndex)

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
        
        self._filter()

    def filter_by_first_name(self, name: str):
        self._filter_by("first_name", FilterIndex.FIRST_NAME, name)

    def filter_by_last_name(self, name: str):
        self._filter_by("last_name", FilterIndex.LAST_NAME, name)

    def filter_by_position(self, position: str):
        self._filter_by("position", FilterIndex.POSITION, position)

    def filter_by_id(self, employee_id: str):
        self._filter_by("employee_id", FilterIndex.EMPLOYEE_ID, employee_id)

    def filter_by_contract(self, contract: str):
        self._filter_by("contract", FilterIndex.CONTRACT, contract)

    def _filter_by(
        self,
        employee_attr: str,
        filter_index: FilterIndex,
        target: str
    ) -> None:
        normalized_target = self._normalize(target)

        def query(employee: Employee) -> bool:
            return getattr(employee, employee_attr).lower().startswith(normalized_target)

        self._filter_queries[filter_index.value] = query

        self._filter()

    def _filter(self) -> None:
        self.setCurrentItem(None) # Clear the current selection

        for row in range(self.rowCount()):
            employee = self.get_employee_from_row(row)

            matches_queries = all(
                query(employee) if query is not None else True \
                for query in self._filter_queries
            )

            self.setRowHidden(row, not matches_queries)

    def _normalize(self, val: str) -> str:
        return val.strip().lower()

    def get_employee_from_row(self, row: int) -> Employee:
        return self.employees[row]

    def get_employees_matching_filter(self) -> list[Employee]:
        return [
            self.get_employee_from_row(row)
            for row in range(self.rowCount())
            if not self.isRowHidden(row)
        ]
