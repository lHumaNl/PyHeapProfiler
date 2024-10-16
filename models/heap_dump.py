import json
import logging

class HeapDumpModel:
    """
    Model representing a heap dump loaded from a JSON file.
    """
    def __init__(self, file_path):
        """
        Initialize the heap dump model.

        Args:
            file_path (str): Path to the heap dump JSON file.
        """
        self.file_path = file_path
        self.data = {}
        self.total_objects = 0
        self.total_size = 0
        self.processed_data = {}
        self.logger = logging.getLogger(__name__)

        self.load_data()

    def load_data(self):
        """
        Load data from the JSON file.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.process_data()
            self.logger.info(f"Data loaded from {self.file_path}")
        except Exception as e:
            self.logger.exception(f"Failed to load data from {self.file_path}")
            raise e

    def process_data(self):
        """
        Process raw data to calculate totals and prepare for display.
        """
        self.processed_data = {}
        self.total_objects = 0
        self.total_size = 0

        for obj_type, objs in self.data.items():
            num_objs = len(objs)
            size = sum(obj.get('size', 0) for obj in objs.values())

            self.processed_data[obj_type] = {
                'num_objects': num_objs,
                'total_size': size,
                'objects': objs
            }

            self.total_objects += num_objs
            self.total_size += size

        self.logger.info("Data processed successfully")

    def compare_with(self, other_dump):
        """
        Compare this heap dump with another heap dump.

        Args:
            other_dump (HeapDumpModel): The other heap dump to compare with.

        Returns:
            dict: Comparison results.
        """
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

        self.logger.info("Comparison completed successfully")
        return comparison_result

    def get_object_statuses(self, obj_type, other_dump):
        """
        Get statuses of objects for a specific type when compared to another heap dump.

        Args:
            obj_type (str): The object type to analyze.
            other_dump (HeapDumpModel): The other heap dump for comparison.

        Returns:
            dict: Object IDs mapped to their statuses ('New', 'Deleted', 'Old', 'Modified').
        """
        current_objects = self.processed_data.get(obj_type, {}).get('objects', {})
        other_objects = other_dump.processed_data.get(obj_type, {}).get('objects', {})

        statuses = {}
        for obj_id in set(current_objects.keys()).union(other_objects.keys()):
            if obj_id in current_objects and obj_id in other_objects:
                if current_objects[obj_id] != other_objects[obj_id]:
                    statuses[obj_id] = 'Modified'
                else:
                    statuses[obj_id] = 'Old'
            elif obj_id in current_objects:
                statuses[obj_id] = 'Deleted'
            else:
                statuses[obj_id] = 'New'

        self.logger.debug(f"Object statuses computed for type {obj_type}")
        return statuses
