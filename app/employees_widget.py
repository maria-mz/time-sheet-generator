import sys

from PySide6.QtWidgets import (
    QWidget, 
    QAbstractItemView,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QColor, QFont
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

        self.setup_header()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.init_search_bar()

        # Table with employees data
        self.table = QTableWidget(self)
        self.init_table()

        # Set layout for the main window
        self.set_main_layout()

    def setup_header(self):
        # Title 
        self.title = QLabel("Employees")
        self.title.setStyleSheet("font-weight: bold; font-size: 24px")

        # Button(s)
        self.add_employee_btn = QPushButton("Add Employee")
        self.add_employee_btn.clicked.connect(self.add_employee)

    def init_search_bar(self):
        """
        Sets the max length, placeholder text, and signal slot for the search bar.
        """
        self.search_bar.setMaxLength(40)
        self.search_bar.setPlaceholderText("Search by name")
        self.search_bar.textChanged.connect(self.filter_table_by_name)

    def init_table(self):
        """
        Populates and sets the properties for the employeees table. 
        """
        self.table.setColumnCount(COUNT_PROFILE + (COUNT_WORKDAY * COUNT_PAYPERIOD))

        # Populate the table
        self.refresh_table()

        # Hide the first column with the ID
        self.table.setColumnHidden(0, True)     

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.cellDoubleClicked.connect(self.edit_employee)

    def set_main_layout(self):
        """
        Creates and sets the layout for the EmployeesWidget.
        """
        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title)

        # Add a horizontal spacer to keep the title and button apart
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        header_layout.addItem(spacer)

        header_layout.addWidget(self.add_employee_btn)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def refresh_table(self):
        """
        Refreshes the table. This updates the contents of each cell. 
        """
        self.table.clearContents()
        self.table.setRowCount(0)  # Reset row count to 0
        self.set_all_headers()
        self.populate_table()
        self.table.resizeColumnsToContents()
        
    def insert_table_item(self, row, column, content):
        """
        Inserts a cell into the table that is non-editable, and bolded if a week day.

        Parameters:
            row (int): the row of the cell.
            column (int): the column of the cell.
            content (int, str, float): what is inside the cell.
        """
        item = QTableWidgetItem(content)
        item.setFlags(~Qt.ItemIsEditable)

        if (column - COUNT_PROFILE) % COUNT_WORKDAY == 0:
            font = QFont()
            font.setBold(True)
            item.setFont(font)

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
                    day['regular_hours'],
                    day['overtime_hours']
                ])
            self.insert_table_items(row, COUNT_PROFILE, contents)

    def get_id(self, row):
        """
        Finds the ID of an employee from the table and returns it.

        Parameters:
            row (int): the row corresponding to the employee.

        Returns:
            A string representing the employee's ID.
        """
        return self.table.item(row, 0).text()

    def create_window(self, title, layout):
        self.employee_popup = QWidget()
        self.employee_popup.setGeometry(900, 150, 500, 300)
        self.employee_popup.setWindowTitle(title)
        self.employee_popup.setLayout(layout)
        self.employee_popup.show()
        
    """
    Slots
    """
    @Slot(str)
    def filter_table_by_name(self, query):
        """
        Filters out rows of the table not containing the query. Filters by employee name.

        Parameters:
            query (str): contents of search bar.
        """
        # Clear the current selection
        self.table.setCurrentItem(None)

        for row in range(self.table.rowCount()):
            if query.lower().strip() not in self.table.item(row, 1).text().lower():
                self.table.setRowHidden(row, True)
            else:
                self.table.setRowHidden(row, False)

    @Slot()
    def add_employee(self):
        layout = EmployeeInfoLayout(isEdit=False)
        layout.finished_edit_signal.connect(self.close_employee)

        self.create_window("Add Employee", layout)

    @Slot(int, int)
    def edit_employee(self, row, column):
        data = self.handler.get_employee(id=self.get_id(row))
        layout = EmployeeInfoLayout(isEdit=True, data=data)
        layout.finished_edit_signal.connect(self.close_employee)

        self.create_window("Edit Employee", layout)

    @Slot()
    def close_employee(self):
        self.employee_popup.close()
        self.refresh_table()
