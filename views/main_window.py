import logging
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QTableView, QLabel, QHeaderView, QMessageBox, QMenu
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtCore import Qt
from views.object_details_window import ObjectDetailsWindow
from controllers.main_controller import MainController

class MainWindow(QMainWindow):
    """
    The main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heap Dump Analyzer")
        self.resize(800, 600)
        self.logger = logging.getLogger(__name__)

        self.current_dump = None
        self.comparison_dump = None
        self.details_windows = []

        self.controller = MainController(self)

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.load_button = QPushButton("Load Heap Dump\n(JSON)")
        self.compare_button = QPushButton("Load for\nComparison")
        self.compare_button.setEnabled(False)

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.compare_button)

        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.summary_label = QLabel("Summary data will be displayed here.")
        self.layout.addWidget(self.summary_label)

        self.load_button.clicked.connect(self.controller.handle_load_dump)
        self.compare_button.clicked.connect(self.controller.handle_compare_dumps)
        self.table_view.clicked.connect(self.controller.handle_table_click)

        # Context menu for toggling columns
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_column_menu)

    def populate_table(self, data, comparison=False):
        """
        Populate the main table with data.

        Args:
            data (HeapDumpModel): The heap dump data to display.
            comparison (bool): Whether to include comparison data.
        """
        try:
            model = QStandardItemModel()
            headers = [
                "Object\nType", "Number of\nObjects", "% of\nTotal\nObjects",
                "Total Size\n(bytes)", "% of\nTotal\nSize"
            ]

            if comparison:
                headers.extend([
                    "Objects\n(Main)", "Objects\n(Comparison)",
                    "New\nObjects", "Deleted\nObjects",
                    "Size\n(Main)", "Size\n(Comparison)",
                    "Size\nChange\n(%)", "Size\nChange\n(bytes)"
                ])

            model.setHorizontalHeaderLabels(headers)

            total_objects = data.total_objects
            total_size = data.total_size

            if comparison:
                comparison_results = self.current_dump.compare_with(self.comparison_dump)
                all_obj_types = set(comparison_results.keys())
            else:
                all_obj_types = data.processed_data.keys()

            for obj_type in all_obj_types:
                type_item = QStandardItem(obj_type)
                type_item.setEditable(False)
                type_item.setForeground(Qt.blue)
                type_item.setData(obj_type, Qt.UserRole)

                if comparison:
                    comp_result = comparison_results.get(obj_type, {})
                    num_objects_main = comp_result.get('num_objects_main', 0)
                    num_objects_other = comp_result.get('num_objects_other', 0)
                    num_new_objects = comp_result.get('num_new_objects', 0)
                    num_deleted_objects = comp_result.get('num_deleted_objects', 0)

                    total_size_main = comp_result.get('total_size_main', 0)
                    total_size_other = comp_result.get('total_size_other', 0)
                    size_change = comp_result.get('size_change', 0)
                    size_percent_change = comp_result.get('size_percent_change', 0)

                    # For display purposes, we can set None if zero
                    num_new_objects_display = num_new_objects if num_new_objects != 0 else None
                    num_deleted_objects_display = num_deleted_objects if num_deleted_objects != 0 else None
                    size_change_display = size_change if size_change != 0 else None
                    size_percent_change_display = size_percent_change if size_percent_change != 0 else None

                    num_total_objects = num_objects_main + num_new_objects - num_deleted_objects
                    total_objects_combined = self.current_dump.total_objects + self.comparison_dump.total_objects
                    perc_objects = (num_total_objects / total_objects_combined) * 100 if total_objects_combined else 0

                    total_size_combined = total_size_main + size_change
                    total_size_overall = self.current_dump.total_size + self.comparison_dump.total_size
                    perc_size = (total_size_combined / total_size_overall) * 100 if total_size_overall else 0

                    row_items = [
                        type_item,
                        QStandardItem(str(num_total_objects)),
                        QStandardItem(f"{perc_objects:.2f}"),
                        QStandardItem(str(total_size_combined)),
                        QStandardItem(f"{perc_size:.2f}"),
                        QStandardItem(str(num_objects_main)),
                        QStandardItem(str(num_objects_other)),
                        QStandardItem(str(num_new_objects_display) if num_new_objects_display is not None else ""),
                        QStandardItem(str(num_deleted_objects_display) if num_deleted_objects_display is not None else ""),
                        QStandardItem(str(total_size_main)),
                        QStandardItem(str(total_size_other)),
                        QStandardItem(f"{size_percent_change_display:.2f}" if size_percent_change_display is not None else ""),
                        QStandardItem(str(size_change_display) if size_change_display is not None else "")
                    ]
                else:
                    obj_data = data.processed_data[obj_type]
                    num_objects = obj_data['num_objects']
                    total_size_obj = obj_data['total_size']

                    perc_objects = (num_objects / total_objects) * 100 if total_objects else 0
                    perc_size = (total_size_obj / total_size) * 100 if total_size else 0

                    row_items = [
                        type_item,
                        QStandardItem(str(num_objects)),
                        QStandardItem(f"{perc_objects:.2f}"),
                        QStandardItem(str(total_size_obj)),
                        QStandardItem(f"{perc_size:.2f}")
                    ]

                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.setSortingEnabled(True)
            self.table_view.sortByColumn(1, Qt.DescendingOrder)
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Interactive)  # Allow column width adjustment
            self.table_view.resizeColumnsToContents()
            self.table_view.horizontalHeader().setStretchLastSection(False)

            # Adjust window size to fit columns
            total_width = self.table_view.verticalHeader().width()
            for i in range(model.columnCount()):
                total_width += self.table_view.columnWidth(i)
            total_width += self.table_view.verticalScrollBar().sizeHint().width()
            self.resize(total_width + 50, self.height())

            self.summary_label.setText(
                f"Total objects: {data.total_objects}, Total size: {data.total_size} bytes"
            )

            self.logger.info("Main table populated successfully")
        except Exception as e:
            self.logger.exception("Failed to populate main table")
            self.show_message("Error", f"Failed to populate table: {e}")

    def show_message(self, title, message):
        """
        Display a message box.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        QMessageBox.information(self, title, message)

    def open_object_details(self, obj_type):
        """
        Open the object details window for a specific object type.

        Args:
            obj_type (str): The object type to display.
        """
        try:
            details_window = ObjectDetailsWindow(obj_type, self.current_dump, self.comparison_dump)
            details_window.show()
            details_window.activateWindow()
            self.details_windows.append(details_window)
            self.logger.info(f"Opened details window for object type {obj_type}")
        except Exception as e:
            self.logger.exception("Failed to open object details window")
            self.show_message("Error", f"Failed to open object details: {e}")

    def show_column_menu(self, position):
        """
        Show a context menu to toggle column visibility.

        Args:
            position: The position where the menu is requested.
        """
        menu = QMenu()
        model = self.table_view.model()
        if not model:
            return

        header = self.table_view.horizontalHeader()
        for col in range(model.columnCount()):
            action = QAction(model.headerData(col, Qt.Horizontal), self)
            action.setCheckable(True)
            action.setChecked(not self.table_view.isColumnHidden(col))
            action.toggled.connect(lambda checked, c=col: self.table_view.setColumnHidden(c, not checked))
            menu.addAction(action)

        menu.exec(self.table_view.viewport().mapToGlobal(position))
