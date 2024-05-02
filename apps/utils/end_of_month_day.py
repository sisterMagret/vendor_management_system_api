import datetime


def end_of_month_day(year, month):
    """returns the number of days in a given month"""
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    d = days_per_month[month - 1]
    if month == 2 and (year % 4 == 0 and year % 100 != 0 or year % 400 == 0):
        d = 29
    return d


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)


def get_start_and_end_date_in_range(start_date, end_date):
    begin = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    result = []
    while True:
        if begin.month == 12:
            next_month = begin.replace(year=begin.year + 1, month=1, day=1)
        else:
            next_month = begin.replace(month=begin.month + 1, day=1)
        if next_month > end:
            break
        result.append([begin.strftime("%Y-%m-%d"), last_day_of_month(begin).strftime("%Y-%m-%d")])
        begin = next_month
        if begin.month == 12:
            result.append([begin.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
    return result
