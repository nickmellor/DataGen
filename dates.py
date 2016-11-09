import random


def birthday():
    """Return random birthdays (string, dd/mm/yyyy). Attempts to distribute birthdays realistically."""
    # Normal Distribution by default
    # See http://en.wikipedia.org/wiki/Median_age for population models
    # TODO-- sex differences
    year = int(random.normalvariate(1960, 15))
    month = random.randint(1, 12)
    monthdays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    # lists are 0-indexed but months are 1-indexed
    lastdayofmonth = monthdays[month - 1]
    # take leap year into account: allow 29 days in some Febs
    if (month == 2
        and year % 4 == 0
        and (year % 100 != 0 or year % 400 == 0)):
        lastdayofmonth = 29
    # choose day of month
    day = int(random.uniform(1.0, 31.0) * (float(lastdayofmonth) / 31) + 1.0)
    return date_fields('dob', day, month, year)


def date_fields(name, day, month, year):
    return {
        name: "{0:02d}/{1:02d}/{2:02d}".format(day, month, year),
        name + '_day': str(day),
        name + '_month': str(month),
        name + '_year': str(year)
    }

