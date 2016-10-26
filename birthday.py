import random

def birthday():
    """Return random birthdays (string, dd/mm/yyyy). Attempts to distribute birthdays realistically."""
    # Normal Distribution by default
    # See http://en.wikipedia.org/wiki/Median_age for population models
    # TODO-- sex differences
    birthyear = int(random.normalvariate(1960, 15))
    birthmonth = random.randint(1, 12)
    monthlen = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    lastdayofmonth = monthlen[birthmonth - 1]
    # take leap year into account: allow 29 days in some Febs
    if (birthmonth == 2
        and birthyear % 4 == 0
        and (birthyear % 100 != 0 or birthyear % 400 == 0)):
        lastdayofmonth = 29
    # choose day of month
    birthday = int(random.uniform(1.0, 31.0) *
                   (float(lastdayofmonth) / 31) + 1.0)
    return "{0:02d}/{1:02d}/{2:02d}".format(birthday, birthmonth, birthyear)
