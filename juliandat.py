#!/usr/bin/env python

import datetime

#--
# First make a datetime.datetime from 1985-02-17T06:00.
#--

dt = datetime.datetime ( 2016, 2, 22, 12, 10, 10 )
print "Input datetime:", dt

#--
# Convert to Julian Date and display.
#--
my_date=dt
def date_to_julian_day(my_date):
    """Returns the Julian day number of a date."""
a = (14 - my_date.month)//12
y = my_date.year + 4800 - a
m = my_date.month + 12*a - 3
#      return my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045

print(my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045)
