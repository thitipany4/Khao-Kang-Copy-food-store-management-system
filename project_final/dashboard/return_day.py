import calendar

def days_in_month(year, month):
    # Get the number of days in the given month
    num_days = calendar.monthrange(year, month)[1]
    
    # Generate a list of all days in the month
    days_list = [day for day in range(1, num_days + 1)]
    
    return days_list

# Example usage:
