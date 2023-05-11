import csv
import datetime 
import calendar
from pymongo import MongoClient

NUM_PAY_PERIOD_DAYS = 14
DEFAULT_REG = 8.00
DEFAULT_OT = 0.00
TIME_IN = '9:00 AM'
TIME_OUT = '5:00 PM'

class DatabaseHandler:
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')

        # Access the database and collections. If doesn't exist, will be created upon first write.
        database = client['employee_data']
        self.employees = database['employees']
        self.start_date = database['start_date']
    
    def read_csv(self):
        """
        Reads data from a CSV file and initializes the employee collection with the data. The method expects a start date to have been set using "set_start_date" method. Each row in the CSV file is expected to contain employee data in the following order: full name, job title. 

        Returns:
            int: 0 on success, 1 on failure to find a start date
        """
        if not self.has_start_date():
            return 1
        
        self.employees.delete_many({})
        year, month, day = self.get_start_date()
        default_work_days = self._initialize_work_days(year, month, day)
        employee_list = []

        with open('test_data.csv') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the first row (header), handle options later
            next(reader)
            
            for row in reader:
                employee_data = {
                    "full_name": row[0],
                    "job_title": row[1],
                    "work_days": default_work_days
                }
                employee_list.append(employee_data)
            
        if employee_list:
            self.employees.insert_many(employee_list)

        return 0
        
    def _initialize_work_days(self, year, month, day):
        """
        Populates a list with default data for each work day in the pay period

        Parameters:
            year (int): the year of the start date.
            month (int): the month of the start date.
            day (int): the day of the start date.

        Returns:
            A list of dictionaries, where each dictionary represents a work day
        """
        work_days = []

        date_obj = datetime.date(year, month, day)

        for i in range(NUM_PAY_PERIOD_DAYS):
            date = date_obj.strftime('%m/%d/%Y')
            day_of_week = calendar.day_name[date_obj.weekday()]
            is_weekend = day_of_week == calendar.SATURDAY or day_of_week == calendar.SUNDAY
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
    
    def get_all_employees(self):
        """
        Retrieve all employee data from the database.

        Returns:
            A list of dictionaries, where each dictionary represents one employee record
            in the database.
        """
        return list(self.employees.find())
    
    def get_employee(self, name):
        """
        Retrive an employee's information

        Parameters:
            name (str): The full name of the employee

        Returns:
            A single dictionary representing the employee record matching the provided name.
            None if no match is found
        """
        return self.employees.find_one({"full_name": name})
    
    def set_date_and_reset(self, year, month, day):
        """
        Sets the start date for the payroll system. 
        Updates the employee data to reflect the new pay period

        Parameters:
            year (int): the year of the start date.
            month (int): the month of the start date.
            day (int): the day of the start date.
        """
        self.start_date.delete_many({})

        date = {
            "year": year,
            "month": month,
            "day": day
        }

        self.start_date.insert_one(date)
        self._reset_employee_data()

    def _reset_employee_data(self):
        """
        Updates the "work_days" key for each employee based on the start date.
        """
        year, month, day = self.get_start_date()
        new_work_days = self._initialize_work_days(year, month, day)
        self.employees.update_many({}, {'$set': {'work_days': new_work_days}})

    def get_start_date(self):
        """
        Returns a tuple containing the year, month, day of the start date 
        """
        data = self.start_date.find()[0]
        return (data['year'], data['month'], data['day'])
    
    def has_start_date(self):
        return self.start_date.count_documents({})

    
    # For debugging purposes, delete later
    def print(self):
        for employee in self.employees.find():
            print("Full name:", employee["full_name"])
            print("Job title:", employee["job_title"])
            print("Work days:")
            for work_day in employee["work_days"]:
                print(work_day["work_date"], work_day["day_of_week"], work_day["time_in"], work_day["time_out"], work_day["regular_hours"], work_day["overtime_hours"])

