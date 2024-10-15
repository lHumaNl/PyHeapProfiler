# views/object_attribute_window.py

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit
)
from PySide6.QtCore import Qt


class ObjectAttributeWindow(QWidget):
    def __init__(self, obj_id, obj_data, heap_dump):
        super().__init__()
        self.obj_id = obj_id
        self.obj_data = obj_data
        self.heap_dump = heap_dump
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle(f"Детали объекта ID: {obj_id}")
        self.resize(400, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Атрибуты объекта
        attr_label = QLabel("Атрибуты объекта:")
        layout.addWidget(attr_label)

        attr_text = QTextEdit()
        attr_text.setReadOnly(True)
        attr_content = ""

        attr_data = self.obj_data.get('attr', {})
        for key, value in attr_data.items():
            attr_content += f"{key}: {value}\n"

        attr_text.setText(attr_content)
        layout.addWidget(attr_text)

        # Ссылки объекта
        ref_label = QLabel("Ссылки объекта:")
        layout.addWidget(ref_label)

        ref_text = QTextEdit()
        ref_text.setReadOnly(True)
        ref_content = ""

        ref_data = self.obj_data.get('ref', [])
        for ref in ref_data:
            if isinstance(ref, list) and len(ref) == 2:
                ref_type, ref_id = ref
                ref_content += f"{ref_type} (ID: {ref_id})\n"
            else:
                ref_content += f"{ref}\n"

        ref_text.setText(ref_content)
        layout.addWidget(ref_text)
