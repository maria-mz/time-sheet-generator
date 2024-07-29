"""DatabaseHandler Module for interacting with the database."""

import sqlite3
from datetime import datetime
from typing import Union

import constants
from db.db_data import PayPeriod, Employee, Shift


class EmployeeAlreadyExistsError(Exception):
    pass


class DatabaseHandler:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON;")

    def create_settings_table(self) -> None:
        """
        Create a new `settings` table if one doesn't exist already.
        """
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        self.cur.execute("INSERT INTO settings VALUES ('pay_period_start_date', NULL)")
        self.cur.execute("INSERT INTO settings VALUES ('pay_period_end_date', NULL)")

    def create_employee_table(self) -> None:
        """
        Create a new `employee` table if one doesn't exist already.
        """
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employee(
                employee_id TEXT PRIMARY KEY,
                full_name TEXT,
                position TEXT
            )
            """
        )

    def create_shift_table(self) -> None:
        """
        Create a new `shift` table if one doesn't exist already.
        """
        # TODO: Make (employee_id, date) a primary key ? basically, don't allow
        # an employee to have more than one shift per day
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS shift(
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

    def delete_settings_table(self) -> None:
        """
        Delete the `settings` table if it exists.
        """
        self.cur.execute("DROP TABLE IF EXISTS settings")

    def delete_employee_table(self) -> None:
        """
        Delete the `employee` table if it exists.
        """
        self.cur.execute("DROP TABLE IF EXISTS employee")

    def delete_shift_table(self):
        """
        Delete the `shift` table if it exists.
        """
        self.cur.execute("DROP TABLE IF EXISTS shift")

    def update_pay_period(self, pay_period: PayPeriod) -> None:
        """
        Update the setting's pay period.
        """
        self.cur.execute(
            f"UPDATE settings SET \
            value='{pay_period.start_date.strftime(constants.DATE_FORMAT)}' \
            WHERE key='pay_period_start_date'"
        )
        self.cur.execute(
            f"UPDATE settings SET \
            value='{pay_period.end_date.strftime(constants.DATE_FORMAT)}' \
            WHERE key='pay_period_end_date'"
        )

    def get_pay_period(self) -> Union[PayPeriod, None]:
        """
        Get the pay period from `settings`. If a pay period hasn't been set yet,
        returns None.
        """
        start_date = self.cur.execute(
            "SELECT value FROM settings WHERE key='pay_period_start_date'"
        ).fetchone()[0]

        end_date = self.cur.execute(
            "SELECT value FROM settings WHERE key='pay_period_end_date'"
        ).fetchone()[0]

        if start_date is None or end_date is None:
            return None

        return PayPeriod(
            start_date=datetime.strptime(start_date, constants.DATE_FORMAT).date(),
            end_date=datetime.strptime(end_date, constants.DATE_FORMAT).date()
        )

    def get_employees(self) -> list[Employee]:
        rows = self.cur.execute(f"SELECT * FROM employee ORDER BY full_name").fetchall()

        employees = []

        for row in rows:
            employee = Employee(
                employee_id=row[0],
                full_name=row[1],
                position=row[2],
            )

            shifts = self._get_shifts(employee.employee_id)
            employee.shifts = shifts

            employees.append(employee)

        return employees

    def get_employee(self, employee_id: str) -> Union[Employee, None]:
        """
        Get the employee matching the id. If no match, returns None.
        """
        row = self.cur.execute(
            f"SELECT * FROM employee WHERE employee_id='{employee_id}'"
        ).fetchone()

        if row is None:
            return None

        return Employee(
            employee_id=employee_id,
            full_name=row[1],
            position=row[2],
            shifts=self._get_shifts(employee_id)
        )

    def add_employee(self, employee: Employee) -> None:
        """
        Add a new employee. If there is already an employee with the same id,
        raises sqlite3.IntegrityError.
        """
        v = f"'{employee.employee_id}', '{employee.full_name}', '{employee.position}'"

        self.cur.execute(f"INSERT INTO employee VALUES ({v})")

        for shift in employee.shifts:
            self._add_shift(employee.employee_id, shift)

    def add_employees(self, employees: list[Employee]) -> None:
        for employee in employees:
            try:
                self.add_employee(employee)
            except sqlite3.IntegrityError:
                raise EmployeeAlreadyExistsError(
                    f"Already an employee with number '{employee.employee_id}'"
                )

    def delete_employee(self, employee_id: str) -> None:
        """
        Delete an employee. Deletes all shifts as well. If an employee with this id
        doesn't exist, delete is a no-op.
        """
        self.cur.execute(f"DELETE FROM employee WHERE employee_id='{employee_id}'")

    def update_employee(self, employee: Employee) -> None:
        """
        Update an existing employee.
        """
        self.cur.execute(
            f"UPDATE employee SET \
            full_name='{employee.full_name}', \
            position='{employee.position}' \
            WHERE employee_id='{employee.employee_id}'"
        )

        if self.cur.rowcount == 0:
            return # No employee found

        for shift in employee.shifts:
            self._update_shift(employee.employee_id, shift)

    def update_employees(self, employees: list[Employee]) -> None:
        for employee in employees:
            self.update_employee(employee)

    def _get_shifts(self, employee_id: str) -> list[Shift]:
        """
        Get all the shifts for an employee.
        """
        rows = self.cur.execute(
            f"SELECT * FROM shift \
            WHERE employee_id='{employee_id}' \
            ORDER BY date"
        ).fetchall()

        shifts = []

        for row in rows:
            shift = Shift(
                date=datetime.strptime(row[0], constants.DATE_FORMAT).date(),
                time_in=datetime.strptime(row[1], constants.TIME_FORMAT).time(),
                time_out=datetime.strptime(row[2], constants.TIME_FORMAT).time(),
                hours_reg=row[3],
                hours_ot=row[4],
            )
            shifts.append(shift)

        return shifts

    def _add_shift(self, employee_id: str, shift: Shift) -> None:
        """
        Add a new shift for an employee. If an employee with this id doesn't exist,
        raises sqlite3.IntegrityError.
        """
        v = f" \
            '{shift.date.strftime(constants.DATE_FORMAT)}', \
            '{shift.time_in.strftime(constants.TIME_FORMAT)}', \
            '{shift.time_out.strftime(constants.TIME_FORMAT)}', \
            '{shift.hours_reg}', \
            '{shift.hours_ot}', \
            '{employee_id}'"

        self.cur.execute(f"INSERT INTO shift VALUES ({v})")

    def _delete_shift(self, employee_id: str, date: datetime.date) -> None:
        """
        Delete a shift. If an employee with this id doesn't exist and/or there
        isn't a shift for this day, delete is a no-op.
        """
        self.cur.execute(
            f"DELETE FROM shift \
            WHERE employee_id='{employee_id}' \
            AND date='{date.strftime(constants.DATE_FORMAT)}'"
        )

    def _update_shift(self, employee_id: str, shift: Shift) -> None:
        """
        Update an existing shift.
        """
        self.cur.execute(
            f"UPDATE shift SET \
            date='{shift.date.strftime(constants.DATE_FORMAT)}', \
            time_in='{shift.time_in.strftime(constants.TIME_FORMAT)}', \
            time_out='{shift.time_out.strftime(constants.TIME_FORMAT)}', \
            hours_reg='{shift.hours_reg}', \
            hours_ot='{shift.hours_ot}' \
            WHERE employee_id='{employee_id}' \
            AND date='{shift.date.strftime(constants.DATE_FORMAT)}'"
        )

    def print_settings(self) -> None:
        """
        Print all the records in the `settings` table.
        """
        for row in self.cur.execute("SELECT * FROM settings"):
            print(row)

    def print_shifts(self) -> None:
        """
        Print all records in the `shift` table.
        """
        for row in self.cur.execute("SELECT * FROM shift"):
            print(row)

    def print_employees(self) -> None:
        """
        Print all records in the `employees` table.
        """
        for row in self.cur.execute("SELECT * FROM employee"):
            print(row)

    def commit(self) -> None:
        """
        Commit database changes to disk.
        """
        self.conn.commit()

    def close(self) -> None:
        """
        Close the connection to the database. Note, this can only be done once.
        """
        self.cur.close()
        self.conn.close()
