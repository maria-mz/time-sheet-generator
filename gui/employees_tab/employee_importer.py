import os
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QAbstractItemView,
    QPushButton,
    QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

import gui.constants
from gui import qutils
from gui.employees_tab.employees_table import EmployeesTable

from backend.backend import backend
from backend.errors import CSVReadError, InternalError
from db.db_handler import EmployeeAlreadyExistsError


class EmployeeImporter(QWidget):
    EMPLOYEES_UPDATED = Signal()
    DONE = Signal()

    def __init__(self):
        super().__init__()

        self.employees = []
        self.filename_label = QLabel("No file chosen")

        self.preview_table = EmployeesTable()
        self.preview_table.setCursor(QCursor(Qt.ForbiddenCursor))
        self.preview_table.setSelectionMode(QAbstractItemView.NoSelection)

        self.import_btn = QPushButton("Import Employees")
        self.import_btn.clicked.connect(self._on_import)
        self.import_btn.setEnabled(False)

        layout = self._create_layout()

        self.setLayout(layout)

    def _create_layout(self) -> QVBoxLayout:
        import_csv_label = QLabel("File")
        import_csv_label.setStyleSheet("font-weight: bold; font-size: 16px")

        instr = self._create_instructions()

        file_chooser = self._create_file_chooser()

        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("font-weight: bold; font-size: 16px")

        bottom_buttons_row = self._create_bottom_buttons_row()

        layout = QVBoxLayout()

        layout.addWidget(import_csv_label)
        layout.addWidget(instr)
        layout.addWidget(file_chooser)
        layout.addWidget(preview_label)
        layout.addWidget(self.preview_table)
        layout.addLayout(bottom_buttons_row)

        layout.setAlignment(Qt.AlignTop)

        return layout

    def _create_instructions(self) -> QLabel:
        instr = QLabel()
        instr.setText(
            "Import employees from a .csv file. <b>The first row of the " + \
            "file must be the header row</b>. The header column names " + \
            "should include the following:" + \
            "<ul>" + \
            "<li>First Name</li>" + \
            "<li>Last Name</li>" + \
            "<li>Employee No</li>" + \
            "<li>Job Title</li>" + \
            "<li>Contract</li>" + \
            "</ul>" + \
            "The timesheet information will be populated automatically " + \
            "with the default values."
        )
        instr.setTextFormat(Qt.TextFormat.RichText)
        instr.setWordWrap(True)

        return instr

    def _create_file_chooser(self) -> QGroupBox:
        box = QGroupBox()

        choose_file_btn = QPushButton("Choose File")
        choose_file_btn.clicked.connect(self._on_choose_file)

        layout = QHBoxLayout()

        layout.addWidget(choose_file_btn)
        layout.addWidget(self.filename_label)
        layout.setAlignment(Qt.AlignLeft)

        box.setLayout(layout)

        return box

    def _create_bottom_buttons_row(self) -> QHBoxLayout:
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)

        layout = QHBoxLayout()

        layout.addWidget(cancel_btn)
        layout.addWidget(self.import_btn)
        layout.setAlignment(Qt.AlignRight)

        return layout

    def _on_choose_file(self) -> None:
        file_path = self._open_file_picker_window()

        if not file_path: # This may happen if the user exits out of the window.
            return

        # Empty the preview table to take in the new employees.
        # If there is an issue with the read, the preview table will stay empty,
        # which is intended.
        self.preview_table.populate_table([])
        # Disable the import button until it's certain there are employees
        # that can be imported
        self.import_btn.setEnabled(False)

        self.filename_label.setText(file_path)

        try:
            self.employees = backend.generate_employees_from_csv(file_path)

        except CSVReadError as e:
            self.filename_label.setStyleSheet("color: red;")
            dialog = qutils.create_error_dialog("Read failed.", str(e))
            dialog.exec()

        except InternalError as e:
            self.filename_label.setStyleSheet("color: red;")
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()

        else:
            if len(self.employees) > 0:
                self.import_btn.setEnabled(True)
                self.preview_table.populate_table(self.employees)

            self.filename_label.setStyleSheet("color: green;")
            dialog = qutils.create_info_dialog("Read successful.")
            dialog.exec()

    def _open_file_picker_window(self) -> str:
        file_filter = "Data File (*.csv)"

        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a file",
            # dir=os.path.expanduser("~"), # uncomment when creating the .exe, gives home dir
            dir=os.getcwd(),
            filter=file_filter
        )

        file_path = response[0]

        return file_path

    def _on_import(self) -> None:
        try:
            backend.add_employees(self.employees)
        except EmployeeAlreadyExistsError as e:
            dialog = qutils.create_error_dialog("Import failed.", str(e))
            dialog.exec()
        except InternalError:
            dialog = qutils.create_error_dialog(gui.constants.INTERNAL_ERR_MSG)
            dialog.exec()
        else:
            self.EMPLOYEES_UPDATED.emit()

            dialog = qutils.create_info_dialog("Employees imported successfully.")

            dialog.exec()
            self.DONE.emit()

    def _on_cancel(self) -> None:
        self.DONE.emit()
