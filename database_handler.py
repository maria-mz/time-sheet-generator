import csv
import datetime 
import calendar
from pymongo import MongoClient

NUM_PAY_PERIOD_DAYS = 14
DEFAULT_REG = 8.00
DEFAULT_OT = 0.00
TIME_IN = "9:00 AM"
TIME_OUT = "5:00 PM"

# Delete later
year = 2023
month = 1
day = 9

class DatabaseHandler:
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')

        # Access the database and collection. If doesn't exist, will be created upon first write.
        database = client['employee_data']
        self.employees = database['employees']
    
    def read_csv(self):
        with open('test_data.csv') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the first row (header), handle options later
            next(reader)
            for row in reader:
                employee_data = {
                    "full_name": row[0],
                    "job_title": row[1],
                    "work_days": self.initialize_work_days(year, month, day)
                }
                self.employees.insert_one(employee_data)
        
    def _initialize_work_days(self, year, month, day):
        """
        Returns a list of of work days for a given pay period.
        """
        work_days = []

        date_obj = datetime.date(year, month, day)

        for i in range(NUM_PAY_PERIOD_DAYS):
            date = date_obj.strftime('%m/%d/%Y')
            day_of_week = calendar.day_name[date_obj.weekday()]
            is_weekend = day_of_week == "Saturday" or day_of_week == "Sunday"
            work_day = {
                "work_date": date,
                "day_of_week": day_of_week,
                "time_in": "" if is_weekend else TIME_IN,
                "time_out": "" if is_weekend else TIME_OUT,
                "regular_hours": 0.00 if is_weekend else DEFAULT_REG,
                "overtime_hours": DEFAULT_OT
            }
            work_days.append(work_day)

            date_obj += datetime.timedelta(days=1)
            
        return work_days
    
    def get_data(self):
        """
        Returns a list that contains each employee's information
        """
        data = []
        for document in self.employees.find():
            data.append(document)
        return data
    
    def num_entries(self):
        return self.employees.count_documents({})
    

    # For debugging purposes, delete later
    def print(self):
        for employee in self.employees.find():
            print("Full name:", employee["full_name"])
            print("Job title:", employee["job_title"])
            print("Work days:")
            for work_day in employee["work_days"]:
                print(work_day["work_date"], work_day["day_of_week"], work_day["time_in"], work_day["time_out"], work_day["regular_hours"], work_day["overtime_hours"])


