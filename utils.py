import os
import datetime

def next_date(curr_date: datetime.date, days: int) -> datetime.date:
    return curr_date + datetime.timedelta(days=days)

def load_file(relative_path: str) -> str:
    absolute_path = os.path.join(os.path.dirname(__file__), relative_path)
    return absolute_path
