"""App-wide Constants"""
import datetime
import utils

PAY_PERIOD_DAYS = 14
DEFAULT_HOURS_REG = "8.00"
DEFAULT_HOURS_OT = "0.00"
DEFAULT_HOURS_WEEKEND = "0.00"
DEFAULT_TIME_IN = datetime.time(hour=9) # 9 AM
DEFAULT_TIME_OUT = datetime.time(hour=17) # 5 PM

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

DB_PATH = utils.load_file("assets/database.db")

APP_NAME = "Timesheet Generator"
COMPANY_NAME = "Company Name"

VERSION = "0.1.0"
