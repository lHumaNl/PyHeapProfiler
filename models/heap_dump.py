# models/heap_dump.py

import json


class HeapDumpModel:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self.total_objects = 0
        self.total_size = 0
        self.processed_data = {}

        self.load_data()

    def load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.process_data()

    def process_data(self):
        self.processed_data = {}
        self.total_objects = 0
        self.total_size = 0

        for obj_type, objs in self.data.items():
            num_objs = len(objs)
            size = sum(obj['size'] for obj in objs.values())

            self.processed_data[obj_type] = {
                'num_objects': num_objs,
                'total_size': size,
                'objects': objs
            }

            self.total_objects += num_objs
            self.total_size += size

    def compare_with(self, other_dump):
        comparison_result = {}

        all_obj_types = set(self.processed_data.keys()).union(other_dump.processed_data.keys())

        for obj_type in all_obj_types:
            data = self.processed_data.get(obj_type, {'num_objects': 0, 'total_size': 0, 'objects': {}})
            other_data = other_dump.processed_data.get(obj_type, {'num_objects': 0, 'total_size': 0, 'objects': {}})

            num_objects_main = data['num_objects']
            num_objects_other = other_data['num_objects']
            num_new = num_objects_other - num_objects_main
            num_deleted = num_objects_main - num_objects_other

            total_size_main = data['total_size']
            total_size_other = other_data['total_size']
            size_change = total_size_other - total_size_main
            size_percent_change = (size_change / total_size_main * 100) if total_size_main else 0

            comparison_result[obj_type] = {
                'num_objects_main': num_objects_main,
                'num_objects_other': num_objects_other,
                'num_new_objects': num_new if num_new > 0 else 0,
                'num_deleted_objects': num_deleted if num_deleted > 0 else 0,
                'total_size_main': total_size_main,
                'total_size_other': total_size_other,
                'size_change': size_change,
                'size_percent_change': size_percent_change
            }

        return comparison_result

    def get_object_statuses(self, obj_type, other_dump):
        current_objects = self.processed_data.get(obj_type, {}).get('objects', {})
        other_objects = other_dump.processed_data.get(obj_type, {}).get('objects', {})

        statuses = {}
        for obj_id in set(current_objects.keys()).union(other_objects.keys()):
            if obj_id in current_objects and obj_id in other_objects:
                statuses[obj_id] = 'Старый'
            elif obj_id in current_objects and obj_id not in other_objects:
                statuses[obj_id] = 'Удаленный'
            elif obj_id not in current_objects and obj_id in other_objects:
                statuses[obj_id] = 'Новый'

        return statuses
