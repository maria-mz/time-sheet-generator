import sqlite3
import datetime
import pytest

from db.db_handler import DatabaseHandler, DuplicateEmployeeID
from db.db_data import PayPeriod, Employee, Shift


@pytest.fixture(name="db_handler")
def fixture_db_handler():
    db_handler = DatabaseHandler(db=":memory:") # RAM database

    # Init all tables
    db_handler.create_employee_table()
    db_handler.create_settings_table()
    db_handler.create_shift_table()

    yield db_handler

    db_handler.close()

@pytest.fixture(name="employee")
def fixture_employee():
    employee = Employee(
        employee_id="1",
        first_name="Alissa",
        last_name="Rivers",
        position="Ornithologist",
        contract="Full-time",
        shifts=[]
    )
    return employee

def test_get_pay_period_initial(db_handler: DatabaseHandler):
    pay_period = db_handler.get_pay_period()
    assert pay_period is None


def test_update_pay_period(db_handler: DatabaseHandler):
    pay_period = PayPeriod(
        start_date=datetime.date(year=2024, month=7, day=1),
        end_date=datetime.date(year=2024, month=7, day=14)
    )

    db_handler.update_pay_period(pay_period)

    actual_pay_period = db_handler.get_pay_period()
    assert actual_pay_period == pay_period


def test_add_employee__success(db_handler: DatabaseHandler, employee: Employee):
    db_handler.add_employee(employee)
    assert db_handler.get_employee(employee.employee_id) == employee


def test_add_employee__duplicate(db_handler: DatabaseHandler, employee: Employee):
    db_handler.add_employee(employee)

    with pytest.raises(DuplicateEmployeeID):
        db_handler.add_employee(employee)


def test_update_employee(db_handler: DatabaseHandler, employee: Employee):
    db_handler.add_employee(employee)
    employee.position = "Wildlife Biologist"

    db_handler.update_employee(employee)

    assert db_handler.get_employee(employee.employee_id) == employee


def test_add_shifts__success(db_handler: DatabaseHandler, employee: Employee):
    """
    Test adding some shifts for an existing employee.
    Also verifies that shifts are returned in ascending order.
    """
    db_handler.add_employee(employee)

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
        db_handler._add_shift(employee.employee_id, shift)

    actual_shifts = db_handler._get_shifts(employee.employee_id)

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


def test_update_shift(db_handler: DatabaseHandler, employee: Employee):
    """Test updating an existing shift"""

    db_handler.add_employee(employee)

    shift = Shift(
        date=datetime.date(year=2024, month=7, day=20),
        time_out=datetime.time(hour=12),
        hours_reg="3.00"
    )
    db_handler._add_shift(employee.employee_id, shift)

    shift.hours_reg = "8.00"

    db_handler._update_shift(employee.employee_id, shift)

    actual_shift = db_handler._get_shifts(employee.employee_id)[0]
    assert actual_shift == shift


def test_update_shift__no_change(db_handler: DatabaseHandler, employee: Employee):
    """Test updating a shift that doesn't exist"""

    db_handler.add_employee(employee)

    shift = Shift(
        date=datetime.date(year=2024, month=7, day=20),
        time_out=datetime.time(hour=12),
    )
    db_handler._add_shift(employee.employee_id, shift)

    # This shift doesn't exist. Changes in update will only be made
    # to existing shifts which occur on some day
    shift2 = Shift(
        date=datetime.date(year=2025, month=1, day=1),
    )

    db_handler._update_shift(employee.employee_id, shift2)

    assert len(db_handler._get_shifts(employee.employee_id)) == 1


def test_delete_employee(db_handler: DatabaseHandler,  employee: Employee):
    """Test deleting an employee - should delete their shifts too"""

    db_handler.add_employee(employee)

    shift = Shift(
        date=datetime.date(year=2024, month=7, day=20),
        time_out=datetime.time(hour=12),
    )
    db_handler._add_shift(employee.employee_id, shift)

    db_handler.delete_employee(employee.employee_id)

    assert db_handler.get_employee(employee.employee_id) is None
    assert db_handler._get_shifts(employee.employee_id) == []
