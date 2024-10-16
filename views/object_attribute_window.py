import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QLabel, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class ObjectAttributeWindow(QWidget):
    """
    Window displaying attributes and references of a specific object.
    """
    def __init__(self, obj_id, obj_data, heap_dump):
        """
        Initialize the object attribute window.

        Args:
            obj_id: The ID of the object.
            obj_data: The data of the object.
            heap_dump: The heap dump model.
        """
        super().__init__()
        self.obj_id = obj_id
        self.obj_data = obj_data
        self.heap_dump = heap_dump
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle(f"Object Details - ID: {obj_id}")
        self.resize(600, 800)

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Attributes Table
        attr_label = QLabel("Object Attributes:")
        layout.addWidget(attr_label)

        self.attr_table = QTableView()
        layout.addWidget(self.attr_table)
        self.populate_attributes()

        # References Table
        ref_label = QLabel("Object References:")
        layout.addWidget(ref_label)

        self.ref_table = QTableView()
        layout.addWidget(self.ref_table)
        self.populate_references()

        # Source Information
        src_info = self.obj_data.get('src', {})
        if src_info:
            src_label = QLabel("Source Information:")
            layout.addWidget(src_label)
            src_text = QLabel(f"Name: {src_info.get('co_name')}, "
                              f"File: {src_info.get('co_filename')}, "
                              f"Line: {src_info.get('co_lineno')}")
            layout.addWidget(src_text)

    def populate_attributes(self):
        """
        Populate the attributes table.
        """
        try:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Attribute", "Value", "Type"])

            attr_data = self.obj_data.get('attr', {})
            for attr_name, attr_value in attr_data.items():
                name_item = QStandardItem(str(attr_name))
                if isinstance(attr_value, list) and len(attr_value) == 2:
                    value_item = QStandardItem(f"Object ID: {attr_value[1]}")
                    type_item = QStandardItem(str(attr_value[0]))
                else:
                    value_item = QStandardItem(str(attr_value))
                    type_item = QStandardItem(str(type(attr_value).__name__))

                model.appendRow([name_item, value_item, type_item])

            self.attr_table.setModel(model)
            self.attr_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.attr_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.attr_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        except Exception as e:
            self.logger.exception("Failed to populate attributes table")

    def populate_references(self):
        """
        Populate the references table.
        """
        try:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Value", "Type"])

            ref_data = self.obj_data.get('ref', [])
            for ref in ref_data:
                if isinstance(ref, list) and len(ref) == 2:
                    value_item = QStandardItem(f"Object ID: {ref[1]}")
                    value_item.setForeground(Qt.blue)
                    value_item.setData(ref, Qt.UserRole)
                    type_item = QStandardItem(str(ref[0]))
                else:
                    value_item = QStandardItem(str(ref))
                    type_item = QStandardItem(str(type(ref).__name__))

                model.appendRow([value_item, type_item])

            self.ref_table.setModel(model)
            self.ref_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.ref_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.ref_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # Handle clicks on object references
            self.ref_table.clicked.connect(self.handle_ref_click)
        except Exception as e:
            self.logger.exception("Failed to populate references table")

    def handle_ref_click(self, index):
        """
        Handle clicks on reference entries.

        Args:
            index: The model index of the clicked cell.
        """
        try:
            ref_data = index.model().item(index.row(), 0).data(Qt.UserRole)
            if ref_data:
                ref_type, ref_id = ref_data
                obj_data = self.heap_dump.data.get(ref_type, {}).get(str(ref_id))
                if obj_data:
                    new_window = ObjectAttributeWindow(ref_id, obj_data, self.heap_dump)
                    new_window.show()
        except Exception as e:
            self.logger.exception("Failed to handle reference click")
