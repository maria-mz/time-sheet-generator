import sys

from PySide6.QtWidgets import (
    QWidget, 
    QAbstractItemView,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Slot
from database_handler import DatabaseHandler
from employee_info_layout import EmployeeInfoLayout

sys.path.append('../time-sheet-generator')

COUNT_PAYPERIOD = 14
COUNT_WORKDAY = 6
COUNT_PROFILE = 3

class EmployeesWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the table
        self.table = QTableWidget(self)
        self.table.setColumnCount(COUNT_PROFILE + (COUNT_WORKDAY * COUNT_PAYPERIOD))
        self.refresh_table()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        # Set layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh_table(self):
        """
        Refreshes the table. This updates the contents of each cell. 
        """
        self.table.clearContents()
        self.table.setRowCount(0)  # Reset row count to 0
        self.set_all_headers()
        self.populate_table()
        
    def insert_table_item(self, row, column, content):
        """
        Inserts a cell into the table that is non-editable, and highlighted if a week day.

        Parameters:
            row (int): the row of the cell.
            column (int): the column of the cell.
            content (int, str, float): what is inside the cell.
        """
        item = QTableWidgetItem(content)
        item.setFlags(~Qt.ItemIsEditable)

        if (column - COUNT_PROFILE) % COUNT_WORKDAY == 0:
            item.setBackground(QColor(224, 229, 233))

        self.table.setItem(row, column, item)

    def insert_table_items(self, row, column_start, contents):
        """
        Sequentially inserts a group of cells into a specific row.

        Parameters:
            row (int): the row for the cells.
            column_start (int): the starting column for the first cell.
            contents (list): a list containing the content for each cell.
        """
        for i, content in enumerate(contents):
            self.insert_table_item(row, column_start + i, content)

    def set_header_name(self, column, name):
        """
        Sets a header name for a specific column.

        Parameters:
            column (int): the column of the header.
            name (str): the name for the header.
        """
        header_item = QTableWidgetItem(name)
        self.table.setHorizontalHeaderItem(column, header_item)

    def set_all_headers(self):
        """
        Sets the header names for all columns of the table.
        """
        profile_names = ["ID", "Full Name", "Job Title"]
        workday_names = ["Day", "Date", "In", "Out", "Reg", "OT"]

        for i, profile_name in enumerate(profile_names):
            self.set_header_name(i, profile_name)
       
        for i in range(COUNT_PAYPERIOD):
            column_offset = COUNT_PROFILE + (i * COUNT_WORKDAY)
            day = i + 1
            for j, workday_name in enumerate(workday_names):
                self.set_header_name(column_offset + j, f'{workday_name} {day}')

    def populate_table(self):
        """
        Populates the table from employee data. 
        """
        self.handler = DatabaseHandler()
        data = self.handler.get_all_employees()

        for row, employee in enumerate(data):
            self.table.insertRow(row)
            contents = []

            # Insert profile data (ID, Name, Job Title)
            contents.extend([
                str(employee['_id']),
                employee['full_name'],
                employee['job_title']
            ])
            self.insert_table_items(row, 0, contents)
            contents.clear()

            # Insert work-day data for each day in the pay period (Day, Date, In, Out, Reg, OT)
            days = employee['work_days']
            for day in days:
                contents.extend([
                    day['day_of_week'],
                    day['work_date'],
                    day['time_in'],
                    day['time_out'],
                    str(format(day['regular_hours'], '.2f')),
                    str(format(day['overtime_hours'], '.2f'))
                ])
            self.insert_table_items(row, COUNT_PROFILE, contents)
        
        self.table.setColumnHidden(0, True)
        self.table.resizeColumnsToContents()

    def get_id(self, row):
        """
        Finds the ID of an employee from the table and returns it.

        Parameters:
            row (int): the row corresponding to the employee.

        Returns:
            A string representing the employee's ID.
        """
        return self.table.item(row, 0).text()
    
    @Slot(int, int)
    def on_cell_double_clicked(self, row, column):
        self.employee_popup = QWidget()
        self.employee_popup.setGeometry(900, 150, 500, 300)

        data = self.handler.get_employee(id=self.get_id(row))

        employee_info_layout = EmployeeInfoLayout(data)
        employee_info_layout.edit_signal.connect(self._on_employee_edited)

        self.employee_popup.setLayout(employee_info_layout)
        self.employee_popup.show()

    @Slot()
    def _on_employee_edited(self):
        self.employee_popup.close()
        self.refresh_table()
