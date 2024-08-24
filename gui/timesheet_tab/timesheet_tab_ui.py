from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QFileDialog
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon

from gui import gui_utils
from gui.employees_table import EmployeesTable
from gui.employee_profile import EmployeeProfile

import utils


class TimesheetTabUI(QWidget):
    pdf_filename_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self.table = EmployeesTable()

        self.download_pdf_btn = self._create_pdf_btn()
        self.delete_all_employees_btn = QPushButton("Delete All Employees")
        self.import_btn = QPushButton("Import Employees")
        self.add_employee_btn = QPushButton("Add Employee")

        self.download_pdf_btn.clicked.connect(self._handle_download_pdf)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()

        layout.addLayout(self._create_header_layout())
        layout.addWidget(self._create_filter())
        layout.addWidget(self.download_pdf_btn, alignment=Qt.AlignRight)
        layout.addWidget(self.table)
        layout.addLayout(self._create_bottom_btns_layout())

        self.setLayout(layout)

    def _create_header_layout(self) -> QVBoxLayout:
        title = QLabel("Timesheet")
        title.setStyleSheet("font-weight: bold; font-size: 24px")

        subtitle = QLabel(
            "Edit employee details and timesheet information here. " + \
            "Click an employee to open the editor."
        )

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(gui_utils.create_sunken_line())

        return layout

    def _create_filter(self) -> EmployeeProfile:
        filter_ = EmployeeProfile() # filter is a keyword
        filter_.setTitle("Filter")

        filter_.first_name_edit.textChanged.connect(self.table.filter_by_first_name)
        filter_.last_name_edit.textChanged.connect(self.table.filter_by_last_name)
        filter_.id_edit.textChanged.connect(self.table.filter_by_id)
        filter_.position_edit.textChanged.connect(self.table.filter_by_position)
        filter_.contract_edit.textChanged.connect(self.table.filter_by_contract)

        return filter_

    def _create_pdf_btn(self) -> QPushButton:
        btn = QPushButton("Download Timesheet")
        btn.setToolTip(
            "Generate the timesheet PDF for employees matching the current filter."
        )

        pdf_icon = QIcon(utils.load_file("assets/icons/arrow-down-solid.svg")) # TODO: constant
        pdf_icon_size = QSize(14, 14)

        btn.setIcon(pdf_icon)
        btn.setIconSize(pdf_icon_size)

        return btn

    def _create_bottom_btns_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addWidget(self.delete_all_employees_btn)
        layout.addItem(spacer)
        layout.addWidget(self.import_btn)
        layout.addWidget(self.add_employee_btn)

        return layout

    def _handle_download_pdf(self) -> None:
        file_path = self._open_file_saver()
        self.pdf_filename_selected.emit(file_path)

    def _open_file_saver(self) -> None:
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save PDF",
            dir=gui_utils.get_home_dir(),
            filter="Adobe Acrobat Document (*.pdf)"
        )

        file_path = response[0]

        return file_path
