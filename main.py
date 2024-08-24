import sys
import logging
from PySide6.QtWidgets import QApplication

import constants
from db.db_handler import DatabaseHandler
from backend.backend import Backend
from gui.main_window import MainWindow


logging.basicConfig(
    format=" %(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
)

logging.getLogger().setLevel(logging.INFO)


_logger = logging.getLogger(__name__)


if __name__ == "__main__":
    db_handler = DatabaseHandler(constants.DB_PATH)

    try:
        backend = Backend(db_handler)
    except Exception as e:
        _logger.exception("failed to initialize backend. terminating program")
        sys.exit(1)

    app = QApplication(sys.argv)

    main_window = MainWindow(backend)
    main_window.show()

    # Run the event loop
    app.exec()

    backend.shutdown()
