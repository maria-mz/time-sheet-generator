import os
import datetime

def next_date(curr_date: datetime.date, days: int) -> datetime.date:
    return curr_date + datetime.timedelta(days=days)

def str_to_date(date: str, format: str) -> datetime.date:
    return datetime.datetime.strptime(date, format).date()

def str_to_time(time: str, format: str) -> datetime.date:
    return datetime.datetime.strptime(time, format).time()

def load_file(relative_path: str) -> str:
    absolute_path = os.path.join(os.path.dirname(__file__), relative_path)
    return absolute_path
