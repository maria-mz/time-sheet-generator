import sys
import logging
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


logging.basicConfig(
    format=" %(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
)

logging.getLogger().setLevel(logging.INFO)


app = QApplication(sys.argv)

main_window = MainWindow()
main_window.show()

# Run the event loop
app.exec()
