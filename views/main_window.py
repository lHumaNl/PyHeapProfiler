# views/main_window.py

import logging
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QTableView, QLabel, QHeaderView, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from models.heap_dump import HeapDumpModel
from views.object_details_window import ObjectDetailsWindow
from controllers.main_controller import MainController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализатор дампов памяти")
        self.resize(800, 600)

        self.current_dump = None
        self.comparison_dump = None
        self.details_windows = []

        self.controller = MainController(self)

        self.setup_ui()

    def setup_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Кнопки
        self.load_button = QPushButton("Загрузить\nдамп памяти\n(JSON)")
        self.compare_button = QPushButton("Загрузить для\nсравнения")
        self.compare_button.setEnabled(False)

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.compare_button)

        # Таблица
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        # Сводные данные
        self.summary_label = QLabel("Сводные данные будут отображаться здесь.")
        self.layout.addWidget(self.summary_label)

        # Подключение сигналов
        self.load_button.clicked.connect(self.controller.handle_load_dump)
        self.compare_button.clicked.connect(self.controller.handle_compare_dumps)
        self.table_view.clicked.connect(self.controller.handle_table_click)

    def populate_table(self, data, comparison=False):
        model = QStandardItemModel()
        headers = [
            "Тип\nобъекта", "Количество\nобъектов", "% от\nобщего\nколичества",
            "Объем\nв байтах", "% от\nобщего\nобъема"
        ]

        if comparison:
            headers.extend([
                "Количество\nобъектов\n(основной)", "Количество\nобъектов\n(сравнение)",
                "Новые\nобъекты", "Удаленные\nобъекты",
                "Объем в\nбайтах\n(основной)", "Объем в\nбайтах\n(сравнение)",
                "Изменение\nразмера\n(%)", "Изменение\nразмера"
            ])

        model.setHorizontalHeaderLabels(headers)

        total_objects = data.total_objects
        total_size = data.total_size

        if comparison:
            all_obj_types = set(self.current_dump.processed_data.keys()).union(
                self.comparison_dump.processed_data.keys()
            )
        else:
            all_obj_types = data.processed_data.keys()

        for obj_type in all_obj_types:
            type_item = QStandardItem(obj_type)
            type_item.setEditable(False)
            type_item.setForeground(Qt.blue)
            type_item.setData(obj_type, Qt.UserRole)

            if obj_type in data.processed_data:
                obj_data = data.processed_data[obj_type]
                num_objects = obj_data['num_objects']
                total_size_obj = obj_data['total_size']
            else:
                num_objects = 0
                total_size_obj = 0

            num_item = QStandardItem()
            num_item.setData(num_objects, Qt.DisplayRole)

            perc_objects = (num_objects / total_objects) * 100 if total_objects else 0
            perc_objects_item = QStandardItem()
            perc_objects_item.setData(perc_objects, Qt.DisplayRole)

            size_item = QStandardItem()
            size_item.setData(total_size_obj, Qt.DisplayRole)

            perc_size = (total_size_obj / total_size) * 100 if total_size else 0
            perc_size_item = QStandardItem()
            perc_size_item.setData(perc_size, Qt.DisplayRole)

            row_items = [type_item, num_item, perc_objects_item, size_item, perc_size_item]

            if comparison:
                comparison_result = self.current_dump.compare_with(self.comparison_dump).get(obj_type, {})

                num_objects_main = comparison_result.get('num_objects_main', 0)
                num_objects_other = comparison_result.get('num_objects_other', 0)
                num_new_objects = comparison_result.get('num_new_objects', 0)
                num_deleted_objects = comparison_result.get('num_deleted_objects', 0)

                total_size_main = comparison_result.get('total_size_main', 0)
                total_size_other = comparison_result.get('total_size_other', 0)
                size_change = comparison_result.get('size_change', 0)
                size_percent_change = comparison_result.get('size_percent_change', 0)

                # Пересчитываем колонки: количество объектов и объем
                num_objects_combined = num_objects_main + num_new_objects - num_deleted_objects
                total_size_combined = total_size_main + size_change

                num_item.setData(num_objects_combined, Qt.DisplayRole)
                size_item.setData(total_size_combined, Qt.DisplayRole)

                # % от общего количества и размера
                total_objects_combined = self.current_dump.total_objects + self.comparison_dump.total_objects
                total_size_combined_all = self.current_dump.total_size + self.comparison_dump.total_size

                perc_objects_combined = (num_objects_combined / total_objects_combined) * 100 if total_objects_combined else 0
                perc_objects_item.setData(perc_objects_combined, Qt.DisplayRole)

                perc_size_combined = (total_size_combined / total_size_combined_all) * 100 if total_size_combined_all else 0
                perc_size_item.setData(perc_size_combined, Qt.DisplayRole)

                # Создаем элементы таблицы
                num_objects_main_item = QStandardItem()
                num_objects_main_item.setData(num_objects_main, Qt.DisplayRole)

                num_objects_other_item = QStandardItem()
                num_objects_other_item.setData(num_objects_other, Qt.DisplayRole)

                num_new_item = QStandardItem()
                num_new_item.setData(num_new_objects if num_new_objects != 0 else None, Qt.DisplayRole)

                num_deleted_item = QStandardItem()
                num_deleted_item.setData(num_deleted_objects if num_deleted_objects != 0 else None, Qt.DisplayRole)

                total_size_main_item = QStandardItem()
                total_size_main_item.setData(total_size_main, Qt.DisplayRole)

                total_size_other_item = QStandardItem()
                total_size_other_item.setData(total_size_other, Qt.DisplayRole)

                size_percent_change_item = QStandardItem()
                size_percent_change_item.setData(size_percent_change if size_percent_change != 0 else None, Qt.DisplayRole)

                size_change_item = QStandardItem()
                size_change_item.setData(size_change if size_change != 0 else None, Qt.DisplayRole)

                row_items.extend([
                    num_objects_main_item,
                    num_objects_other_item,
                    num_new_item,
                    num_deleted_item,
                    total_size_main_item,
                    total_size_other_item,
                    size_percent_change_item,
                    size_change_item
                ])

            model.appendRow(row_items)

        self.table_view.setModel(model)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(1, Qt.DescendingOrder)  # Сортировка по количеству объектов
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.resizeColumnsToContents()

        # Подстройка ширины главного окна
        total_width = self.table_view.verticalHeader().width()  # Ширина вертикального заголовка
        for i in range(model.columnCount()):
            total_width += self.table_view.columnWidth(i)
        total_width += self.table_view.verticalScrollBar().sizeHint().width()  # Ширина скроллбара
        self.resize(total_width + 50, self.height())  # Добавляем немного к ширине

        # Обновление сводных данных
        self.summary_label.setText(
            f"Общее количество объектов: {data.total_objects}, Общий объем: {data.total_size} байт"
        )

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def open_object_details(self, obj_type):
        details_window = ObjectDetailsWindow(obj_type, self.current_dump, self.comparison_dump)
        details_window.show()
        details_window.activateWindow()
        self.details_windows.append(details_window)  # Сохраняем ссылку на окно
