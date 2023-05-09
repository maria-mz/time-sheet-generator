from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout
from pay_period_widget import PayPeriodWidget

class TabWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TimeSheetGen")

        tab_widget = QTabWidget(self)
        
        pay_period_widget = PayPeriodWidget()

        # Databse widget (TODO: make class)
        widget_database = QWidget()

        # Download timesheet widget (TODO: make class)
        widget_download = QWidget()

        # Add tabs to widget
        tab_widget.addTab(pay_period_widget, "Pay Period")
        tab_widget.addTab(widget_database, "Employees")
        tab_widget.addTab(widget_download, "Time Sheet")

        tab_widget.setStyleSheet("""
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
        layout.addWidget(tab_widget)

        self.setLayout(layout)

