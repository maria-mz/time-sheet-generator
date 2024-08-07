from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QDateEdit,
    QPushButton,
    QMessageBox,
    QSizePolicy,
    QGroupBox,
    QFrame
)
from PySide6.QtCore import QDate, Qt, Signal, Slot
from PySide6.QtGui import QFont

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

    def __init__(self, pay_period: PayPeriod):
        super().__init__()

        self.q_pay_period = self._create_q_pay_period(pay_period)

        layout = self._create_main_layout()

        self.setLayout(layout)

    def _create_main_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        title = QLabel("Settings")
        title.setStyleSheet(f"font-weight: {QFont.Weight.Bold}; font-size: 24px")
        subtitle = QLabel("Update the pay period here and view the default timesheet values.")

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        boxes_layout = self._create_boxes_layout()

        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._on_update)

        layout.addWidget(title, alignment=Qt.AlignLeft)
        layout.addWidget(subtitle, alignment=Qt.AlignLeft)
        layout.addWidget(line)
        layout.addLayout(boxes_layout)
        layout.addWidget(update_btn, alignment=Qt.AlignRight)

        layout.setAlignment(Qt.AlignTop)

        return layout

    def _create_boxes_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(32)

        default_values_box = self._create_default_values_box()
        pay_period_box = self._create_pay_period_box()

        layout.addWidget(default_values_box)
        layout.addWidget(pay_period_box)

        return layout

    def _create_default_values_box(self) -> QGroupBox:
        box = QGroupBox("Default Values")

        grid = QGridLayout()
        grid.setSpacing(16)

        rows = [
            ("Default time in", constants.DEFAULT_TIME_IN.strftime("%I:%M %p")),
            ("Default time out", constants.DEFAULT_TIME_IN.strftime("%I:%M %p")),
            ("Default regular hours", constants.DEFAULT_HOURS_REG),
            ("Default overtime hours", constants.DEFAULT_HOURS_OT)
        ]

        for i, row in enumerate(rows):
            field, value = row
            grid.addWidget(self._create_settings_field_label(field), i, 0)
            grid.addWidget(QLabel(value), i, 1, Qt.AlignRight)

        box.setLayout(grid)

        return box

    def _create_pay_period_box(self) -> QGroupBox:
        box = QGroupBox(f"Pay Period ({constants.PAY_PERIOD_DAYS} days)")

        grid = QGridLayout()

        start_date_label = self._create_settings_field_label("Start date")
        end_date_label = self._create_settings_field_label("End date")

        grid.addWidget(start_date_label, 0, 0)
        grid.addWidget(self.q_pay_period.start_date_edit, 0, 1, Qt.AlignRight)
        grid.addWidget(end_date_label, 1, 0)
        grid.addWidget(self.q_pay_period.end_date_edit, 1, 1, Qt.AlignRight)

        box.setLayout(grid)

        return box

    def _create_settings_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return label

    def _create_q_pay_period(self, pay_period: PayPeriod) -> QPayPeriod:
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setFixedWidth(200)
        start_date_edit.setDate(qutils.date_to_qdate(pay_period.start_date))
        start_date_edit.userDateChanged.connect(self._on_start_date_changed)

        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setFixedWidth(200)
        end_date_edit.setEnabled(False)
        end_date_edit.setDate(qutils.date_to_qdate(pay_period.end_date))

        return QPayPeriod(
            start_date_edit=start_date_edit, end_date_edit=end_date_edit
        )

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
