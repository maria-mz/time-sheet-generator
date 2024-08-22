from datetime import datetime

from PySide6.QtWidgets import QLabel, QLineEdit

from db.db_data import Shift
from gui.gui_data import ShiftText

import validation


HOURS_ERR_TOOLTIP = "Please enter a number with up to 2 digits " + \
                    "before and after the decimal point. (e.g., 7.25)"
TIME_ERR_TOOLTIP = "Please enter the time in HH:MM AM/PM format (e.g., 09:30 AM)."

ERR_STYLE = "border: 1px solid orange; background-color: gold"

DATE_FORMAT = "%b %d"
TIME_FORMAT = "%I:%M %p"


class TimesheetShift:
    def __init__(self, shift: Shift) -> None:
        self.date = shift.date
        self.date_label = self._create_date_label(shift.date)
        self.time_in_edit = self._create_time_edit(shift.time_in)
        self.time_out_edit = self._create_time_edit(shift.time_out)
        self.hours_reg_edit = self._create_hours_edit(shift.hours_reg)
        self.hours_ot_edit = self._create_hours_edit(shift.hours_ot)

    def _create_date_label(self, date: datetime.date) -> QLabel:
        date_label = QLabel(date.strftime(DATE_FORMAT))
        date_label.setContentsMargins(0, 0, 8, 0)

        return date_label

    def _create_time_edit(self, time: str) -> QLineEdit:
        edit = QLineEdit(time.strftime(TIME_FORMAT))

        edit.editingFinished.connect(lambda: self._handle_time_input(edit))
        edit.textChanged.connect(lambda: self._clear_error_outline(edit))

        return edit

    def _create_hours_edit(self, hours: str) -> QLineEdit:
        edit = QLineEdit(hours)

        edit.editingFinished.connect(lambda: self._handle_hours_input(edit))
        edit.textChanged.connect(lambda: self._clear_error_outline(edit))

        return edit

    def _handle_hours_input(self, edit: QLineEdit) -> None:
        """
        Handles input for hours. This should be called when editing is finished.
        """
        self._strip(edit)

        if validation.validate_hours(edit.text()):
            edit.setToolTip("")
            self._format_hours(edit)
            self._clear_error_outline(edit)
        else:
            edit.setToolTip(HOURS_ERR_TOOLTIP)
            self._put_error_outline(edit)

    def _handle_time_input(self, edit: QLineEdit) -> None:
        """
        Handles input for time. This should be called when editing is finished.
        """
        self._strip(edit)

        if validation.validate_time(edit.text()):
            edit.setToolTip("")
            self._clear_error_outline(edit)
        else:
            edit.setToolTip(TIME_ERR_TOOLTIP)
            self._put_error_outline(edit)

    def _format_hours(self, edit: QLineEdit) -> None:
        """
        Formats hours. For example, if the hours is "5", the value after
        formatting will be "5.00".
        """
        hours = edit.text()

        if hours in {"", "."}:
            edit.setText("0.00")
        else:
            edit.setText("{:.2f}".format(float(hours)))

    def _strip(self, edit: QLineEdit) -> None:
        edit.setText(edit.text().strip())

    def _put_error_outline(self, edit: QLineEdit) -> None:
        edit.setStyleSheet(ERR_STYLE)

    def _clear_error_outline(self, edit: QLineEdit) -> None:
        edit.setStyleSheet("")

    def _handle_input(self) -> None:
        """
        Handle input for current field values. Normally, inputs are handled
        after editing is finished, but if the user saves while editing, it
        may not trigger the signal in time.
        """
        self._handle_time_input(self.time_in_edit)
        self._handle_time_input(self.time_out_edit)
        self._handle_hours_input(self.hours_reg_edit)
        self._handle_hours_input(self.hours_ot_edit)

    @property
    def shift(self) -> ShiftText:
        self._handle_input() # TODO: Not sure how to go about this...

        return ShiftText(
            date=self.date,
            time_in=self.time_in_edit.text(),
            time_out=self.time_out_edit.text(),
            hours_reg=self.hours_reg_edit.text(),
            hours_ot=self.hours_ot_edit.text()
        )
