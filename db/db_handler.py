import sqlite3
from datetime import datetime
from typing import Union

import const
from db_data import PayPeriod, Employee, Shift

# TODO: Maybe split up into table
class DatabaseHandler:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON;")

    # -- USER SETTINGS TABLE

    def create_settings_table(self):
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

        self.conn.commit()

    def delete_settings_table(self):
        self.cur.execute("DROP TABLE IF EXISTS settings")
        self.conn.commit()

    def update_pay_period(self, pay_period: PayPeriod):
        self.cur.execute(
            f"UPDATE settings SET \
            value='{pay_period.start_date.strftime(const.DATE_FORMAT)}' \
            WHERE key='pay_period_start_date'"
        )
        self.cur.execute(
            f"UPDATE settings SET \
            value='{pay_period.end_date.strftime(const.DATE_FORMAT)}' \
            WHERE key='pay_period_end_date'"
        )

        self.conn.commit()

    def print_settings(self):
        for row in self.cur.execute("SELECT * FROM settings"):
            print(row)

    def get_pay_period(self) -> Union[PayPeriod, None]:
        res = self.cur.execute("SELECT value FROM settings WHERE key='pay_period_start_date'")

        start_date = res.fetchone()[0]
        if start_date is None:
            return None

        res = self.cur.execute("SELECT value FROM settings WHERE key='pay_period_end_date'")

        end_date = res.fetchone()[0]
        if end_date is None:
            return None

        return PayPeriod(
            start_date=datetime.strptime(start_date, const.DATE_FORMAT).date(),
            end_date=datetime.strptime(end_date, const.DATE_FORMAT).date()
        )

    # -- EMPLOYEE TABLE

    def create_employee_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employee(
                employee_id TEXT PRIMARY KEY,
                full_name TEXT,
                position TEXT
            )
            """
        )
        self.conn.commit()

    def delete_employee_table(self):
        self.cur.execute("DROP TABLE IF EXISTS employee")
        self.conn.commit()

    def get_employee(self, employee_id: str) -> Union[Employee, None]:
        res = self.cur.execute(f"SELECT * FROM employee WHERE employee_id='{employee_id}'")

        row = res.fetchone()
        if row is None:
            return None

        return Employee(
            employee_id=employee_id,
            full_name=row[1],
            position=row[2],
        )

    def add_employee(self, employee: Employee):
        v = f"'{employee.employee_id}', '{employee.full_name}', '{employee.position}'"

        self.cur.execute(f"INSERT INTO employee VALUES ({v})")
        self.conn.commit()

    def delete_employee(self, employee_id: str):
        self.cur.execute(f"DELETE FROM employee WHERE employee_id='{employee_id}'")
        self.conn.commit()

    def update_employee(self, employee: Employee):
        self.cur.execute(
            f"UPDATE employee SET \
            full_name='{employee.full_name}', \
            position='{employee.position}' \
            WHERE employee_id='{employee.employee_id}'"
        )
        self.conn.commit()

    def print_employees(self):
        for row in self.cur.execute("SELECT * FROM employee"):
            print(row)

    # -- SHIFT TABLE

    def create_shift_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS shift(
                date TEXT,
                time_in TEXT,
                time_out TEXT,
                hours_reg INTEGER,
                hours_ot INTEGER,
                employee_id TEXT REFERENCES employee(employee_id)
                ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    def delete_shift_table(self):
        self.cur.execute("DROP TABLE IF EXISTS shift")
        self.conn.commit()

    def get_shifts(self, employee_id: str) -> list[Shift]:
        res = self.cur.execute(
            f"SELECT * FROM shift \
            WHERE employee_id='{employee_id}' \
            ORDER BY date"
        )

        rows = res.fetchall()

        shifts = []

        for row in rows:
            shift = Shift(
                employee_id=row[5],
                date=datetime.strptime(row[0], const.DATE_FORMAT).date(),
                time_in=datetime.strptime(row[1], const.TIME_FORMAT).time(),
                time_out=datetime.strptime(row[2], const.TIME_FORMAT).time(),
                hours_reg=row[3],
                hours_ot=row[4],
            )
            shifts.append(shift)

        return shifts

    def add_shift(self, shift: Shift):
        v = f" \
            '{shift.date.strftime(const.DATE_FORMAT)}', \
            '{shift.time_in.strftime(const.TIME_FORMAT)}', \
            '{shift.time_out.strftime(const.TIME_FORMAT)}', \
            '{shift.hours_reg}', \
            '{shift.hours_ot}', \
            '{shift.employee_id}'"

        self.cur.execute(f"INSERT INTO shift VALUES ({v})")
        self.conn.commit()

    def delete_shift(self, employee_id: str, date: datetime.date):
        self.cur.execute(
            f"DELETE FROM shift \
            WHERE employee_id='{employee_id}' \
            AND date='{date.strftime(const.DATE_FORMAT)}'"
        )
        self.conn.commit()

    def update_shift(self, shift: Shift):
        self.cur.execute(
            f"UPDATE shift SET \
            date='{shift.date.strftime(const.DATE_FORMAT)}', \
            time_in='{shift.time_in.strftime(const.TIME_FORMAT)}', \
            time_out='{shift.time_out.strftime(const.TIME_FORMAT)}', \
            hours_reg='{shift.hours_reg}', \
            hours_ot='{shift.hours_ot}' \
            WHERE employee_id='{shift.employee_id}' \
            AND date='{shift.date.strftime(const.DATE_FORMAT)}'"
        )
        self.conn.commit()

    def print_shifts(self):
        for row in self.cur.execute("SELECT * FROM shift"):
            print(row)

    def close(self):
        self.cur.close()
        self.conn.close()
