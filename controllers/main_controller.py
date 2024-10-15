# controllers/main_controller.py

import logging
from PySide6.QtWidgets import QFileDialog
from models.heap_dump import HeapDumpModel


class MainController:
    def __init__(self, view):
        self.view = view
        self.logger = logging.getLogger(__name__)

    def handle_load_dump(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.view, "Открыть дамп памяти (JSON)", "", "JSON Files (*.json)"
            )
            if file_name:
                self.view.current_dump = HeapDumpModel(file_name)
                self.view.populate_table(self.view.current_dump)
                self.view.compare_button.setEnabled(True)
                self.view.show_message("Успех", f"Дамп памяти загружен: {file_name}")
        except Exception as e:
            self.logger.exception("Ошибка при загрузке дампа памяти")
            self.view.show_message("Ошибка", f"Не удалось загрузить дамп памяти: {e}")

    def handle_compare_dumps(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.view, "Открыть дамп памяти для сравнения (JSON)", "", "JSON Files (*.json)"
            )
            if file_name:
                self.view.comparison_dump = HeapDumpModel(file_name)
                self.view.populate_table(self.view.current_dump, comparison=True)
                self.view.show_message("Успех", f"Дамп для сравнения загружен: {file_name}")
        except Exception as e:
            self.logger.exception("Ошибка при загрузке дампа для сравнения")
            self.view.show_message("Ошибка", f"Не удалось загрузить дамп для сравнения: {e}")

    def handle_table_click(self, index):
        if index.column() == 0:  # Тип объекта
            obj_type = index.data()
            self.view.open_object_details(obj_type)
