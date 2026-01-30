import orjson
import logging
import threading


class HeapDumpValidationError(Exception):
    """Custom exception for heap dump validation errors."""
    pass


class HeapDumpModel:
    """
    Model representing a heap dump loaded from a JSON file.
    """

    def __init__(self, file_path):
        """
        Initialize heap dump model.

        Args:
            file_path (str): Path to heap dump JSON file.
        """
        self.file_path = file_path
        self.data = {}
        self.total_objects = 0
        self.total_size = 0
        self.processed_data = {}
        self.logger = logging.getLogger(__name__)
        self._loading_thread = None
        self._progress_callback = None

    def load_data(self):
        """
        Load data from JSON file synchronously.
        """
        try:
            with open(self.file_path, 'rb') as f:
                self.data = orjson.loads(f.read())

            self.validate_dump_structure()
            self.process_data()
            self.logger.info(f"Data loaded from {self.file_path}")
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"Heap dump file not found: {self.file_path}") from e
        except orjson.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file: {self.file_path}")
            raise ValueError(f"Invalid JSON file: {str(e)}. Please ensure the file is a valid JSON.") from e
        except Exception as e:
            self.logger.exception(f"Failed to load data from {self.file_path}")
            raise e

    def load_data_async(self, progress_callback=None):
        """
        Load data from the JSON file asynchronously using threading.

        Args:
            progress_callback: Optional callback function to report progress (current, total).
        """
        self._progress_callback = progress_callback
        self._loading_thread = threading.Thread(target=self._load_in_background)
        self._loading_thread.start()

    def _load_in_background(self):
        """
        Load data in a background thread with progress reporting.
        """
        try:
            file_size = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            chunks = []

            with open(self.file_path, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0, 0)

                bytes_read = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    bytes_read += len(chunk)
                    
                    if self._progress_callback:
                        self._progress_callback(bytes_read, file_size)

            json_data = b''.join(chunks)
            self.data = orjson.loads(json_data)
            self.process_data()
            
            if self._progress_callback:
                self._progress_callback(file_size, file_size)
                
            self.logger.info(f"Data loaded from {self.file_path}")
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"Heap dump file not found: {self.file_path}") from e
        except orjson.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file: {self.file_path}")
            raise ValueError(f"Invalid JSON file: {str(e)}. Please ensure the file is a valid JSON.") from e
        except Exception as e:
            self.logger.exception(f"Failed to load data from {self.file_path}")
            raise e

    def validate_dump_structure(self):
        """
        Validate the structure of the loaded heap dump data.

        Raises:
            HeapDumpValidationError: If the data structure is invalid.
        """
        if not isinstance(self.data, dict):
            raise HeapDumpValidationError(
                "Invalid heap dump structure: Expected a dictionary with object types as keys."
            )

        if not self.data:
            self.logger.warning("Heap dump is empty")
            raise HeapDumpValidationError("Heap dump file is empty.")

        for obj_type, objs in self.data.items():
            if not isinstance(objs, dict):
                raise HeapDumpValidationError(
                    f"Invalid structure for object type '{obj_type}': Expected a dictionary of objects."
                )

            for obj_id, obj_data in objs.items():
                if not isinstance(obj_data, dict):
                    raise HeapDumpValidationError(
                        f"Invalid object data for {obj_type}[{obj_id}]: Expected a dictionary."
                    )

                # Check for required or expected fields
                if 'size' not in obj_data:
                    self.logger.warning(f"Object {obj_type}[{obj_id}] missing 'size' field")

                # Validate size is numeric if present
                if 'size' in obj_data and not isinstance(obj_data['size'], (int, float)):
                    self.logger.warning(f"Object {obj_type}[{obj_id}] has non-numeric 'size' field")

    def wait_for_loading(self):
        """
        Wait for the async loading to complete.
        """
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_thread.join()
        self._loading_thread = None

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

    def filter_by_size(self, min_size=None, max_size=None):
        """
        Filter object types by total size.

        Args:
            min_size (int, optional): Minimum total size in bytes.
            max_size (int, optional): Maximum total size in bytes.

        Returns:
            dict: Filtered processed data.
        """
        filtered = {}
        for obj_type, data in self.processed_data.items():
            size = data['total_size']
            if min_size is not None and size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue
            filtered[obj_type] = data
        return filtered

    def filter_by_type(self, obj_types):
        """
        Filter by specific object types.

        Args:
            obj_types (list): List of object type names to include.

        Returns:
            dict: Filtered processed data.
        """
        filtered = {}
        for obj_type in obj_types:
            if obj_type in self.processed_data:
                filtered[obj_type] = self.processed_data[obj_type]
        return filtered

    def get_all_object_types(self):
        """
        Get list of all object types.

        Returns:
            list: List of object type names.
        """
        return list(self.processed_data.keys())

    def search_objects(self, obj_type, search_id=None, search_attr_value=None, search_in_types=False):
        """
        Search for objects within a specific type.

        Args:
            obj_type (str): The object type to search in.
            search_id (str, optional): Object ID to search for.
            search_attr_value (str, optional): Attribute value to search for.
            search_in_types (bool, optional): If True, search in all object types.

        Returns:
            dict: Filtered objects matching search criteria.
        """
        if search_in_types:
            results = {}
            for ot in self.processed_data.keys():
                results.update(self._search_in_type(ot, search_id, search_attr_value))
            return {obj_type: {'num_objects': len(results), 'total_size': sum(o.get('size', 0) for o in results.values()), 'objects': results}}
        else:
            filtered_objs = self._search_in_type(obj_type, search_id, search_attr_value)
            if filtered_objs:
                return {obj_type: {'num_objects': len(filtered_objs), 'total_size': sum(o.get('size', 0) for o in filtered_objs.values()), 'objects': filtered_objs}}
            return {}

    def _search_in_type(self, obj_type, search_id=None, search_attr_value=None):
        """
        Helper method to search within a specific object type.

        Args:
            obj_type (str): The object type to search in.
            search_id (str, optional): Object ID to search for.
            search_attr_value (str, optional): Attribute value to search for.

        Returns:
            dict: Filtered objects.
        """
        objects = self.processed_data.get(obj_type, {}).get('objects', {})
        filtered = {}
        for obj_id, obj_data in objects.items():
            match = True
            if search_id and search_id not in str(obj_id):
                match = False
            if search_attr_value and match:
                attrs = obj_data.get('attr', {})
                found = any(search_attr_value in str(v) for v in attrs.values())
                if not found:
                    match = False
            if match:
                filtered[obj_id] = obj_data
        return filtered

    def filter_comparison_by_status(self, comparison_result, status_filter):
        """
        Filter comparison results by object status.

        Args:
            comparison_result (dict): Original comparison results.
            status_filter (list): List of statuses to include ('New', 'Deleted', 'Old', 'Modified').

        Returns:
            dict: Filtered comparison results.
        """
        filtered = {}
        for obj_type, data in comparison_result.items():
            new = data.get('num_new_objects', 0)
            deleted = data.get('num_deleted_objects', 0)
            total_main = data.get('num_objects_main', 0)
            total_other = data.get('num_objects_other', 0)
            
            include = False
            if 'New' in status_filter and new > 0:
                include = True
            elif 'Deleted' in status_filter and deleted > 0:
                include = True
            elif 'Old' in status_filter and total_main == total_other and new == 0 and deleted == 0:
                include = True
            elif 'Modified' in status_filter and total_other != total_main:
                include = True
            
            if include or not status_filter:
                filtered[obj_type] = data
        return filtered
