import os
import platform
import subprocess
import datetime
from enum import Enum, auto
from typing import Protocol

from PySide6.QtWidgets import QWidget, QMessageBox, QFrame, QVBoxLayout
from PySide6.QtCore import QDate, QTime


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


class DialogType(Enum):
    INFO = auto()
    WARN = auto()
    ERR = auto()
    CONFIRM = auto()

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
        for button_text, role in buttons:
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


class Window(Protocol):
    def show(self) -> None:
        ...
    
    def close(self) -> None:
        ...

def create_window(
    title: str,
    widget: QWidget,
    w: int = None,
    h: int = None
) -> Window:
    """
    Creates a window that can be opened and closed.

    :param title: The window's title.
    :param widget: The widget to display in the window.
    :param w: Optional minimum width of the window.
    :param h: Optional minimum height of the window.

    :return: A `Window`.
    """
    window = QWidget()

    if w and h:
        window.setMinimumWidth(w)
        window.setMinimumHeight(h)

    layout = QVBoxLayout()
    layout.addWidget(widget)

    window.setWindowTitle(title)
    window.setLayout(layout)

    return window


def get_current_dir() -> str:
    return os.getcwd()


def get_home_dir() -> str:
    return os.path.expanduser("~")


def show_file_gui(file_path: str) -> None:
    os_name = platform.system()

    if os_name == 'Windows':
        args = ['explorer', '/select,', file_path]
    elif os_name == 'Darwin':
        args = ['open', '-R', file_path]
    elif os_name == 'Linux':
        args = (['xdg-open', file_path])
    else:
        raise ValueError(f"unsupported os name: {os_name}")

    subprocess.run(args)
