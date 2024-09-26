from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Slot, Qt

from gui import gui_constants
from gui.settings_tab.settings_tab_ui import SettingsTabUI
from gui.settings_tab.settings_tab import SettingsTab
from gui.timesheet_tab.timesheet_tab_ui import TimesheetTabUI
from gui.timesheet_tab.timesheet_tab import TimesheetTab

from backend.backend import Backend
import constants


class MainWindow(QWidget):
    def __init__(self, backend: Backend):
        super().__init__()

        self._backend = backend

        pay_period = self._backend.get_pay_period()

        self.settings_tab = SettingsTab(SettingsTabUI(pay_period), backend)
        self.timesheet_tab = TimesheetTab(TimesheetTabUI(), backend)

        self.settings_tab.pay_period_updated.connect(self.timesheet_tab.refresh_tab)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle(constants.APP_NAME)
        self.setMinimumWidth(gui_constants.WINDOW_WIDTH)
        self.setMinimumHeight(gui_constants.WINDOW_HEIGHT)

        tabs = self._create_tabs()
        tabs.currentChanged.connect(self._on_tab_changed)

        version = QLabel(f"Version: {constants.VERSION}")

        layout = QVBoxLayout()

        layout.addWidget(tabs)
        layout.addWidget(version, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def _create_tabs(self) -> QTabWidget:
        tabs = QTabWidget(self)

        tabs.addTab(self.settings_tab, "Settings")
        tabs.addTab(self.timesheet_tab, "Timesheet")

        return tabs

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        # When we switch to "Settings" tab want to update pay period.
        # This is to handle the case when user updates pay period but doesn't
        # hit "Update". Want to show the active pay period again

        if index == 0:
            pay_period = self._backend.get_pay_period()
            self.settings_tab.update_pay_period(pay_period)
