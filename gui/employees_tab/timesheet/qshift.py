"""
Component of TimesheetEditor. Represents a single shift's UI components.
"""
import re
from datetime import datetime
from typing import Union

from PySide6.QtWidgets import QLabel, QLineEdit

from db.db_data import Shift


HOURS_REGEX = re.compile(r'^\d{0,2}(\.\d{0,2})?$')
TIME_REGEX = re.compile(r'^$|^(0[1-9]|1[0-2]):([0-5][0-9])\s(AM|PM)$')

HOURS_ERR_TOOLTIP = "Please enter a number with up to 2 digits " + \
                    "before and after the decimal point. (e.g., 7.25)"
TIME_ERR_TOOLTIP = "Please enter the time in HH:MM AM/PM format (e.g., 09:30 AM)."

DATE_FORMAT = "%b %d"
TIME_FORMAT = "%I:%M %p"

ERR_STYLE = "border: 1px solid orange; background-color: gold"


class QShift:
    """
    Represents a single shift's UI components.
    """

    def __init__(self, shift: Shift) -> None:
        """
        Initializes a QShift with the details from the provided Shift.
        """
        self.date = shift.date
        self.date_label = self._create_date_label(shift.date)
        self.time_in_edit = self._create_time_edit(shift.time_in)
        self.time_out_edit = self._create_time_edit(shift.time_out)
        self.hours_reg_edit = self._create_hours_edit(shift.hours_reg)
        self.hours_ot_edit = self._create_hours_edit(shift.hours_ot)

    def _create_date_label(self, date: datetime.date) -> QLabel:
        """
        Creates a QLabel for displaying the shift date.
        """
        date_label = QLabel(date.strftime(DATE_FORMAT))
        date_label.setContentsMargins(0, 0, 8, 0)

        return date_label

    def _create_time_edit(self, time: Union[datetime.time, None]) -> QLineEdit:
        """
        Creates a QLineEdit for editing a shift's time.
        """
        if time is None:
            edit = QLineEdit("")
        else:
            edit = QLineEdit(time.strftime(TIME_FORMAT))

        edit.editingFinished.connect(lambda: self._handle_time_input(edit))
        edit.textChanged.connect(lambda: self._clear_error_outline(edit))

        return edit

    def _create_hours_edit(self, hours: str) -> QLineEdit:
        """
        Creates a QLineEdit for editing a shift's hours.
        """
        edit = QLineEdit(hours)

        edit.editingFinished.connect(lambda: self._handle_hours_input(edit))
        edit.textChanged.connect(lambda: self._clear_error_outline(edit))

        return edit

    def _handle_hours_input(self, edit: QLineEdit) -> None:
        """
        Handles input for hours. This should be called when editing is finished.
        """
        self._strip(edit)

        if self._validate_hours(edit):
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

        if self._validate_time(edit):
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
        """
        Removes leading and trailing whitespace from the QLineEdit text.
        """
        edit.setText(edit.text().strip())

    def _extract_time(self, time_edit: QLineEdit) -> Union[datetime.time, None]:
        """
        Gets the time from a QLineEdit as expected by Shift. Raises ValueError
        if the time value is invalid.
        """
        if not self._validate_time(time_edit):
            raise ValueError("cannot convert time; time value is invalid")

        text = time_edit.text()

        if text == "":
            return None

        return datetime.strptime(text, TIME_FORMAT).time()

    def _extract_hours(self, hours_edit: QLineEdit) -> str:
        """
        Gets the hours from a QLineEdit as expected by Shift. Raises ValueError
        if the time value is invalid.
        """
        if not self._validate_hours(hours_edit):
            raise ValueError("cannot convert hours; hours value is invalid")

        return hours_edit.text()

    def _validate_time(self, time_edit: QLineEdit) -> bool:
        """
        Validates a time value.
        """
        return bool(re.match(TIME_REGEX, time_edit.text()))

    def _validate_hours(self, hours_edit: QLineEdit) -> bool:
        """
        Validates an hours value.
        """
        return bool(re.match(HOURS_REGEX, hours_edit.text()))

    def _put_error_outline(self, edit: QLineEdit) -> None:
        """
        Applies an outline style to indicate an error in the QLineEdit.
        """
        edit.setStyleSheet(ERR_STYLE)

    def _clear_error_outline(self, edit: QLineEdit) -> None:
        """
        Clears the error outline style from the QLineEdit.
        """
        edit.setStyleSheet("")

    def is_valid(self) -> bool:
        """
        Checks if all values in the shift are valid.

        :return: True if all values are valid, otherwise False.
        """
        return (
            self._validate_time(self.time_in_edit) and 
            self._validate_time(self.time_out_edit) and
            self._validate_hours(self.hours_reg_edit) and
            self._validate_hours(self.hours_ot_edit)
        )

    def to_shift(self) -> Shift:
        """
        Converts the shift details in the UI to a Shift object. Raises a
        ValueError if a field value is currently invalid.
        """
        return Shift(
            date=self.date,
            time_in=self._extract_time(self.time_in_edit),
            time_out=self._extract_time(self.time_out_edit),
            hours_reg=self._extract_hours(self.hours_reg_edit),
            hours_ot=self._extract_hours(self.hours_ot_edit)
        )

    def handle_input(self) -> None:
        """
        Handle input for current field values. Normally, inputs are handled
        after editing is finished, but if the user saves while editing, it
        may not trigger the signal in time. Call this method before saving
        the shift.
        """
        self._handle_time_input(self.time_in_edit)
        self._handle_time_input(self.time_out_edit)
        self._handle_hours_input(self.hours_reg_edit)
        self._handle_hours_input(self.hours_ot_edit)
