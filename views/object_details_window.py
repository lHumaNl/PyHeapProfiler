# views/object_details_window.py

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView, QLabel, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QCursor
from PySide6.QtCore import Qt
from models.heap_dump import HeapDumpModel
from views.object_attribute_window import ObjectAttributeWindow


class ObjectDetailsWindow(QWidget):
    def __init__(self, obj_type, current_dump, comparison_dump=None):
        super().__init__()
        self.obj_type = obj_type
        self.current_dump = current_dump
        self.comparison_dump = comparison_dump
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle(f"Детали объектов: {self.obj_type}")
        self.resize(800, 600)

        self.model = None
        self.objects = {}
        self.loaded_rows = 0
        self.object_statuses = {}

        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Таблица
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        # Кнопка для загрузки всех объектов
        self.load_all_button = QPushButton("Загрузить все объекты")
        self.layout.addWidget(self.load_all_button)
        self.load_all_button.clicked.connect(self.load_all_objects)

        # Сводные данные
        self.summary_label = QLabel("Сводные данные будут отображаться здесь.")
        self.layout.addWidget(self.summary_label)

        # Настройка таблицы
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.clicked.connect(self.handle_row_click)

        # Ленивая подгрузка
        self.table_view.verticalScrollBar().valueChanged.connect(self.lazy_load_more)

        # Установка курсора при наведении на ячейки ID ссылки
        self.table_view.setMouseTracking(True)
        self.table_view.entered.connect(self.change_cursor)

    def populate_table(self):
        self.model = QStandardItemModel()
        headers = ["ID ссылки", "Размер объекта", "Количество ссылок", "Количество атрибутов"]

        if self.comparison_dump:
            headers.append("Статус объекта")

        self.model.setHorizontalHeaderLabels(headers)

        # Получаем объекты
        self.objects = self.current_dump.processed_data.get(self.obj_type, {}).get('objects', {})

        # Если есть сравнение, получаем статусы объектов
        if self.comparison_dump:
            self.object_statuses = self.current_dump.get_object_statuses(self.obj_type, self.comparison_dump)
        else:
            self.object_statuses = {obj_id: 'Старый' for obj_id in self.objects.keys()}

        self.loaded_rows = 0

        # Ленивая загрузка первых 100 объектов
        self.lazy_load_objects(limit=100)

        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(1, Qt.DescendingOrder)  # Сортировка по размеру объекта
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.resizeColumnsToContents()

        # Обновление сводных данных
        total_objects = len(self.objects)
        self.summary_label.setText(f"Общее количество объектов: {total_objects}")

    def lazy_load_objects(self, limit=100):
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

                size_item = QStandardItem()
                size_item.setData(obj_data['size'], Qt.DisplayRole)

                ref_count = len(obj_data.get('ref', []))
                ref_item = QStandardItem()
                ref_item.setData(ref_count, Qt.DisplayRole)

                attr_count = len(obj_data.get('attr', {}))
                attr_item = QStandardItem()
                attr_item.setData(attr_count, Qt.DisplayRole)

                row_items = [id_item, size_item, ref_item, attr_item]

                if self.comparison_dump:
                    status = self.object_statuses.get(obj_id, 'Неизвестно')
                    status_item = QStandardItem(status)
                    row_items.append(status_item)

                self.model.appendRow(row_items)
                count += 1
                self.loaded_rows += 1
        except Exception as e:
            self.logger.exception("Ошибка при ленивой загрузке объектов")

    def load_all_objects(self):
        # Загрузка всех объектов
        try:
            self.lazy_load_objects(limit=len(self.objects) - self.loaded_rows)
        except Exception as e:
            self.logger.exception("Ошибка при загрузке всех объектов")

    def lazy_load_more(self):
        scrollbar = self.table_view.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            # Пользователь прокрутил до конца, загружаем еще объекты
            self.lazy_load_objects(limit=100)

    def handle_row_click(self, index):
        if index.column() == 0:  # ID ссылки
            obj_id = self.model.item(index.row(), 0).data(Qt.UserRole)
            obj_data = self.objects.get(obj_id)
            if obj_data:
                self.show_object_details(obj_id, obj_data)

    def show_object_details(self, obj_id, obj_data):
        # Открываем новое окно с деталями объекта
        details_window = ObjectAttributeWindow(obj_id, obj_data, self.current_dump)
        details_window.show()

        # Сохраняем ссылку на окно, чтобы не было закрыто сборщиком мусора
        if not hasattr(self, 'attribute_windows'):
            self.attribute_windows = []
        self.attribute_windows.append(details_window)

    def change_cursor(self, index):
        if index.column() == 0:
            self.table_view.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.table_view.setCursor(QCursor(Qt.ArrowCursor))
