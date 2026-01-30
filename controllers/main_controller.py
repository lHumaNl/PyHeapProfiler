import logging
import json
from PySide6.QtWidgets import QFileDialog
from models.heap_dump import HeapDumpModel
from utils.error_handler import show_error_message, get_traceback


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
                self.view.show_loading()
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()

                self.view.current_dump = HeapDumpModel(file_name)
                self.view.current_dump.load_data()

                self._on_dump_loaded()
                self.logger.info(f"Heap dump loaded from {file_name}")
        except FileNotFoundError as e:
            self.logger.exception("File not found")
            show_error_message(self.view, "File Error", 
                              f"Could not find the file: {str(e)}", get_traceback())
            self.view.hide_loading()
        except json.JSONDecodeError as e:
            self.logger.exception("Invalid JSON format")
            show_error_message(self.view, "Invalid JSON File",
                              f"The file is not a valid JSON file: {str(e)}\n\nPlease check the file format.",
                              get_traceback())
            self.view.hide_loading()
        except ValueError as e:
            self.logger.exception("Invalid data format")
            show_error_message(self.view, "Data Format Error",
                              f"The heap dump data format is invalid: {str(e)}",
                              get_traceback())
            self.view.hide_loading()
        except Exception as e:
            self.logger.exception("Failed to load heap dump")
            show_error_message(self.view, "Loading Error",
                              f"Failed to load heap dump: {str(e)}", get_traceback())
            self.view.hide_loading()

    def _on_dump_loaded(self):
        """Called when heap dump loading is complete."""
        self.view.populate_table(self.view.current_dump)
        self.view.hide_loading()
        self.view.show_message("Success", f"Heap dump loaded successfully\n{self.view.current_dump.file_path}")
        self.logger.info(f"Heap dump loaded from {self.view.current_dump.file_path}")

        # Enable buttons
        self.view.chart_button.setEnabled(True)
        self.view.export_button.setEnabled(True)
        self.view.compare_button.setEnabled(True)

        # Enable menu actions
        if hasattr(self.view, 'charts_menu_action'):
            self.view.charts_menu_action.setEnabled(True)
        if hasattr(self.view, 'export_menu_action'):
            self.view.export_menu_action.setEnabled(True)
        if hasattr(self.view, 'compare_menu_action'):
            self.view.compare_menu_action.setEnabled(True)

        # Enable toolbar actions
        if hasattr(self.view, 'charts_toolbar_action'):
            self.view.charts_toolbar_action.setEnabled(True)
        if hasattr(self.view, 'export_toolbar_action'):
            self.view.export_toolbar_action.setEnabled(True)
        if hasattr(self.view, 'compare_toolbar_action'):
            self.view.compare_toolbar_action.setEnabled(True)

    def handle_compare_dumps(self):
        """
        Handle the action of loading a comparison heap dump JSON file.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.view, "Open Heap Dump for Comparison (JSON)", "", "JSON Files (*.json)"
            )
            if file_name:
                self.view.show_loading()
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()

                self.view.comparison_dump = HeapDumpModel(file_name)
                self.view.comparison_dump.load_data()

                self._on_comparison_loaded()
                self.logger.info(f"Comparison heap dump loaded from {file_name}")
        except FileNotFoundError as e:
            self.logger.exception("File not found")
            show_error_message(self.view, "File Error",
                              f"Could not find the file: {str(e)}", get_traceback())
            self.view.hide_loading()
        except json.JSONDecodeError as e:
            self.logger.exception("Invalid JSON format")
            show_error_message(self.view, "Invalid JSON File",
                              f"The file is not a valid JSON file: {str(e)}\n\nPlease check the file format.",
                              get_traceback())
            self.view.hide_loading()
        except ValueError as e:
            self.logger.exception("Invalid data format")
            show_error_message(self.view, "Data Format Error",
                              f"The heap dump data format is invalid: {str(e)}",
                              get_traceback())
            self.view.hide_loading()
        except Exception as e:
            self.logger.exception("Failed to load comparison heap dump")
            show_error_message(self.view, "Loading Error",
                              f"Failed to load comparison heap dump: {str(e)}", get_traceback())
            self.view.hide_loading()

    def _on_comparison_loaded(self):
        """Called when comparison heap dump loading is complete."""
        self.view.populate_table(self.view.current_dump, comparison=True)
        self.view.hide_loading()
        self.view.show_message("Success", f"Comparison heap dump loaded successfully\n{self.view.comparison_dump.file_path}")
        self.logger.info(f"Comparison heap dump loaded from {self.view.comparison_dump.file_path}")
        self.view.chart_button.setEnabled(True)
        self.view.export_button.setEnabled(True)

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
        except AttributeError as e:
            self.logger.exception("Invalid table data")
            show_error_message(self.view, "Data Error",
                              f"Invalid table data: {str(e)}", get_traceback())
        except Exception as e:
            self.logger.exception("Failed to handle table click")
            show_error_message(self.view, "Action Error",
                              f"Failed to open object details: {str(e)}", get_traceback())

    def handle_export(self):
        """
        Handle the action of exporting results.
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self.view, "Export Results", "", 
                "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx)"
            )
            if file_name:
                self.view.export_results(file_name)
                self.view.show_message("Success", f"Results exported successfully\n{file_name}")
                self.logger.info(f"Results exported to {file_name}")
        except Exception as e:
            self.logger.exception("Failed to export results")
            show_error_message(self.view, "Export Error",
                              f"Failed to export results: {str(e)}", get_traceback())

    def handle_refresh(self):
        """
        Handle the action of refreshing/reloading the current dump.
        """
        try:
            if self.view.current_dump:
                if self.view.comparison_dump:
                    self.view.populate_table(self.view.current_dump, comparison=True)
                else:
                    self.view.populate_table(self.view.current_dump)
                self.view.show_message("Success", "Data refreshed successfully")
                self.logger.info("Data refreshed")
            else:
                self.view.show_message("Info", "No heap dump loaded to refresh")
        except Exception as e:
            self.logger.exception("Failed to refresh data")
            show_error_message(self.view, "Refresh Error",
                              f"Failed to refresh data: {str(e)}", get_traceback())

    def handle_show_charts(self):
        """
        Handle the action of showing memory usage charts.
        """
        try:
            if self.view.current_dump:
                from views.chart_window import ChartWindow
                chart_window = ChartWindow(self.view.current_dump)
                self.view.chart_windows.append(chart_window)
                chart_window.show()
                chart_window.activateWindow()
                self.logger.info("Chart window opened")
            else:
                self.view.show_message("Info", "Load a heap dump first to view charts")
        except Exception as e:
            self.logger.exception("Failed to show charts")
            show_error_message(self.view, "Chart Error",
                              f"Failed to display charts: {str(e)}", get_traceback())

    def handle_apply_filters(self, min_size, max_size, obj_type, status_filter, search_id, search_attr):
        """
        Handle the action of applying filters to the data.

        Args:
            min_size (int, optional): Minimum size filter.
            max_size (int, optional): Maximum size filter.
            obj_type (str, optional): Object type filter.
            status_filter (list): List of status filters.
            search_id (str, optional): Object ID to search for.
            search_attr (str, optional): Attribute value to search for.
        """
        try:
            if not self.view.current_dump:
                return

            # Start with all data
            filtered_data = self.view.current_dump.processed_data.copy()

            # Apply size filter
            if min_size is not None or max_size is not None:
                size_filtered = self.view.current_dump.filter_by_size(min_size, max_size)
                # Keep only object types that match size filter
                filtered_data = {k: v for k, v in filtered_data.items() if k in size_filtered}

            # Apply object type filter
            if obj_type:
                filtered_data = {k: v for k, v in filtered_data.items() if k == obj_type}

            # Apply search filters
            if search_id or search_attr:
                if obj_type:
                    # Search within specific type
                    search_result = self.view.current_dump.search_objects(
                        obj_type, search_id, search_attr, search_in_types=False
                    )
                    if search_result:
                        filtered_data = {obj_type: search_result[obj_type]}
                    else:
                        filtered_data = {}
                else:
                    # Search across all types
                    all_types = list(filtered_data.keys())
                    filtered_data = {}
                    for ot in all_types:
                        search_result = self.view.current_dump.search_objects(
                            ot, search_id, search_attr, search_in_types=False
                        )
                        if search_result and ot in search_result:
                            filtered_data[ot] = search_result[ot]

            # Handle comparison mode with status filter
            if self.view.comparison_dump:
                comparison_results = self.view.current_dump.compare_with(self.view.comparison_dump)
                
                # Apply status filter
                if status_filter:
                    comparison_results = self.view.current_dump.filter_comparison_by_status(
                        comparison_results, status_filter
                    )
                
                # Filter by comparison results
                filtered_data = {k: v for k, v in filtered_data.items() if k in comparison_results}
            
            # Create a temporary dump model with filtered data
            from models.heap_dump import HeapDumpModel
            filtered_dump = HeapDumpModel.__new__(HeapDumpModel)
            filtered_dump.processed_data = filtered_data
            filtered_dump.total_objects = sum(v['num_objects'] for v in filtered_data.values())
            filtered_dump.total_size = sum(v['total_size'] for v in filtered_data.values())
            
            # Populate table with filtered data
            self.view.populate_table(filtered_dump, comparison=bool(self.view.comparison_dump))
            self.logger.info("Filters applied successfully")
        except Exception as e:
            self.logger.exception("Failed to apply filters")
            show_error_message(self.view, "Filter Error",
                              f"Failed to apply filters: {str(e)}", get_traceback())
