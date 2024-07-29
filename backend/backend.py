"""Global Backend Module"""

from typing import Union
import pandas as pd
import atexit
import logging

from db.db_handler import DatabaseHandler
from db.db_data import PayPeriod, Shift, Employee
import utils
import constants


_logger = logging.getLogger(__name__)


class CSVReadError(Exception):
    """
    Raised when the backend fails to read the provided .csv file for
    importing employees 
    """


class Backend:
    def __init__(self):
        _logger.info("backend initializing...")

        self.db_handler = DatabaseHandler(constants.DB_PATH)

        self.db_handler.create_settings_table()
        self.db_handler.create_shift_table()
        self.db_handler.create_employee_table()

        self.db_handler.commit()

        _logger.info("backend ready")

    def get_pay_period(self) -> Union[PayPeriod, None]:
        return self.db_handler.get_pay_period()

    def update_pay_period(self, pay_period: PayPeriod) -> None:
        self.db_handler.update_pay_period(pay_period)

        self.db_handler.delete_shift_table()
        self.db_handler.delete_employee_table()

        self.db_handler.create_shift_table()
        self.db_handler.create_employee_table()

        self.db_handler.commit()

    def update_employee(self, employee: Employee) -> None:
        self.db_handler.update_employee(employee)
        self.db_handler.commit()

    def update_employees(self, employees: list[Employee]) -> None:
        self.db_handler.update_employees(employees)
        self.db_handler.commit()

    def add_employee(self, employee: Employee) -> None:
        self.db_handler.add_employee(employee)
        self.db_handler.commit()

    def add_employees(self, employees: list[Employee]) -> None:
        self.db_handler.add_employees(employees)
        self.db_handler.commit()

    def delete_employee(self, employee: Employee) -> None:
        self.db_handler.delete_employee(employee.employee_id)
        self.db_handler.commit()

    def get_employees(self) -> list[Employee]:
        return self.db_handler.get_employees()

    def generate_employees_from_csv(self, file_path: str) -> list[Employee]:
        employees = []

        try:
            df = pd.read_csv(file_path, dtype=str)
        except FileNotFoundError:
            raise CSVReadError("File not found.")
        except pd.errors.EmptyDataError:
            raise CSVReadError("File is empty.")
        except pd.errors.ParserError:
            raise CSVReadError("Error parsing file.")

        required_cols = {"Full Name", "Employee Number", "Job Title"}

        if missing_cols := required_cols - set(df.columns):
            raise CSVReadError(f"File is missing header columns: {missing_cols}")

        def row_to_employee(row) -> Employee:
            employee_id = str(row["Employee Number"]) if not pd.isna(row["Employee Number"]) else ""
            full_name = str(row["Full Name"]) if not pd.isna(row["Full Name"]) else ""
            position = str(row["Job Title"]) if not pd.isna(row["Job Title"]) else ""
            shifts = self._get_fresh_shifts()

            return Employee(
                employee_id=employee_id,
                full_name=full_name,
                position=position,
                shifts=shifts
            )

        employees = df.apply(row_to_employee, axis=1).tolist()

        return employees

    def _get_fresh_shifts(self) -> list[Shift]:
        pay_period = self.db_handler.get_pay_period()

        if pay_period is None:
            return []

        return [
            Shift(date=utils.next_date(pay_period.start_date, i)) \
            for i in range(constants.PAY_PERIOD_DAYS)
        ]

    def create_empty_employee(self) -> Employee:
        return Employee(
            employee_id="",
            full_name="",
            position="",
            shifts=self._get_fresh_shifts()
        )

    def _shutdown(self) -> None:
        _logger.info("backend shutting down")
        self.db_handler.close()


backend = Backend()

atexit.register(backend._shutdown)
