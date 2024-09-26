from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import Slot

from gui.settings_tab.settings_tab_ui import SettingsTabUI
from gui.settings_tab.settings_tab import SettingsTab
from gui.timesheet_tab.timesheet_tab_ui import TimesheetTabUI
from gui.timesheet_tab.timesheet_tab import TimesheetTab

from backend.backend import Backend
import constants


class MainWindow(QMainWindow):
    def __init__(self, backend: Backend):
        super().__init__()

        self._backend = backend

        pay_period = self._backend.get_pay_period()

        self.settings_tab = SettingsTab(SettingsTabUI(pay_period), backend)
        self.timesheet_tab = TimesheetTab(TimesheetTabUI(), backend)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle(constants.APP_NAME)

        self.setMinimumWidth(1024)
        self.setMinimumHeight(768)

        tabs = QTabWidget(self)

        tabs.addTab(self.settings_tab, "Settings")
        tabs.addTab(self.timesheet_tab, "Timesheet")

        tabs.currentChanged.connect(self._on_tab_changed)
        self.settings_tab.pay_period_updated.connect(self.timesheet_tab.refresh_tab)

        self.setCentralWidget(tabs)

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        # When we switch to "Settings" tab want to update pay period.
        # This is to handle the case when user updates pay period but doesn't
        # hit "Update". Want to show the active pay period again

        if index == 0:
            pay_period = self._backend.get_pay_period()
            self.settings_tab.update_pay_period(pay_period)
