from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


class ThemeManager(QObject):
    """Manages application themes (light/dark)."""

    LIGHT_THEME = "light"
    DARK_THEME = "dark"

    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def get_light_stylesheet():
        """Get stylesheet for light theme."""
        return """
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #c0c0c0;
                padding: 4px;
                border-radius: 2px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #f0f0f0;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #2a82da;
                selection-color: #ffffff;
                border: 1px solid #c0c0c0;
            }
            QMenu {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #c0c0c0;
            }
            QMenu::item {
                background-color: transparent;
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #2a82da;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #c0c0c0;
                margin: 4px 0px;
            }
            QMenuBar {
                background-color: #f0f0f0;
                color: #000000;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #2a82da;
                color: #ffffff;
            }
        """

    @staticmethod
    def get_dark_stylesheet():
        """Get stylesheet for dark theme."""
        return """
            QComboBox {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                padding: 4px;
                border-radius: 2px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #454545;
            }
            QComboBox QAbstractItemView {
                background-color: #353535;
                color: #ffffff;
                selection-background-color: #2a82da;
                selection-color: #ffffff;
                border: 1px solid #5a5a5a;
            }
            QMenu {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #5a5a5a;
            }
            QMenu::item {
                background-color: transparent;
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #2a82da;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #5a5a5a;
                margin: 4px 0px;
            }
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #2a82da;
                color: #ffffff;
            }
        """

    @staticmethod
    def get_light_palette():
        """Get the light theme palette."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        return palette

    @staticmethod
    def get_dark_palette():
        """Get the dark theme palette."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        return palette

    @staticmethod
    def apply_theme(theme_name):
        """Apply the specified theme to the application."""
        app = QApplication.instance()
        if theme_name == ThemeManager.DARK_THEME:
            app.setPalette(ThemeManager.get_dark_palette())
            app.setStyleSheet(ThemeManager.get_dark_stylesheet())
        else:
            app.setPalette(ThemeManager.get_light_palette())
            app.setStyleSheet(ThemeManager.get_light_stylesheet())

    @staticmethod
    def apply_menu_theme(widget):
        """Apply theme to menus and menu bar."""
        app = QApplication.instance()
        palette = app.palette()
        
        try:
            widget.setPalette(palette)
        except RuntimeError:
            pass
        
        from PySide6.QtWidgets import QMenu
        
        def apply_to_menu(menu):
            try:
                menu.setPalette(palette)
                for action in menu.actions():
                    try:
                        action.setEnabled(action.isEnabled())
                        if hasattr(action, 'menu') and action.menu():
                            apply_to_menu(action.menu())
                    except RuntimeError:
                        pass
                for child in menu.children():
                    try:
                        if isinstance(child, QMenu):
                            apply_to_menu(child)
                        elif hasattr(child, 'setPalette'):
                            child.setPalette(palette)
                    except RuntimeError:
                        pass
            except RuntimeError:
                pass
        
        try:
            if hasattr(widget, 'findChildren'):
                for menu in widget.findChildren(QMenu):
                    apply_to_menu(menu)
            apply_to_menu(widget)
        except RuntimeError:
            pass
