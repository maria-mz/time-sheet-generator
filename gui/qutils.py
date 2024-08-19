import datetime
from PySide6.QtWidgets import QMessageBox
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

def create_error_dialog(title: str, text: str = "") -> QMessageBox:
    dialog = QMessageBox()
    dialog.setText(title)
    dialog.setInformativeText(text)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.setIcon(QMessageBox.Critical)

    return dialog

def create_warning_dialog(title: str, text: str = "") -> QMessageBox:
    dialog = QMessageBox()
    dialog.setText(title)
    dialog.setInformativeText(text)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.setIcon(QMessageBox.Warning)

    return dialog

def create_info_dialog(title: str, text: str = "") -> QMessageBox:
    dialog = QMessageBox()
    dialog.setText(title)
    dialog.setInformativeText(text)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.setIcon(QMessageBox.Information)

    return dialog

def create_confirm_dialog(title: str, text: str = "") -> QMessageBox:
    dialog = QMessageBox()
    dialog.setText(title)
    dialog.setInformativeText(text)
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    dialog.setIcon(QMessageBox.Warning)

    return dialog
