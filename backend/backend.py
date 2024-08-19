"""Global Backend Module"""

from typing import Union
import pandas as pd
import atexit
import logging

from backend.errors import CSVReadError
from backend.error_handler import error_handler
from db.db_handler import DatabaseHandler
from db.db_data import PayPeriod, Shift, Employee
import utils
import constants


_logger = logging.getLogger(__name__)


class Backend:
    def __init__(self):
        _logger.info("backend initializing...")

        self.db_handler = DatabaseHandler(constants.DB_PATH)

        self.db_handler.create_settings_table()
        self.db_handler.create_shift_table()
        self.db_handler.create_employee_table()

        self.db_handler.commit()

        _logger.info("backend ready")

    @error_handler
    def get_pay_period(self) -> Union[PayPeriod, None]:
        return self.db_handler.get_pay_period()

    @error_handler
    def update_pay_period(self, pay_period: PayPeriod) -> None:
        _logger.info(f"updating pay period to {pay_period}")

        self.db_handler.update_pay_period(pay_period)

        self._clear_employee_data()

        _logger.info(f"pay period updated!")

    @error_handler
    def update_employee(self, employee: Employee) -> None:
        self.db_handler.update_employee(employee)
        self.db_handler.commit()

    @error_handler
    def update_employees(self, employees: list[Employee]) -> None:
        self.db_handler.update_employees(employees)
        self.db_handler.commit()

    @error_handler
    def add_employee(self, employee: Employee) -> None:
        self.db_handler.add_employee(employee)
        self.db_handler.commit()

    @error_handler
    def add_employees(self, employees: list[Employee]) -> None:
        self.db_handler.add_employees(employees)
        self.db_handler.commit()

    @error_handler
    def delete_employee(self, employee: Employee) -> None:
        self.db_handler.delete_employee(employee.employee_id)
        self.db_handler.commit()

    @error_handler
    def delete_employees(self) -> None:
        self._clear_employee_data()

    def _clear_employee_data(self) -> None:
        self.db_handler.delete_shift_table()
        self.db_handler.delete_employee_table()

        self.db_handler.create_shift_table()
        self.db_handler.create_employee_table()

        self.db_handler.commit()

    @error_handler
    def get_employees(self) -> list[Employee]:
        return self.db_handler.get_employees()

    @error_handler
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

        required_cols = {"First Name", "Last Name", "Employee No", "Job Title", "Contract"}

        if missing_cols := required_cols - set(df.columns):
            raise CSVReadError(f"File is missing header columns: {missing_cols}")

        def format_value(value) -> str:
            return str(value) if not pd.isna(value) else ""

        def row_to_employee(row) -> Employee:
            return Employee(
                employee_id=format_value(row["Employee No"]),
                first_name=format_value(row["First Name"]),
                last_name=format_value(row["Last Name"]),
                position=format_value(row["Job Title"]),
                contract=format_value(row["Contract"]),
                shifts=self._get_default_shifts()
            )

        employees = df.apply(row_to_employee, axis=1).tolist()

        return employees

    def _get_default_shifts(self) -> list[Shift]:
        pay_period = self.db_handler.get_pay_period()

        if pay_period is None:
            return []

        shifts = []
        
        for i in range(constants.PAY_PERIOD_DAYS):
            date = utils.next_date(pay_period.start_date, i)

            if date.weekday() >= 5: # is a weekend
                shift = Shift(
                    date=date,
                    time_in=None,
                    time_out=None,
                    hours_reg=constants.DEFAULT_HOURS_WEEKEND,
                    hours_ot=constants.DEFAULT_HOURS_WEEKEND
                )
            else:
                shift = Shift(date=date)

            shifts.append(shift)

        return shifts

    def create_empty_employee(self) -> Employee:
        return Employee(
            employee_id="",
            first_name="",
            last_name="",
            position="",
            contract="",
            shifts=self._get_default_shifts()
        )

    def shutdown(self) -> None:
        _logger.info("backend shutting down")
        self.db_handler.close()


try:
    backend = Backend()
except Exception as e:
    _logger.exception(f"failed to initialize backend. terminating program")
    exit(1)

atexit.register(backend.shutdown)
