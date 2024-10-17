import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView, QLabel, QAbstractItemView, QMenu
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QCursor, QAction
from PySide6.QtCore import Qt, QSortFilterProxyModel
from views.object_attribute_window import ObjectAttributeWindow
from utils.helpers import int_or_none, float_or_none


class ObjectDetailsWindow(QWidget):
    """
    Window displaying details of objects of a specific type.
    """

    def __init__(self, obj_type, current_dump, comparison_dump=None):
        """
        Initialize the object details window.

        Args:
            obj_type (str): The object type to display.
            current_dump (HeapDumpModel): The main heap dump.
            comparison_dump (HeapDumpModel, optional): The comparison heap dump.
        """
        super().__init__()
        self.obj_type = obj_type
        self.current_dump = current_dump
        self.comparison_dump = comparison_dump
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle(f"Object Details: {self.obj_type}")
        self.resize(800, 600)

        self.model = None
        self.objects = {}
        self.loaded_rows = 0
        self.object_statuses = {}
        self.attribute_windows = []

        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Table
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.load_all_button = QPushButton("Load All Objects")
        self.layout.addWidget(self.load_all_button)
        self.load_all_button.clicked.connect(self.load_all_objects)

        self.summary_label = QLabel("Summary data will be displayed here.")
        self.layout.addWidget(self.summary_label)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.clicked.connect(self.handle_row_click)

        self.table_view.verticalScrollBar().valueChanged.connect(self.lazy_load_more)

        self.table_view.setMouseTracking(True)
        self.table_view.entered.connect(self.change_cursor)

        # Context menu for toggling columns
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_column_menu)

    def populate_table(self):
        """
        Populate the table with object data.
        """
        try:
            self.model = QStandardItemModel()
            if self.comparison_dump:
                headers = [
                    "Object\nID", "Object\nStatus", "Size\n(Main)", "Size\n(Comparison)",
                    "Refs\n(Main)", "Refs\n(Comparison)", "Attrs\n(Main)", "Attrs\n(Comparison)",
                    "New\nRefs", "Deleted\nRefs", "New\nAttrs", "Deleted\nAttrs",
                    "Size\nChange\n(%)", "Size\nChange\n(bytes)"
                ]
            else:
                headers = ["Object ID", "Size", "Number of Refs", "Number of Attrs"]

            self.model.setHorizontalHeaderLabels(headers)

            if self.comparison_dump:
                self.object_statuses = self.current_dump.get_object_statuses(self.obj_type, self.comparison_dump)
                current_objects = self.current_dump.processed_data.get(self.obj_type, {}).get('objects', {})
                comparison_objects = self.comparison_dump.processed_data.get(self.obj_type, {}).get('objects', {})
                all_obj_ids = set(current_objects.keys()).union(comparison_objects.keys())

                for obj_id in all_obj_ids:
                    row_items = []
                    id_item = QStandardItem(str(obj_id))
                    id_item.setForeground(Qt.blue)
                    id_item.setData(obj_id, Qt.UserRole)
                    row_items.append(id_item)

                    status = self.object_statuses.get(obj_id, 'Unknown')
                    status_item = QStandardItem(status)
                    row_items.append(status_item)

                    obj_main = current_objects.get(obj_id)
                    obj_comp = comparison_objects.get(obj_id)

                    size_main = obj_main.get('size', 0) if obj_main else None
                    size_comp = obj_comp.get('size', 0) if obj_comp else None

                    size_main_item = QStandardItem(int_or_none(size_main))
                    size_main_item.setData(size_main or 0, Qt.UserRole)
                    size_comp_item = QStandardItem(int_or_none(size_comp))
                    size_comp_item.setData(size_comp or 0, Qt.UserRole)

                    row_items.extend([size_main_item, size_comp_item])

                    refs_main = obj_main.get('ref', []) if obj_main else []
                    refs_comp = obj_comp.get('ref', []) if obj_comp else []

                    num_refs_main = len(refs_main) if refs_main else 0
                    num_refs_comp = len(refs_comp) if refs_comp else 0

                    num_refs_main_item = QStandardItem(int_or_none(num_refs_main))
                    num_refs_main_item.setData(num_refs_main or 0, Qt.UserRole)
                    num_refs_comp_item = QStandardItem(int_or_none(num_refs_comp))
                    num_refs_comp_item.setData(num_refs_comp or 0, Qt.UserRole)

                    row_items.extend([num_refs_main_item, num_refs_comp_item])

                    attrs_main = obj_main.get('attr', {}) if obj_main else {}
                    attrs_comp = obj_comp.get('attr', {}) if obj_comp else {}

                    num_attrs_main = len(attrs_main) if attrs_main else 0
                    num_attrs_comp = len(attrs_comp) if attrs_comp else 0

                    num_attrs_main_item = QStandardItem(int_or_none(num_attrs_main))
                    num_attrs_main_item.setData(num_attrs_main or 0, Qt.UserRole)
                    num_attrs_comp_item = QStandardItem(int_or_none(num_attrs_comp))
                    num_attrs_comp_item.setData(num_attrs_comp or 0, Qt.UserRole)

                    row_items.extend([num_attrs_main_item, num_attrs_comp_item])

                    # Handle unhashable types in refs and attrs
                    try:
                        new_refs = len(set(map(str, refs_comp)) - set(map(str, refs_main))) if refs_comp else 0
                        del_refs = len(set(map(str, refs_main)) - set(map(str, refs_comp))) if refs_main else 0
                    except Exception as e:
                        self.logger.exception("Failed to compute new/deleted refs")
                        new_refs = del_refs = 0

                    new_refs_item = QStandardItem(int_or_none(new_refs))
                    new_refs_item.setData(new_refs or 0, Qt.UserRole)
                    del_refs_item = QStandardItem(int_or_none(del_refs))
                    del_refs_item.setData(del_refs or 0, Qt.UserRole)

                    try:
                        new_attrs = len(set(attrs_comp.keys()) - set(attrs_main.keys())) if attrs_comp else 0
                        del_attrs = len(set(attrs_main.keys()) - set(attrs_comp.keys())) if attrs_main else 0
                    except Exception as e:
                        self.logger.exception("Failed to compute new/deleted attrs")
                        new_attrs = del_attrs = 0

                    new_attrs_item = QStandardItem(int_or_none(new_attrs))
                    new_attrs_item.setData(new_attrs or 0, Qt.UserRole)
                    del_attrs_item = QStandardItem(int_or_none(del_attrs))
                    del_attrs_item.setData(del_attrs or 0, Qt.UserRole)

                    if size_main and size_comp:
                        size_change = size_comp - size_main
                        size_percent_change = (size_change / size_main * 100) if size_main else 0
                    else:
                        size_change = 0
                        size_percent_change = 0

                    size_percent_change_item = QStandardItem(float_or_none(size_percent_change))
                    size_percent_change_item.setData(size_percent_change or 0, Qt.UserRole)
                    size_change_item = QStandardItem(int_or_none(size_change))
                    size_change_item.setData(size_change or 0, Qt.UserRole)

                    row_items.extend([
                        new_refs_item, del_refs_item,
                        new_attrs_item, del_attrs_item,
                        size_percent_change_item, size_change_item
                    ])

                    self.model.appendRow(row_items)
            else:
                self.objects = self.current_dump.processed_data.get(self.obj_type, {}).get('objects', {})
                self.loaded_rows = 0
                self.lazy_load_objects(limit=100)

            # Set up proxy model for numeric sorting
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setSourceModel(self.model)
            self.proxy_model.setSortRole(Qt.UserRole)
            self.table_view.setModel(self.proxy_model)

            self.table_view.setSortingEnabled(True)
            self.table_view.sortByColumn(1, Qt.DescendingOrder)
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Interactive)  # Allow column width adjustment
            self.table_view.resizeColumnsToContents()
            self.table_view.horizontalHeader().setStretchLastSection(False)

            # Adjust column widths
            for col in range(self.model.columnCount()):
                self.table_view.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

            total_objects = self.model.rowCount()
            self.summary_label.setText(f"Total objects: {total_objects}")
            self.logger.info("Object details table populated successfully")
        except Exception as e:
            self.logger.exception("Failed to populate object details table")

    def lazy_load_objects(self, limit=100):
        """
        Load objects lazily to prevent UI blocking.

        Args:
            limit (int): Number of objects to load at a time.
        """
        try:
            count = 0
            obj_ids = list(self.objects.keys())[self.loaded_rows:]
            for obj_id in obj_ids:
                if count >= limit:
                    break

                obj_data = self.objects[obj_id]

                id_item = QStandardItem(str(obj_id))
                id_item.setForeground(Qt.blue)
                id_item.setData(obj_id, Qt.UserRole)

                size_value = obj_data.get('size', 0) or 0
                size_item = QStandardItem(int_or_none(size_value))
                size_item.setData(size_value, Qt.UserRole)

                ref_count = len(obj_data.get('ref', []))
                ref_item = QStandardItem(int_or_none(ref_count))
                ref_item.setData(ref_count, Qt.UserRole)

                attr_count = len(obj_data.get('attr', {}))
                attr_item = QStandardItem(int_or_none(attr_count))
                attr_item.setData(attr_count, Qt.UserRole)

                row_items = [id_item, size_item, ref_item, attr_item]

                self.model.appendRow(row_items)
                count += 1
                self.loaded_rows += 1
        except Exception as e:
            self.logger.exception("Error during lazy loading of objects")

    def load_all_objects(self):
        """
        Load all remaining objects.
        """
        try:
            self.lazy_load_objects(limit=len(self.objects) - self.loaded_rows)
        except Exception as e:
            self.logger.exception("Failed to load all objects")

    def lazy_load_more(self):
        """
        Trigger lazy loading when the user scrolls to the bottom.
        """
        scrollbar = self.table_view.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            self.lazy_load_objects(limit=100)

    def handle_row_click(self, index):
        """
        Handle clicks on table rows.

        Args:
            index: The model index of the clicked cell.
        """
        try:
            if index.column() == 0:  # Object ID column
                obj_id = self.proxy_model.data(self.proxy_model.index(index.row(), 0), Qt.UserRole)
                if self.comparison_dump:
                    # Decide which dump to use based on object status
                    status = self.proxy_model.data(self.proxy_model.index(index.row(), 1))
                    if status in ['Old', 'Deleted', 'Modified']:
                        obj_data = self.current_dump.processed_data.get(self.obj_type, {}).get('objects', {}).get(
                            obj_id)
                    else:
                        obj_data = self.comparison_dump.processed_data.get(self.obj_type, {}).get('objects', {}).get(
                            obj_id)
                else:
                    obj_data = self.objects.get(str(obj_id))
                if obj_data:
                    self.show_object_details(obj_id, obj_data)
        except Exception as e:
            self.logger.exception("Failed to handle row click")

    def show_object_details(self, obj_id, obj_data):
        """
        Show detailed information about an object.

        Args:
            obj_id: The ID of the object.
            obj_data: The data of the object.
        """
        try:
            details_window = ObjectAttributeWindow(obj_id, obj_data, self.current_dump)
            details_window.show()
            self.attribute_windows.append(details_window)
            self.logger.info(f"Opened attribute window for object ID {obj_id}")
        except Exception as e:
            self.logger.exception("Failed to show object details")

    def change_cursor(self, index):
        """
        Change the cursor when hovering over certain cells.

        Args:
            index: The model index of the cell under the cursor.
        """
        if index.column() == 0:
            self.table_view.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.table_view.setCursor(QCursor(Qt.ArrowCursor))

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
