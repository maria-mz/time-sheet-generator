"""App-wide Constants"""

import datetime


PAY_PERIOD_DAYS = 14
DEFAULT_HOURS_REG = "8.00"
DEFAULT_HOURS_OT = "0.00"
DEFAULT_TIME_IN = datetime.time(hour=9) # 9 AM
DEFAULT_TIME_OUT = datetime.time(hour=17) # 5 PM

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

DB_NAME = "database.db"

APP_NAME = "Timesheet Generator"
