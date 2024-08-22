"""DatabaseHandler Class"""

import sqlite3
from typing import Union

import utils
import constants
from db.db_data import PayPeriod, Employee, Shift


class EmployeeAlreadyExistsError(Exception):
    pass


class DatabaseHandler:
    """
    Database Handler for interacting with the app's SQLite database.
    """

    def __init__(self, db: str):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

        # Enable foreign key constraints
        self.cur.execute("PRAGMA foreign_keys = ON;")

    def create_settings_table(self) -> None:
        """
        Create a new `settings` table if one doesn't exist already.
        """
        if self._table_exists("settings"):
            return

        with self.conn:
            self.cur.execute(
                """
                CREATE TABLE settings(
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )

            self.cur.execute(
                "INSERT INTO settings VALUES (:key, :value)",
                {"key": "pay_period_start_date", "value": None}
            )
            self.cur.execute(
                "INSERT INTO settings VALUES (:key, :value)",
                {"key": "pay_period_end_date", "value": None}
            )

    def create_employee_table(self) -> None:
        """
        Create a new `employee` table if one doesn't exist already.
        """
        if self._table_exists("employee"):
            return

        with self.conn:
            self.cur.execute(
                """
                CREATE TABLE employee(
                    employee_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    position TEXT,
                    contract TEXT
                )
                """
            )

    def create_shift_table(self) -> None:
        """
        Create a new `shift` table if one doesn't exist already.
        """
        if self._table_exists("shift"):
            return

        with self.conn:
            self.cur.execute(
                """
                CREATE TABLE shift(
                    date TEXT,
                    time_in TEXT,
                    time_out TEXT,
                    hours_reg TEXT,
                    hours_ot TEXT,
                    employee_id TEXT REFERENCES employee(employee_id)
                    ON DELETE CASCADE
                )
                """
            )

            self.cur.execute(
                "CREATE INDEX idx_employee_id ON shift (employee_id)"
            )

    def delete_settings_table(self) -> None:
        """
        Delete the `settings` table.
        """
        with self.conn:
            self.cur.execute("DROP TABLE IF EXISTS settings")

    def delete_employee_table(self) -> None:
        """
        Delete the `employee` table.
        """
        with self.conn:
            self.cur.execute("DROP TABLE IF EXISTS employee")

    def delete_shift_table(self):
        """
        Delete the `shift` table.
        """
        with self.conn:
            self.cur.execute("DROP TABLE IF EXISTS shift")

    def _update_settings(self, key: str, value: str) -> None:
        self.cur.execute(
            "UPDATE settings SET value=:value WHERE key=:key",
            {"key": key, "value": value}
        )

    def _get_settings(self, key: str) -> Union[str, None]:
        res = self.cur.execute(
            "SELECT value FROM settings WHERE key=:key", {"key": key}
        )

        row = res.fetchone()

        return row[0] if row is not None else None

    def update_pay_period(self, pay_period: PayPeriod) -> None:
        """
        Update the pay period.
        """
        start_date = pay_period.start_date.strftime(constants.DATE_FORMAT)
        end_date = pay_period.end_date.strftime(constants.DATE_FORMAT)

        with self.conn:
            self._update_settings(key="pay_period_start_date", value=start_date)
            self._update_settings(key="pay_period_end_date", value=end_date)

    def get_pay_period(self) -> Union[PayPeriod, None]:
        """
        Get the pay period. If a pay period hasn't been set yet, returns None.
        """
        start_date = self._get_settings(key="pay_period_start_date")
        end_date = self._get_settings(key="pay_period_end_date")

        if start_date is None or end_date is None:
            return None

        return PayPeriod(
            start_date=utils.str_to_date(start_date, constants.DATE_FORMAT),
            end_date=utils.str_to_date(end_date, constants.DATE_FORMAT)
        )

    def get_employees(self) -> list[Employee]:
        """
        Get all employees.
        """
        res = self.cur.execute(f"SELECT * FROM employee ORDER BY first_name")

        rows = res.fetchall()

        employees = []

        for row in rows:
            employee = Employee(
                employee_id=row[0],
                first_name=row[1],
                last_name=row[2],
                position=row[3],
                contract=row[4],
                shifts=[]
            )

            shifts = self._get_shifts(employee.employee_id)
            employee.shifts = shifts

            employees.append(employee)

        return employees

    def get_employee(self, employee_id: str) -> Union[Employee, None]:
        """
        Get the employee matching the id. If no match, returns None.
        """
        res = self.cur.execute(
            f"SELECT * FROM employee WHERE employee_id='{employee_id}'"
        )
        
        row = res.fetchone()

        if row is None:
            return None

        return Employee(
            employee_id=employee_id,
            first_name=row[1],
            last_name=row[2],
            position=row[3],
            contract=row[4],
            shifts=self._get_shifts(employee_id)
        )

    def add_employee(self, employee: Employee) -> None:
        """
        Add a new employee. If there is already an employee with the same id,
        raises sqlite3.IntegrityError.
        """
        with self.conn:
            self._add_employee(employee)

    def _add_employee(self, employee: Employee) -> None:
        self.cur.execute(
            """
            INSERT INTO employee VALUES
            (:employee_id, :first_name, :last_name, :position, :contract)
            """,
            {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "position": employee.position,
                "contract": employee.contract
            }
        )

        for shift in employee.shifts:
            self._add_shift(employee.employee_id, shift)

    def add_employees(self, employees: list[Employee]) -> None:
        """
        Add a list of employees.
        """
        with self.conn:
            for employee in employees:
                self._add_employee(employee)

    def delete_employee(self, employee_id: str) -> None:
        """
        Delete an employee. Deletes all shifts as well. If an employee with this id
        doesn't exist, delete is a no-op.
        """
        with self.conn:
            self.cur.execute(
                "DELETE FROM employee WHERE employee_id=:employee_id",
                {"employee_id": employee_id}
            )

    def update_employee(self, employee: Employee) -> None:
        """
        Update an existing employee.
        """
        with self.conn:
            self._update_employee(employee)

    def _update_employee(self, employee: Employee) -> None:
        self.cur.execute(
            """
            UPDATE employee SET
            first_name=:first_name,
            last_name=:last_name,
            position=:position,
            contract=:contract
            WHERE employee_id=:employee_id
            """,
            {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "position": employee.position,
                "contract": employee.contract
            }
        )

        if self.cur.rowcount == 0:  # No employee found
            return

        for shift in employee.shifts:
            self._update_shift(employee.employee_id, shift)

    def update_employees(self, employees: list[Employee]) -> None:
        """
        Update a list of employees.
        """
        with self.conn:
            for employee in employees:
                self._update_employee(employee)

    def _get_shifts(self, employee_id: str) -> list[Shift]:
        """
        Get all the shifts for an employee.
        """
        res = self.cur.execute(
            "SELECT * FROM shift WHERE employee_id=:employee_id ORDER BY date",
            {"employee_id": employee_id}
        )

        rows = res.fetchall()

        shifts = []

        for row in rows:
            date = utils.str_to_date(row[0], constants.DATE_FORMAT)
            time_in = utils.str_to_time(row[1], constants.TIME_FORMAT) if row[1] else None
            time_out = utils.str_to_time(row[2], constants.TIME_FORMAT) if row[2] else None
            hours_reg = row[3]
            hours_ot = row[4]

            shift = Shift(
                date=date,
                time_in=time_in,
                time_out=time_out,
                hours_reg=hours_reg,
                hours_ot=hours_ot,
            )
            shifts.append(shift)

        return shifts

    def _add_shift(self, employee_id: str, shift: Shift) -> None:
        """
        Add a new shift for an employee. If an employee with this id doesn't exist,
        raises sqlite3.IntegrityError.
        """
        date = shift.date.strftime(constants.DATE_FORMAT)
        time_in = shift.time_in.strftime(constants.TIME_FORMAT) if shift.time_in else None
        time_out = shift.time_out.strftime(constants.TIME_FORMAT) if shift.time_out else None
        hours_reg = shift.hours_reg
        hours_ot = shift.hours_ot

        self.cur.execute(
            """
            INSERT INTO shift VALUES
            (:date, :time_in, :time_out, :hours_reg, :hours_ot, :employee_id)
            """,
            {
                "date": date,
                "time_in": time_in,
                "time_out": time_out,
                "hours_reg": hours_reg,
                "hours_ot": hours_ot,
                "employee_id": employee_id
            }
        )

    def _update_shift(self, employee_id: str, shift: Shift) -> None:
        """
        Update an existing shift.
        """
        date = shift.date.strftime(constants.DATE_FORMAT)
        time_in = shift.time_in.strftime(constants.TIME_FORMAT) if shift.time_in else None
        time_out = shift.time_out.strftime(constants.TIME_FORMAT) if shift.time_out else None
        hours_reg = shift.hours_reg
        hours_ot = shift.hours_ot

        self.cur.execute(
            """
            UPDATE shift SET
            date=:date,
            time_in=:time_in,
            time_out=:time_out,
            hours_reg=:hours_reg,
            hours_ot=:hours_ot
            WHERE employee_id=:employee_id
            AND date=:date
            """,
            {
                "date": date,
                "time_in": time_in,
                "time_out": time_out,
                "hours_reg": hours_reg,
                "hours_ot": hours_ot,
                "employee_id": employee_id,
            }
        )

    def print_settings(self) -> None:
        """
        Print all the records in the `settings` table. (For debugging)
        """
        for row in self.cur.execute("SELECT * FROM settings"):
            print(row)

    def print_shifts(self) -> None:
        """
        Print all records in the `shift` table. (For debugging)
        """
        for row in self.cur.execute("SELECT * FROM shift"):
            print(row)

    def print_employees(self) -> None:
        """
        Print all records in the `employees` table. (For debugging)
        """
        for row in self.cur.execute("SELECT * FROM employee"):
            print(row)

    def _table_exists(self, name: str) -> bool:
        res = self.cur.execute(
            "SELECT name FROM sqlite_master WHERE name=:name", {"name": name}
        )

        return res.fetchone() is not None

    def close(self) -> None:
        """
        Close the connection to the database. Note, this should only be done once.
        """
        self.cur.close()
        self.conn.close()
