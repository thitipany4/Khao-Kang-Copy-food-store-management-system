import datetime
from dateutil import relativedelta, rrule  

def get_quarter(month):
    if month in range(1, 4):
        return 1
    elif month in range(4, 7):
        return 2
    elif month in range(7, 10):
        return 3
    elif month in range(10, 13):
        return 4

def get_month_dates(year, quarter):
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    start_date = datetime.datetime(year, start_month, 1)
    end_date = datetime.datetime(year, end_month, 1) + relativedelta.relativedelta(day=31)
    return start_date, end_date

def get_list_quarter(quarter):
    if quarter == 1:
        len_quarter = [1,2,3]
    elif quarter == 2:
        len_quarter = [4,5,6]
    elif quarter == 3:
        len_quarter = [7,8,9]
    elif quarter == 4:
        len_quarter = [10,11,12]
    return len_quarter

