import sys
import logging
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from utils.settings_manager import SettingsManager
from utils.theme_manager import ThemeManager


def main():
    """
    Entry point for the application.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting application")

    app = QApplication(sys.argv)

    settings_manager = SettingsManager()
    saved_theme = settings_manager.load_theme()
    ThemeManager.apply_theme(saved_theme)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

