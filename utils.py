import datetime

def next_date(curr_date: datetime.date, days: int) -> datetime.date:
    return curr_date + datetime.timedelta(days=days)
