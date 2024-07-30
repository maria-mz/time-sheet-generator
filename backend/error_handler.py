"""
Backend error handler decorator
"""
import logging

from backend.errors import InternalError, CSVReadError
from db.db_handler import EmployeeAlreadyExistsError


_logger = logging.getLogger(__name__)


def error_handler(func):
    """
    Wraps a backend function in a try-except block.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CSVReadError as e:
            _logger.error(e)
            raise e
        except EmployeeAlreadyExistsError as e:
            _logger.error(e)
            raise e
        except Exception as e:
            _logger.exception(e)
            raise InternalError

    return wrapper
