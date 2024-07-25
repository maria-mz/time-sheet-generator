"""Database Dataclasses"""
from dataclasses import dataclass
import datetime

import const

@dataclass
class PayPeriod:
    """
    Pay Period settings data
    """
    start_date: datetime.datetime
    end_date: datetime.datetime

@dataclass
class Employee:
    """
    Employee table row data
    """
    employee_id: str
    full_name: str
    position: str

@dataclass
class Shift:
    """
    Shift table row data
    """
    employee_id: str
    date: datetime.date
    time_in: datetime.time = const.DEFAULT_TIME_IN
    time_out: datetime.time = const.DEFAULT_TIME_OUT
    hours_reg: int = const.DEFAULT_HOURS_REG
    hours_ot: int = const.DEFAULT_HOURS_OT
