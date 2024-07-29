import sqlite3
import datetime
import pytest

from db.db_handler import DatabaseHandler
from db.db_data import PayPeriod, Employee, Shift


TEST_DB_NAME = "test_database.db"


@pytest.fixture(name="db_handler", scope="session")
def fixture_db_handler():
    db_handler = DatabaseHandler(TEST_DB_NAME)

    # Start with fresh empty tables
    db_handler.delete_shift_table()
    db_handler.delete_employee_table()
    db_handler.delete_settings_table()

    db_handler.create_employee_table()
    db_handler.create_shift_table()
    db_handler.create_settings_table()

    yield db_handler

    db_handler.close()


def test_get_pay_period_initial(db_handler: DatabaseHandler):
    """Verify that pay period dates are null when table is created"""

    pay_period = db_handler.get_pay_period()
    assert pay_period is None


def test_update_pay_period(db_handler: DatabaseHandler):
    """Test updating the pay period"""

    pay_period = PayPeriod(
        start_date=datetime.date(year=2024, month=7, day=1),
        end_date=datetime.date(year=2024, month=7, day=14)
    )

    db_handler.update_pay_period(pay_period)

    actual_pay_period = db_handler.get_pay_period()
    assert actual_pay_period == pay_period


def test_add_employee__success(db_handler: DatabaseHandler):
    """Test adding an employee"""

    employee = Employee(
        employee_id="1",
        full_name="Charlie Brown",
        position="Teacher",
        shifts=[]
    )

    db_handler.add_employee(employee)

    assert db_handler.get_employee("1") == employee


def test_add_employee__duplicate(db_handler: DatabaseHandler):
    """Test adding an employee with the same employee_id"""

    employee2 = Employee(
        employee_id="1",
        full_name="Franklin",
        position="Architect",
        shifts=[]
    )

    with pytest.raises(sqlite3.IntegrityError):
        db_handler.add_employee(employee2)


def test_update_employee(db_handler: DatabaseHandler):
    """Test updating the field of an employee"""

    employee = db_handler.get_employee("1")
    employee.position = "Writer"

    db_handler.update_employee(employee)

    assert db_handler.get_employee(employee.employee_id) == employee


def test_add_shifts__success(db_handler: DatabaseHandler):
    """
    Test adding some shifts for an existing employee.
    Also verifies that shifts are returned in ascending order.
    """

    shifts = [
        # Intentionally out of order
        Shift(
            date=datetime.date(year=2024, month=7, day=22),
        ),
        Shift(
            date=datetime.date(year=2024, month=7, day=20),
            time_out=datetime.time(hour=19),
            hours_ot="2.00"
        )
    ]

    for shift in shifts:
        db_handler._add_shift("1", shift)

    actual_shifts = db_handler._get_shifts("1")

    # Handler's result should be in order
    assert actual_shifts[0] == shifts[1]
    assert actual_shifts[1] == shifts[0]


def test_add_shift__no_employee(db_handler: DatabaseHandler):
    """Test adding a shifts for an employee that doesn't exist"""

    shift = Shift(
        date=datetime.date(year=2024, month=7, day=22),
    )

    with pytest.raises(sqlite3.IntegrityError):
        db_handler._add_shift("5", shift)


def test_update_shift(db_handler: DatabaseHandler):
    """Test updating an existing shift"""

    shift = Shift(
        date=datetime.date(year=2024, month=7, day=20),
        time_out=datetime.time(hour=12),
        hours_reg="3.00"
    )

    db_handler._update_shift("1", shift)

    actual_shift = db_handler._get_shifts("1")[0]
    assert actual_shift == shift


def test_update_shift__no_change(db_handler: DatabaseHandler):
    """Test updating a shift that doesn't exist"""

    # This shift doesn't exist. Changes in update will only be made
    # to existing shifts which occur on some day
    shift = Shift(
        date=datetime.date(year=2025, month=1, day=1),
    )

    db_handler._update_shift("1", shift)

    assert len(db_handler._get_shifts("1")) == 2 # at this time should still be 2 shifts
    # TODO: check contents of shifts are the same


def test_delete_shift(db_handler: DatabaseHandler):
    """Test deleting an existing shift"""

    db_handler._delete_shift("1", datetime.date(year=2024, month=7, day=20))

    assert len(db_handler._get_shifts("1")) == 1


def test_delete_employee(db_handler: DatabaseHandler):
    """Test deleting an employee - should delete their shifts too"""

    db_handler.delete_employee("1")

    assert db_handler.get_employee("1") is None
    assert db_handler._get_shifts("1") == []

# TODO: Write more tests, compare updating vs adding
