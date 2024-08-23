import datetime
from enum import Enum, auto

from PySide6.QtWidgets import QMessageBox, QFrame
from PySide6.QtCore import QDate, QTime


class DialogType(Enum):
    INFO = auto()
    WARN = auto()
    ERR = auto()
    CONFIRM = auto()


def date_to_qdate(date: datetime.date) -> QDate:
    return QDate(date.year, date.month, date.day)

def time_to_qtime(time: datetime.time) -> QTime:
    return QTime(time.hour, time.minute)

def qdate_to_date(qdate: QDate) -> datetime.date:
    return datetime.date(year=qdate.year(), month=qdate.month(), day=qdate.day())

def qtime_to_time(qtime: QTime) -> datetime.time:
    return datetime.time(hour=qtime.hour(), minute=qtime.minute())

def is_text_empty(text: str) -> bool:
    return text.strip() == ""

def create_sunken_line() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)

    return line

def show_dialog(
    dialog_type: DialogType,
    title: str,
    text: str = "",
    buttons: list[tuple[str, QMessageBox.ButtonRole]] = None
) -> int:
    """
    Creates and displays a customizable dialog box.

    :param dialog_type: 
        The type of dialog to display. It determines the icon and default
        buttons. Options include:

        - INFO: Shows an information dialog with an "Information" icon 
          and an "Ok" button by default.
        - WARNING: Shows a warning dialog with a "Warning" icon and an "Ok" 
          button by default.
        - ERROR: Shows an error dialog with a "Critical" icon and an "Ok" 
          button by default.
        - CONFIRM: Shows a confirmation dialog with a "Question" icon and 
          "Yes" and "Cancel" buttons by default.

    :param title: 
        The bolded text of the dialog.

    :param text: 
        Optional. Informative text.

    :param buttons: 
        Optional. A list of tuples where each inner tuple contains a button 
        label (str) and its associated `QMessageBox.ButtonRole`. If provided, 
        these buttons will replace the default buttons for the given 
        `dialog_type`.

        Example::
        
            buttons = [
                ('Ok', QMessageBox.AcceptRole),
                ('Settings', QMessageBox.ActionRole)
            ]

    :return: 
        An integer value representing the button that was clicked by the user. 
    """

    dialog = QMessageBox()
    dialog.setText(title)
    dialog.setInformativeText(text)

    if dialog_type == DialogType.INFO:
        dialog.setIcon(QMessageBox.Information)
    elif dialog_type == DialogType.WARN:
        dialog.setIcon(QMessageBox.Warning)
    elif dialog_type == DialogType.ERR:
        dialog.setIcon(QMessageBox.Critical)
    elif dialog_type == DialogType.CONFIRM:
        dialog.setIcon(QMessageBox.Question)

    if buttons:
        for button_text, role in buttons.items():
            dialog.addButton(button_text, role)
    else:
        if dialog_type == DialogType.INFO:
            dialog.setStandardButtons(QMessageBox.Ok)
        elif dialog_type == DialogType.WARN:
            dialog.setStandardButtons(QMessageBox.Ok)
        elif dialog_type == DialogType.ERR:
            dialog.setStandardButtons(QMessageBox.Ok)
        elif dialog_type == DialogType.CONFIRM:
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

    return dialog.exec()
