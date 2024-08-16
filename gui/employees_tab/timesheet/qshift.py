"""
Component of TimesheetEditor. Represents a single shift's UI components.
"""
import re
from datetime import datetime
from typing import Union, Callable
from PySide6.QtWidgets import QLabel, QLineEdit

import constants
from db.db_data import Shift


class QShift:
    """
    Represents a single shift's UI components.

    Supports:
        - Checking if any changes were made.
        - Validation.
        - Formatting.
        - Outlining invalid fields.

    """

    HOURS_REGEX = re.compile(r'^\d{0,2}(\.\d{0,2})?$')
    TIME_REGEX = re.compile(r'^$|^(0[1-9]|1[0-2]):([0-5][0-9])\s(AM|PM)$')

    def __init__(self, shift: Shift) -> None:
        self._og_shift = shift

        self.date = shift.date
        self.date_label = self._create_date_label(shift.date)
        self.time_in_edit = self._create_time_edit(shift.time_in)
        self.time_out_edit = self._create_time_edit(shift.time_out)
        self.hours_reg_edit = self._create_hours_edit(shift.hours_reg)
        self.hours_ot_edit = self._create_hours_edit(shift.hours_ot)

    def _create_date_label(self, date: datetime.date) -> QLabel:
        date_label = QLabel(date.strftime(constants.DATE_FORMAT))
        date_label.setContentsMargins(0, 0, 24, 0)
        return date_label

    def _create_time_edit(self, time: Union[datetime.time, None]) -> QLineEdit:
        if time is None:
            edit = QLineEdit("")
        else:
            edit = QLineEdit(time.strftime("%I:%M %p"))

        edit_callback = self._edit_finished_callback(
            edit=edit,
            validator=self._validate_time_edit
        )

        edit.editingFinished.connect(edit_callback)
        edit.textChanged.connect(lambda _: self._clear_outline(edit))

        return edit

    def _create_hours_edit(self, hours: str) -> QLineEdit:
        edit = QLineEdit(hours)

        edit_callback = self._edit_finished_callback(
            edit=edit,
            validator=self._validate_hours_edit,
            formatter=self._format_hours_edit
        )

        edit.editingFinished.connect(edit_callback)
        edit.textChanged.connect(lambda _: self._clear_outline(edit))

        return edit

    def _edit_finished_callback(
        self, edit: QLineEdit, validator: Callable, formatter: Callable = None
    ) -> Callable:
        def callback():
            self._strip_edit(edit)

            if validator(edit):
                if formatter:
                    formatter(edit)
                self._clear_outline(edit)
            else:
                self._outline_edit(edit)

        return callback

    def _format_hours_edit(self, edit: QLineEdit) -> None:
        hours = edit.text()
        formatted_hours = "0.00" if hours in {"", "."} else "{:.2f}".format(float(hours))
        edit.setText(formatted_hours)

    def _strip_edit(self, edit: QLineEdit) -> None:
        edit.setText(edit.text().strip())

    def to_shift(self) -> Shift:
        return Shift(
            date=self.date,
            time_in=self._get_time(self.time_in_edit),
            time_out=self._get_time(self.time_out_edit),
            hours_reg=self._get_hours(self.hours_reg_edit),
            hours_ot=self._get_hours(self.hours_ot_edit)
        )

    def _get_time(self, time_edit: QLineEdit) -> Union[datetime.time, None]:
        text = time_edit.text().strip()

        if text == "":
            return None

        return datetime.strptime(text, "%I:%M %p").time()

    def _get_hours(self, hours_edit: QLineEdit) -> str:
        return hours_edit.text().strip()

    def made_changes(self) -> bool:
        return self._og_shift != self.to_shift()

    def _validate_time_edit(self, time_edit: QLineEdit) -> bool:
        return bool(re.match(self.TIME_REGEX, time_edit.text()))

    def _validate_hours_edit(self, hours_edit: QLineEdit) -> bool:
        return bool(re.match(self.HOURS_REGEX, hours_edit.text()))

    def is_valid(self) -> bool:
        return (
            self._validate_time_edit(self.time_in_edit) and 
            self._validate_time_edit(self.time_out_edit) and
            self._validate_hours_edit(self.hours_reg_edit) and
            self._validate_hours_edit(self.hours_ot_edit)
        )

    def outline_invalid_edits(self) -> None:
        if not self._validate_time_edit(self.time_in_edit):
            self._outline_edit(self.time_in_edit)

        if not self._validate_time_edit(self.time_out_edit):
            self._outline_edit(self.time_out_edit)

        if not self._validate_hours_edit(self.hours_reg_edit):
            self._outline_edit(self.hours_reg_edit)
        
        if not self._validate_hours_edit(self.hours_ot_edit):
            self._outline_edit(self.hours_ot_edit)

    def _outline_edit(self, edit: QLineEdit) -> None:
        edit.setStyleSheet("border: 1px solid red; background: pink")

    def _clear_outline(self, edit: QLineEdit) -> None:
        edit.setStyleSheet("")
