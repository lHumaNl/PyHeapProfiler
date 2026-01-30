from PySide6.QtCore import QSettings


class SettingsManager:
    """Manages application settings persistence."""

    ORG_NAME = "PyHeapProfiler"
    APP_NAME = "Heap Dump Analyzer"

    def __init__(self):
        self.settings = QSettings(self.ORG_NAME, self.APP_NAME)

    def save_window_geometry(self, window):
        """Save window geometry and state."""
        self.settings.setValue("window_geometry", window.saveGeometry())
        self.settings.setValue("window_state", window.saveState())

    def load_window_geometry(self, window):
        """Load window geometry and state."""
        geometry = self.settings.value("window_geometry")
        state = self.settings.value("window_state")
        if geometry:
            window.restoreGeometry(geometry)
        if state:
            window.restoreState(state)

    def save_theme(self, theme_name):
        """Save the current theme."""
        self.settings.setValue("theme", theme_name)

    def load_theme(self):
        """Load the saved theme, defaults to light."""
        return self.settings.value("theme", "light", type=str)

    def save_column_visibility(self, hidden_columns):
        """Save column visibility settings."""
        self.settings.setValue("column_visibility", hidden_columns)

    def load_column_visibility(self):
        """Load column visibility settings."""
        return self.settings.value("column_visibility", [], type=list)

    def save_column_order(self, column_order):
        """Save column order settings."""
        self.settings.setValue("column_order", column_order)

    def load_column_order(self):
        """Load column order settings."""
        return self.settings.value("column_order", [], type=list)

    def save_column_widths(self, column_widths):
        """Save column widths."""
        self.settings.setValue("column_widths", column_widths)

    def load_column_widths(self):
        """Load column widths."""
        return self.settings.value("column_widths", [], type=list)

    def save_sorting(self, column, order):
        """Save sorting settings."""
        self.settings.setValue("sort_column", column)
        self.settings.setValue("sort_order", order)

    def load_sorting(self):
        """Load sorting settings. Returns tuple (column, order)."""
        column = self.settings.value("sort_column", -1, type=int)
        order = self.settings.value("sort_order", 0, type=int)
        return column, order

    def clear_settings(self):
        """Clear all settings."""
        self.settings.clear()
