from PySide6.QtWidgets import QApplication
import sys
from tab_widget import TabWidget

# Create the application
app = QApplication(sys.argv)

widget = TabWidget()
widget.show()

# Run the event loop
app.exec()
