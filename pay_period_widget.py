from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QDateEdit, QPushButton, QGridLayout
from PySide6.QtCore import QDate, Qt

class PayPeriodWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()

        # Set up the label
        date_label = QLabel("Starting date")
        date_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Set up the date field
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setStyleSheet("QDateEdit{border: 2px solid #999999; padding: 8px; border-radius: 5px;}")
        date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        mini_v_layout = QVBoxLayout()
        mini_v_layout.addWidget(date_label)
        mini_v_layout.addWidget(date_edit)

        # Set up the button
        save_button = QPushButton("Save")
        save_button.setStyleSheet("""
        QPushButton {
          background-color: #4CAF50;
          border: none;
          color: white;
          padding: 10px 20px;
          text-align: center;
          margin: 4px 2px;
          border-radius: 5px;
        }

        QPushButton:hover {
            background-color: #3E8E41;
        }

        """)

        # Add elements to a grid layout
        grid_layout = QGridLayout()
        grid_layout.addLayout(mini_v_layout, 0, 0, 1, 3, alignment=Qt.AlignBottom)
        grid_layout.addWidget(save_button, 1, 2, alignment=Qt.AlignTop)

        # Set the layout
        self.setLayout(grid_layout)