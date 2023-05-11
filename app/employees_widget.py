from PySide6.QtWidgets import QWidget, QAbstractItemView, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PySide6.QtCore import Qt, Slot
import sys
sys.path.append('../time-sheet-generator')
from database_handler import DatabaseHandler
from database_handler import NUM_PAY_PERIOD_DAYS

class EmployeesWidget(QWidget):
    def __init__(self):
        super().__init__()

        widget = QWidget(self)

        # Set up the table properties
        self.table = QTableWidget(self)
        self.table.setColumnCount(2 + (6 * NUM_PAY_PERIOD_DAYS))
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.set_headers()
        self.populate_table()
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        # Set layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_table(self):
        self.table.clearContents()
        self.set_headers()
        self.populate_table()
        
    def add_table_item(self, row, col, content):
        """
        Adds a non-editable cell to the table
        """
        item = QTableWidgetItem(content)
        item.setFlags(~Qt.ItemIsEditable)
        self.table.setItem(row, col, item)

    def set_column_header(self, col, title):
        """
        Sets a header name for a specific column
        """
        header_item = QTableWidgetItem(title)
        self.table.setHorizontalHeaderItem(col, header_item)

    def set_headers(self):
        """
        Sets all column headers
        """
        self.set_column_header(0, "Full Name")
        self.set_column_header(1, "Job Title")

        for i in range(NUM_PAY_PERIOD_DAYS):
            self.set_column_header(i * 6 + 2, "Day " + str(i+1))
            self.set_column_header(i * 6 + 3, "Date " + str(i+1))
            self.set_column_header(i * 6 + 4, "In " + str(i+1))
            self.set_column_header(i * 6 + 5, "Out " + str(i+1))
            self.set_column_header(i * 6 + 6, "Reg " + str(i+1))
            self.set_column_header(i * 6 + 7, "OT " + str(i+1))

    def populate_table(self):
        """
        Populates table from employee data 
        """
        handler = DatabaseHandler()
        data = handler.get_all_employees()

        for row, employee in enumerate(data):
            self.table.insertRow(row)
            self.add_table_item(row, 0, employee['full_name'])
            self.add_table_item(row, 1, employee['job_title'])

            work_days = employee['work_days']
            for col, work_day in enumerate(work_days):
                self.add_table_item(row, col * 6 + 2, work_day['day_of_week'])
                self.add_table_item(row, col * 6 + 3, work_day['work_date'])
                self.add_table_item(row, col * 6 + 4, work_day['time_in'])
                self.add_table_item(row, col * 6 + 5, work_day['time_out'])
                self.add_table_item(row, col * 6 + 6, str(format(work_day['regular_hours'], '.2f')))
                self.add_table_item(row, col * 6 + 7, str(format(work_day['overtime_hours'], '.2f')))

    @Slot(int, int)
    def on_cell_double_clicked(self, row, col):
        self.new_window = QWidget()
        self.new_window.setGeometry(900, 150, 400, 300)

        self.new_window.setWindowTitle(f"Row {row} Double Clicked")
        self.new_window.show()
        
        