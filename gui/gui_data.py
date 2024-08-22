from dataclasses import dataclass

@dataclass
class PayPeriodText:
    """
    Pay period details
    """
    start_date: str
    end_date: str


@dataclass
class ShiftText:
    """
    Shift details
    """
    date: str
    time_in: str
    time_out: str
    hours_reg: str
    hours_ot: str


@dataclass
class EmployeeText:
    """
    Employee details and their shifts
    """
    employee_id: str
    first_name: str
    last_name: str
    position: str
    contract: str
    shifts: list[ShiftText]
