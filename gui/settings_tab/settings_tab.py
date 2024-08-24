from typing import Protocol

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Signal, Slot

from gui import gui_constants
from gui import gui_utils

from db.db_data import PayPeriod


# -------------------- INTERFACES [START] --------------------


class SettingsTabUI(Protocol):
    @property
    def update_btn(self) -> QPushButton:
        ...

    @property
    def pay_period(self) -> PayPeriod:
        ...
    
    def update_pay_period(self) -> None:
        ...


class SettingsService(Protocol):
    def update_pay_period(self, pay_period: PayPeriod) -> None:
        ...


# -------------------- INTERFACES [END] --------------------


class SettingsTab(QWidget):
    pay_period_updated = Signal()

    def __init__(self, ui: SettingsTabUI, service: SettingsService):
        super().__init__()

        self._service = service
        self._ui = ui
        self.setLayout(self._ui.layout())

        self._init_conns()

    def _init_conns(self):
        self._ui.update_btn.clicked.connect(self._handle_update_pay_period)

    @Slot()
    def _handle_update_pay_period(self):
        choice = gui_utils.show_dialog(
            gui_utils.DialogType.CONFIRM,
            "Update pay period?",
            "You will permanently lose all employee data. Please make sure " + \
            "that any timesheet reports are saved before proceeding."
        )

        if choice != QMessageBox.Yes:
            return

        try:
            self._service.update_pay_period(self._ui.pay_period)
        except Exception:
            gui_utils.show_dialog(
                gui_utils.DialogType.ERR, gui_constants.INTERNAL_ERR_MSG
            )
        else:
            self.pay_period_updated.emit()
            gui_utils.show_dialog(gui_utils.DialogType.INFO, "Pay period updated.")

    def update_pay_period(self, pay_period: PayPeriod) -> None:
        self._ui.update_pay_period(pay_period)
