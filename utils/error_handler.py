import logging
import traceback
from functools import wraps
from PySide6.QtWidgets import QMessageBox


def log_errors(func):
    """
    Decorator to log errors with full stack trace and re-raise them.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__module__)
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper


def show_error_message(parent, title, message, details=None):
    """
    Show a user-friendly error message with optional details.

    Args:
        parent: Parent widget for the message box.
        title (str): Title of the error dialog.
        message (str): User-friendly error message.
        details (str, optional): Detailed error information (stack trace).
    """
    if details:
        QMessageBox.critical(parent, title, f"{message}\n\nDetails:\n{details}")
    else:
        QMessageBox.critical(parent, title, message)


def format_exception(e):
    """
    Format an exception into a user-friendly message.

    Args:
        e (Exception): The exception to format.

    Returns:
        str: Formatted error message.
    """
    error_type = type(e).__name__
    error_message = str(e)
    return f"{error_type}: {error_message}"


def get_traceback():
    """
    Get the current exception traceback as a string.

    Returns:
        str: Formatted traceback string.
    """
    return traceback.format_exc()
