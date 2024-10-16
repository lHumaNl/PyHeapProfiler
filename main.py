import sys
import logging
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    """
    Entry point for the application.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting application")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
