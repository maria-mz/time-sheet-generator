import csv
import datetime 
import calendar
from pymongo import MongoClient

NUM_PAY_PERIOD_DAYS = 14
DEFAULT_REG = 8
DEFAULT_OT = 0
TIME_IN = "9:00 AM"
TIME_OUT = "5:00 PM"

client = MongoClient('mongodb://localhost:27017/')

# Access the database and collection. If doesn't exist, will be created upon first write.
database = client['employee_data']
employees = database['employees']

# For now, clear the database first
employees.delete_many({})

def initialize_work_days(year, month, day):
    """
    Returns a list of of work days for a given pay period.
    """
    work_days = []

    date_obj = datetime.date(year, month, day)

    for i in range(NUM_PAY_PERIOD_DAYS):
        date = date_obj.strftime('%Y-%m-%d')
        day_of_week = calendar.day_name[date_obj.weekday()]

        work_day = {"work_date": date, "day_of_week": day_of_week, "time_in": TIME_IN, "time_out": TIME_OUT, "regular_hours": DEFAULT_REG, "overtime_hours": DEFAULT_OT}
        work_days.append(work_day)

        date_obj += datetime.timedelta(days=1)
        
    return work_days


year = 2023
month = 5
day = 6

# Read the CSV file
with open('test_data.csv') as csvfile:
    reader = csv.reader(csvfile)

    # Skip the first row (header)
    next(reader)
    for row in reader:
        employee_data = {
            "full_name": row[0],
            "job_title": row[1],
            "work_days": initialize_work_days(year, month, day)
        }
        employees.insert_one(employee_data)
        

# Printing the number of employees
num_employees = employees.count_documents({})
print(f'There are {num_employees} employees in the database.')

# Printing out each employee's details
for employee in employees.find():
    print("Full name:", employee["full_name"])
    print("Job title:", employee["job_title"])
    print("Work days:")
    for work_day in employee["work_days"]:
        print(work_day["work_date"], work_day["day_of_week"], work_day["time_in"], work_day["time_out"], work_day["regular_hours"], work_day["overtime_hours"])
        

