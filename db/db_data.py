"""Database Dataclasses"""

from dataclasses import dataclass
from typing import Union
import datetime

import constants


@dataclass
class PayPeriod:
    """
    Pay Period settings data
    """
    start_date: datetime.datetime
    end_date: datetime.datetime


@dataclass
class Shift:
    """
    Shift table row data
    """
    date: datetime.date
    time_in: Union[datetime.time, None] = constants.DEFAULT_TIME_IN
    time_out: Union[datetime.time, None] = constants.DEFAULT_TIME_OUT
    hours_reg: str = constants.DEFAULT_HOURS_REG
    hours_ot: str = constants.DEFAULT_HOURS_OT


@dataclass
class Employee:
    """
    Employee table row data and their shifts.
    """
    employee_id: str
    first_name: str
    last_name: str
    position: str
    contract: str
    shifts: list[Shift]
