"""
Worker classes for asynchronous operations.
"""
from PySide6.QtCore import QObject, Signal
import logging
import orjson


class ProgressWorker(QObject):
    """
    Worker for asynchronous loading with progress reporting.
    """
    progress_updated = Signal(int, int)
    loading_finished = Signal()
    loading_error = Signal(str, str)

    def __init__(self, model, file_path):
        super().__init__()
        self.model = model
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def load_data(self):
        try:
            file_size = 0
            chunk_size = 1024 * 1024
            
            with open(self.file_path, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0, 0)
                
                bytes_read = 0
                chunks = []
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    bytes_read += len(chunk)
                    self.progress_updated.emit(bytes_read, file_size)
            
            json_data = b''.join(chunks)
            self.model.data = orjson.loads(json_data)
            self.model.validate_dump_structure()
            self.model.process_data()
            self.progress_updated.emit(file_size, file_size)
            self.loading_finished.emit()
        except Exception as e:
            import traceback
            self.logger.exception(f"Error loading file {self.file_path}")
            self.loading_error.emit(str(e), traceback.format_exc())
