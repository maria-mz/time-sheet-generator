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

        pay_period = self.get_pay_period()

        self.settings_tab = SettingsTab(pay_period)

        self.settings_tab.PAY_PERIOD_UPDATED.connect(self._on_save_update_table)

        self.employees_tab = EmployeesTab()
        export_tab = QWidget() # TODO

        # Add tabs to widget
        tabs.addTab(self.settings_tab, "Settings")
        tabs.addTab(self.employees_tab, "Employees")
        tabs.addTab(export_tab, "Report")

        tabs.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(tabs)

    def get_pay_period(self) -> PayPeriod:
        pay_period = backend.get_pay_period()

        if pay_period is not None:
            return pay_period

        start_date = datetime.datetime.now().date()
        end_date = utils.next_date(start_date, constants.PAY_PERIOD_DAYS - 1)

        return PayPeriod(start_date, end_date)

    @Slot()
    def _on_save_update_table(self) -> None:
        self.employees_tab.refresh_tab()

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        # When we switch to "Settings" tab want to update pay period.
        # This is to handle the case when user updates pay period but doesn't
        # hit "Update". Want to show the active pay period again

        if index == 0:
            pay_period = self.get_pay_period()
            self.settings_tab.update_pay_period(pay_period)
