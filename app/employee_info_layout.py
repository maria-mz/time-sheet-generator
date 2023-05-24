import sys
import datetime 
import calendar

from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QGroupBox,
    QComboBox,
    QSizePolicy,
    QSpacerItem,
    QGridLayout,
    QCompleter,
    QPushButton,
    QMessageBox
)
from database_handler import DatabaseHandler
from database_handler import NUM_PAY_PERIOD_DAYS

sys.path.append('../time-sheet-generator')

MAX_LEN_PROFILE = 40
MAX_LEN_TIME = 8
MAX_LEN_HOURS = 5

class EmployeeInfoLayout(QVBoxLayout):
    finished_edit_signal = Signal()

    def __init__(self, data):
        super().__init__()

        self.handler = DatabaseHandler()
        self.data = data

        # Initialize profile field attributes
        profile_attributes = ['full_name', 'job_title']

        for attribute in profile_attributes:
            field = self.init_input_field(self.get_data_attribute(attribute), MAX_LEN_PROFILE)
            setattr(self, f'{attribute}_field', field)

        # Initialize date field attribute
        self.date_field = self.init_date_selector()

        # Initialize workday field attributes
        workday_attributes = ['time_in', 'time_out', 'regular_hours', 'overtime_hours']

        for i, attribute in enumerate(workday_attributes):
            default_value = self.get_workday_attribute_at_index(0, attribute)
            field = self.init_input_field(default_value, MAX_LEN_TIME if i < 2 else MAX_LEN_HOURS)
            setattr(self, f'{attribute}_field', field)

        self.connect_signals()
       
        # Set the layout
        employee_box = QGroupBox("Employee Information")
        employee_box.setLayout(self.init_layout())
        self.addWidget(employee_box)

    def get_data_attribute(self, attribute):
        return self.data[attribute]
    
    def set_data_attribute(self, attribute, new_value):
        self.data[attribute] = new_value

    def get_workday_attribute_at_index(self, index, attribute):
        return self.data['work_days'][index][attribute]

    def set_workday_attribute_at_index(self, index, attribute, new_value):
        self.data['work_days'][index][attribute] = new_value

    def init_input_field(self, content, max_chars):
        field = QLineEdit(content)
        field.setMaxLength(max_chars)
        return field
    
    def init_date_selector(self):
        selector = QComboBox()

        year, month, day = self.handler.get_start_date()
        date_obj = datetime.date(year, month, day)

        for i in range(NUM_PAY_PERIOD_DAYS):
            day_of_week = calendar.day_name[date_obj.weekday()]
            date = date_obj.strftime('%m/%d/%Y')
            selection = f'{day_of_week}, {date}'
            selector.addItem(selection)
            date_obj += datetime.timedelta(days=1)

        return selector

    def connect_signals(self):
        self.date_field.currentIndexChanged.connect(self.on_date_selected)
        self.time_in_field.editingFinished.connect(self.on_time_in_edited)
        self.time_out_field.editingFinished.connect(self.on_time_out_edited)
        self.regular_hours_field.editingFinished.connect(self.on_regular_hours_edited)
        self.overtime_hours_field.editingFinished.connect(self.on_overtime_hours_edited)

    def init_layout(self):
        main_layout = QVBoxLayout()
        
        # Sublayout (1). Holds the profile fields + date selector.
        profile_date_layout = self.create_profile_date_layout()

        # Sublayout (2). Holds the Time Group and Hours Group.
        time_hours_layout = QHBoxLayout()

        time_group = self.create_time_widget()
        time_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        hours_group = self.create_hours_widget()
        hours_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        time_hours_layout.addWidget(time_group)
        time_hours_layout.addWidget(hours_group)

        # Sublayout (3). Holds the buttons.
        button_layout = self.create_buttons_layout()

        # Add all three Sublayouts to the main layout
        main_layout.addLayout(profile_date_layout)
        main_layout.addLayout(time_hours_layout)
        main_layout.addLayout(button_layout)

        # Add a Vertical Spacer to keep the Sub-Layouts stacked together
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        return main_layout

    def create_profile_date_layout(self):
        grid_layout = QGridLayout()

        # Create labels and add them to the layout
        label_names = ["Full Name:", "Job Title:", "Work Day:"]

        for row, name in enumerate(label_names):
            label = QLabel(name)
            label.setStyleSheet("font-weight: bold;")
            grid_layout.addWidget(label, row, 0)

        # Add input fields to layout
        grid_layout.addWidget(self.full_name_field, 0, 1)
        grid_layout.addWidget(self.job_title_field, 1, 1)
        grid_layout.addWidget(self.date_field, 2, 1)

        return grid_layout

    def create_time_widget(self):
        time_box = QGroupBox("Time")
        grid_layout = QGridLayout()

        # Create labels and add them to the layout
        label_names = ["In:", "Out:"]

        for row, name in enumerate(label_names):
            label = QLabel(name)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setStyleSheet("font-weight: bold;")
            grid_layout.addWidget(label, row, 0)

        # Add input fields to layout
        grid_layout.addWidget(self.time_in_field, 0, 1)
        grid_layout.addWidget(self.time_out_field, 1, 1)

        # Set the widget's layout
        time_box.setLayout(grid_layout)

        return time_box

    def create_hours_widget(self):
        hours_box = QGroupBox("Hours")
        grid_layout = QGridLayout()

        # Create labels and add them to the layout
        label_names = ["Reg:", "OT:"]

        for row, name in enumerate(label_names):
            label = QLabel(name)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setStyleSheet("font-weight: bold;")
            grid_layout.addWidget(label, row, 0)

        # Add input fields to layout
        grid_layout.addWidget(self.regular_hours_field, 0, 1)
        grid_layout.addWidget(self.overtime_hours_field, 1, 1)
        
        # Set the widget's layout
        hours_box.setLayout(grid_layout)

        return hours_box

    def create_buttons_layout(self):
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.on_save)

        delete_button = QPushButton("Delete Employee")
        delete_button.clicked.connect(self.on_delete)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        button_layout.addWidget(delete_button)
        button_layout.addItem(spacer)
        button_layout.addWidget(save_button)

        return button_layout

    def update_workday_fields(self, index):
        self.time_in_field.setText(self.get_workday_attribute_at_index(index,'time_in'))
        self.time_out_field.setText(self.get_workday_attribute_at_index(index,'time_out'))
        self.regular_hours_field.setText(self.get_workday_attribute_at_index(index,'regular_hours'))
        self.overtime_hours_field.setText(self.get_workday_attribute_at_index(index,'overtime_hours'))

    def save_fields_to_data(self):
        index = self.date_field.currentIndex()
        self.set_data_attribute('full_name', self.full_name_field.text())
        self.set_data_attribute('job_title', self.job_title_field.text())
        self.set_workday_attribute_at_index(index, 'time_in', self.time_in_field.text())
        self.set_workday_attribute_at_index(index, 'time_out',  self.time_out_field.text())
        self.set_workday_attribute_at_index(index, 'regular_hours',  self.regular_hours_field.text())
        self.set_workday_attribute_at_index(index, 'overtime_hours',  self.overtime_hours_field.text())

    """
    Slots for editing data fields.
    """
    @Slot(int)
    def on_date_selected(self, index):
        self.update_workday_fields(index)

    @Slot()
    def on_time_in_edited(self):
        index = self.date_field.currentIndex()
        self.set_workday_attribute_at_index(index, 'time_in', self.time_in_field.text())

    @Slot()
    def on_time_out_edited(self):
        index = self.date_field.currentIndex()
        self.set_workday_attribute_at_index(index, 'time_out', self.time_out_field.text())

    @Slot()
    def on_regular_hours_edited(self):
        index = self.date_field.currentIndex()
        self.set_workday_attribute_at_index(index, 'regular_hours', self.regular_hours_field.text())

    @Slot()
    def on_overtime_hours_edited(self):
        index = self.date_field.currentIndex()
        self.set_workday_attribute_at_index(index, 'overtime_hours', self.overtime_hours_field.text())

    @Slot()
    def on_save(self):
        # Save each field currently in the view
        self.save_fields_to_data()

        # Update the database with the new data
        self.handler.update_employee(self.get_data_attribute('_id'), self.data)

        # Signify that editing is now finished
        self.finished_edit_signal.emit()

    @Slot()
    def on_delete(self):
        # Show confirmation message
        msg = QMessageBox()
        msg.setText("Delete this employee?")
        msg.setInformativeText("This will permanently delete the employee and their data.")    
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)    
        choice = msg.exec()

        if choice == QMessageBox.Yes:
            # Update the database
            self.handler.delete_employee(self.get_data_attribute('_id'))

            # Signify that editing is now finished
            self.finished_edit_signal.emit()

        # Else, do nothing
    
    
