from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QDateEdit,
    QPushButton,
    QSizePolicy,
    QGroupBox,
)
from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtGui import QFont

from gui import gui_utils

from db.db_data import PayPeriod
import utils
import constants


class SettingsTabUI(QWidget):
    def __init__(self, pay_period: PayPeriod):
        super().__init__()

        self.update_btn = QPushButton("Update")
        self._start_date_edit = self._create_date_edit(pay_period.start_date)
        self._end_date_edit =  self._create_date_edit(pay_period.end_date)
        self._end_date_edit.setEnabled(False)

        self._start_date_edit.userDateChanged.connect(self._on_start_date_changed)

        self._init_ui()

    def _set_date(self, date_edit: QDateEdit, date: datetime.date) -> None:
        date_edit.setDate(gui_utils.date_to_qdate(date))

    def _create_date_edit(self, date: datetime.date) -> QDateEdit:
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setFixedWidth(200)
        self._set_date(edit, date)

        return edit

    def _init_ui(self) -> None:
        layout = QVBoxLayout()

        title = QLabel("Settings")
        title.setStyleSheet(f"font-weight: {QFont.Weight.Bold}; font-size: 24px")
        subtitle = QLabel("Update the pay period here and view the default timesheet values.")

        layout.addWidget(title, alignment=Qt.AlignLeft)
        layout.addWidget(subtitle, alignment=Qt.AlignLeft)
        layout.addWidget(gui_utils.create_sunken_line())
        layout.addLayout(self._create_boxes_layout())
        layout.addWidget(self.update_btn, alignment=Qt.AlignRight)

        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def _create_boxes_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(32)
        layout.addWidget(self._create_default_values_box())
        layout.addWidget(self._create_pay_period_box())

        return layout

    def _create_default_values_box(self) -> QGroupBox:
        box = QGroupBox("Default Values")

        grid = QGridLayout()
        grid.setSpacing(16)

        rows = [
            ("Default time in", constants.DEFAULT_TIME_IN.strftime("%I:%M %p")),
            ("Default time out", constants.DEFAULT_TIME_OUT.strftime("%I:%M %p")),
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
        grid.addWidget(self._start_date_edit, 0, 1, Qt.AlignRight)
        grid.addWidget(end_date_label, 1, 0)
        grid.addWidget(self._end_date_edit, 1, 1, Qt.AlignRight)

        box.setLayout(grid)

        return box

    def _create_settings_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"font-weight: {QFont.Weight.Medium};")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return label

    @Slot(QDate)
    def _on_start_date_changed(self, date: QDate):
        end_date = utils.next_date(
            gui_utils.qdate_to_date(date), constants.PAY_PERIOD_DAYS - 1
        )
        self._end_date_edit.setDate(gui_utils.date_to_qdate(end_date))

    @property
    def pay_period(self) -> PayPeriod:
        return PayPeriod(
            start_date=gui_utils.qdate_to_date(self._start_date_edit.date()),
            end_date=gui_utils.qdate_to_date(self._end_date_edit.date())
        )

    def update_pay_period(self, pay_period: PayPeriod):
        self._set_date(self._start_date_edit, pay_period.start_date)
        self._set_date(self._end_date_edit, pay_period.end_date)
