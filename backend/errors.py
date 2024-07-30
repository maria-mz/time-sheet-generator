class CSVReadError(Exception):
    """
    Raised when the backend fails to read the provided .csv file for
    importing employees 
    """

class InternalError(Exception):
    """
    Raised when the backend encounters an unexpected error
    """
