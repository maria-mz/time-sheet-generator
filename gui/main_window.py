import datetime

from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget
from PySide6.QtCore import Slot

from gui.settings_tab.settings_tab import SettingsTab
from gui.employees_tab.employees_tab import EmployeesTab

from backend.backend import backend
from db.db_data import PayPeriod
import utils
import constants


# TODO: handle all backend interaction here, in one place? (use signals)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(constants.APP_NAME)

        self.setMinimumWidth(800)
        self.setMinimumHeight(600)


        tabs = QTabWidget(self)

        pay_period = backend.get_pay_period()

        if pay_period is None:
            start_date = datetime.datetime.now().date()
            end_date = utils.next_date(start_date, constants.PAY_PERIOD_DAYS - 1)

            pay_period = PayPeriod(start_date, end_date)

        self.settings_tab = SettingsTab(pay_period)

        self.settings_tab.PAY_PERIOD_UPDATED.connect(self._on_save_update_table)

        self.employees_tab = EmployeesTab()
        export_tab = QWidget() # TODO

        # Add tabs to widget
        tabs.addTab(self.settings_tab, "Settings")
        tabs.addTab(self.employees_tab, "Employees")
        tabs.addTab(export_tab, "Report")

        self.setCentralWidget(tabs)

    @Slot()
    def _on_save_update_table(self):
        self.employees_tab.refresh_table()
