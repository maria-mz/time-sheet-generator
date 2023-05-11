from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QDateEdit, QPushButton, QLineEdit, QMessageBox
from PySide6.QtCore import QDate, Qt, Signal, QObject, Slot
import sys
sys.path.append('../time-sheet-generator')
from database_handler import NUM_PAY_PERIOD_DAYS
from database_handler import DatabaseHandler
import datetime 


class PayPeriodWidget(QWidget, QObject):
    save_date_signal = Signal()
    
    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.handler = DatabaseHandler()

        if self.handler.has_start_date():
            year, month, day = self.handler.get_start_date()
            print(year, month, day)
            self.defaultDate = QDate(year, month, day)
        else:
            self.defaultDate = QDate.currentDate()

        # Create each element
        start_label = QLabel("Start Date")
        end_label = QLabel("End Date")
        self._start_date_field()
        self._end_date_field()
        self.start_date.userDateChanged.connect(self._on_date_changed)
        self._create_save_button("Apply")
        self.save_button.clicked.connect(self._on_saved)
        
        # Add each element to a vertical layout
        v_layout = QVBoxLayout()
        v_layout.addWidget(start_label)
        v_layout.addWidget(self.start_date)
        v_layout.addWidget(end_label)
        v_layout.addWidget(self.end_date)
        v_layout.addWidget(self.save_button, 0, Qt.AlignLeft)
        v_layout.setSpacing(12)
        v_layout.setAlignment(Qt.AlignCenter)

        # Set the layout
        self.setLayout(v_layout)
    
    def _start_date_field(self):
        field = QDateEdit()
        field.setCalendarPopup(True)
        field.setMaximumWidth(300)
        field.setStyleSheet("""
            QDateEdit {
                border: 1px solid #999999;
                border-radius: 2px;
                padding: 8px;
            }
        """)
        field.setDate(self.defaultDate)
        self.start_date = field

    def _end_date_field(self):
        field = QLineEdit(" ")
        field.setReadOnly(True) 
        field.setMaximumWidth(300)
        field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #999999;
                border-radius: 2px;
                padding: 8px;
                color: #808080;
                background-color: #F0F0F0;
            }
        """)

        self.end_date = field
        self._set_end_date(self.defaultDate.year(), self.defaultDate.month(), self.defaultDate.day())

    def _create_save_button(self, name):
        button = QPushButton(name)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 2px;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-weight: 500;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #3E8E41;
            }
        """)

        self.save_button = button
    
    def _set_end_date(self, year, month, day):
        date_obj = datetime.date(year, month, day) 
        date_obj += datetime.timedelta(days=NUM_PAY_PERIOD_DAYS - 1)
        self.end_date.setText(date_obj.strftime('%Y-%m-%d'))

    @Slot(QDate)
    def _on_date_changed(self, date):
        self._set_end_date(date.year(), date.month(), date.day())

    @Slot()
    def _on_saved(self):
        msg = QMessageBox()
        msg.setText("Apply this date?")
        msg.setInformativeText("This will update the database. You'll lose all Date, In/Out, Reg./OT data from the previous time period.")    
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)    
        input = msg.exec()

        if input == QMessageBox.Yes:
            date = self.start_date.date()
            self.handler.set_date_and_reset(date.year(), date.month(), date.day())
            self.save_date_signal.emit()

            # TODO: show message to screen, Saved!
