"""
Validation functions
"""
import re

HOURS_REGEX = re.compile(r'^\d{0,2}(\.\d{0,2})?$')
TIME_REGEX = re.compile(r'^$|^(0[1-9]|1[0-2]):([0-5][0-9])\s(AM|PM)$')


def validate_hours(hours: str) -> bool:
    return bool(re.match(HOURS_REGEX, hours))

def validate_time(time: str) -> bool:
    return bool(re.match(TIME_REGEX, time))
