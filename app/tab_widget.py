from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Slot
from pay_period_widget import PayPeriodWidget
from employees_widget import EmployeesWidget

class TabWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self._setup_window()

        tabs = QTabWidget(self)
        
        self.pay_period_widget = PayPeriodWidget()
        self.employees_widget = EmployeesWidget()
        self.pay_period_widget.save_date_signal.connect(self._on_save_update_table)

        # Download timesheet widget (TODO: make class)
        widget_download = QWidget()

        # Add tabs to widget
        tabs.addTab(self.pay_period_widget, "Pay Period")
        tabs.addTab(self.employees_widget, "Employees")
        tabs.addTab(widget_download, "Time Sheet")

        tabs.setStyleSheet("""
            QTabWidget::pane {
                border-top: 2px solid #C2C7CB;
                position: absolute;
                top: -0.5em;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #E0E5E9;
                color: #3D3D3D;
                min-width: 120px;
                padding: 8px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #3D3D3D;
                color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def _setup_window(self):
        self.setWindowTitle("TimeSheetGen")
        self.setGeometry(0, 0, 680, 480)

        # center the main window
        screen_geometry = QApplication.instance().primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())            

    @Slot()
    def _on_save_update_table(self):
        self.employees_widget.update_table()

