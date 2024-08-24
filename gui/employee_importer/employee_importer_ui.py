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

from gui import gui_utils
from gui.employees_table import EmployeesTable

from db.db_data import Employee


class EmployeeImporterUI(QWidget):
    file_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self._filename_label = QLabel("No file chosen")

        self._preview_table = EmployeesTable()
        self._preview_table.setCursor(QCursor(Qt.ForbiddenCursor))
        self._preview_table.setSelectionMode(QAbstractItemView.NoSelection)

        self.import_employees_btn = QPushButton("Import Employees")
        self.import_employees_btn.setEnabled(False)
        self.cancel_btn = QPushButton("Cancel")

        self._init_ui()

    def _init_ui(self) -> None:
        file_label = QLabel("File")
        file_label.setStyleSheet("font-weight: bold; font-size: 16px")

        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("font-weight: bold; font-size: 16px")

        layout = QVBoxLayout()

        layout.addWidget(file_label)
        layout.addWidget(self._create_instructions())
        layout.addWidget(self._create_file_box())
        layout.addWidget(preview_label)
        layout.addWidget(self._preview_table)
        layout.addLayout(self._create_btns_layout())

        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

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

    def _create_file_box(self) -> QGroupBox:
        box = QGroupBox()

        choose_file_btn = QPushButton("Choose File")
        choose_file_btn.clicked.connect(self._handle_choose_file)

        layout = QHBoxLayout()

        layout.addWidget(choose_file_btn)
        layout.addWidget(self._filename_label)
        layout.setAlignment(Qt.AlignLeft)

        box.setLayout(layout)

        return box

    def _create_btns_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.import_employees_btn)
        layout.setAlignment(Qt.AlignRight)

        return layout

    def _handle_choose_file(self) -> None:
        file_path = self._open_file_picker_window()
        self.file_selected.emit(file_path)

    def _open_file_picker_window(self) -> str:
        file_filter = "Data File (*.csv)"

        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a file",
            dir=gui_utils.get_current_dir(),
            filter=file_filter
        )

        file_path = response[0]

        return file_path

    def set_filename(self, text: str, style: str = "") -> None:
        self._filename_label.setText(text)
        self._filename_label.setStyleSheet(style)

    def populate_table(self, employees: list[Employee]) -> None:
        self._preview_table.populate_table(employees)
