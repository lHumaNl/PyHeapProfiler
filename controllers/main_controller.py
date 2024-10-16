import logging
from PySide6.QtWidgets import QFileDialog
from models.heap_dump import HeapDumpModel

class MainController:
    """
    Controller for handling main window events and actions.
    """
    def __init__(self, view):
        """
        Initialize the controller with the main window view.

        Args:
            view: The main window instance.
        """
        self.view = view
        self.logger = logging.getLogger(__name__)

    def handle_load_dump(self):
        """
        Handle the action of loading a heap dump JSON file.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.view, "Open Heap Dump (JSON)", "", "JSON Files (*.json)"
            )
            if file_name:
                self.view.current_dump = HeapDumpModel(file_name)
                self.view.populate_table(self.view.current_dump)
                self.view.compare_button.setEnabled(True)
                self.view.show_message("Success", f"Heap dump loaded: {file_name}")
                self.logger.info(f"Heap dump loaded from {file_name}")
        except Exception as e:
            self.logger.exception("Failed to load heap dump")
            self.view.show_message("Error", f"Failed to load heap dump: {e}")

    def handle_compare_dumps(self):
        """
        Handle the action of loading a comparison heap dump JSON file.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.view, "Open Heap Dump for Comparison (JSON)", "", "JSON Files (*.json)"
            )
            if file_name:
                self.view.comparison_dump = HeapDumpModel(file_name)
                self.view.populate_table(self.view.current_dump, comparison=True)
                self.view.show_message("Success", f"Comparison heap dump loaded: {file_name}")
                self.logger.info(f"Comparison heap dump loaded from {file_name}")
        except Exception as e:
            self.logger.exception("Failed to load comparison heap dump")
            self.view.show_message("Error", f"Failed to load comparison heap dump: {e}")

    def handle_table_click(self, index):
        """
        Handle the action when a table cell is clicked.

        Args:
            index: The index of the clicked cell.
        """
        try:
            if index.column() == 0:  # Object Type column
                obj_type = index.data()
                self.view.open_object_details(obj_type)
        except Exception as e:
            self.logger.exception("Failed to handle table click")
            self.view.show_message("Error", f"Failed to open object details: {e}")
