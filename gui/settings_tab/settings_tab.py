from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QDateEdit,
    QPushButton,
    QMessageBox,
    QFrame
)
from PySide6.QtCore import QDate, Qt, Signal, Slot

import gui.constants
from gui import qutils

from backend.backend import backend
from backend.errors import InternalError
from db.db_data import PayPeriod
import utils
import constants


@dataclass
class QPayPeriod:
    start_date_edit: QDateEdit
    end_date_edit: QDateEdit


class SettingsTab(QWidget):
    PAY_PERIOD_UPDATED = Signal()

    def __init__(self, pay_period: QPayPeriod):
        super().__init__()

        self.widget = QWidget()

        self.q_pay_period = self._create_q_pay_period(pay_period)

        layout = self.create_layout()
        self.setLayout(layout)

    def _create_q_pay_period(self, pay_period: PayPeriod) -> QPayPeriod:
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setFixedWidth(200)
        start_date_edit.setDate(qutils.date_to_qdate(pay_period.start_date))
        start_date_edit.userDateChanged.connect(self._on_start_date_changed)

        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(False)
        end_date_edit.setEnabled(False)
        end_date_edit.setFixedWidth(200)
        end_date_edit.setDate(qutils.date_to_qdate(pay_period.end_date))

        return QPayPeriod(
            start_date_edit=start_date_edit, end_date_edit=end_date_edit
        )

    def create_layout(self) -> QVBoxLayout:
        base_layout = QVBoxLayout()

        title = QLabel("Pay Period")
        title.setStyleSheet("font-weight: bold; font-size: 24px")

        base_layout.addWidget(title, alignment=Qt.AlignLeft)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        base_layout.addWidget(line)

        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(QLabel("Start Date"))
        start_date_layout.addWidget(self.q_pay_period.start_date_edit)

        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(QLabel("End Date"))
        end_date_layout.addWidget(self.q_pay_period.end_date_edit)

        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._on_update)

        base_layout.addLayout(start_date_layout)
        base_layout.addLayout(end_date_layout)

        base_layout.addWidget(update_btn, 0, Qt.AlignRight)
        base_layout.setSpacing(12)
        base_layout.setAlignment(Qt.AlignCenter)

        return base_layout

    @Slot(QDate)
    def _on_start_date_changed(self, date: QDate):
        end_date = utils.next_date(
            curr_date=qutils.qdate_to_date(date),
            days=constants.PAY_PERIOD_DAYS - 1
        )
        self.q_pay_period.end_date_edit.setDate(qutils.date_to_qdate(end_date))

    @Slot()
    def _on_update(self):
        dialog = qutils.create_confirm_dialog(
            "Update pay period?",
            "You will permanently lose all employee data. Please make sure " + \
            "that any timesheet reports are saved before proceeding."
        )

        choice = dialog.exec()

        if choice == QMessageBox.Cancel:
            return

        pay_period = self._extract_pay_period()

        try:
            backend.update_pay_period(pay_period)
        except InternalError:
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.PAY_PERIOD_UPDATED.emit()

            dialog = qutils.create_info_dialog("Pay period updated.")
            dialog.exec()

    def _extract_pay_period(self) -> PayPeriod:
        start_date = self.q_pay_period.start_date_edit.date()
        end_date = self.q_pay_period.end_date_edit.date()

        return PayPeriod(
            start_date=qutils.qdate_to_date(start_date),
            end_date=qutils.qdate_to_date(end_date)
        )
