#!/usr/bin/env python
import sys
print(sys.path)
from solzen import solzen 

year=1985
month=1
day=10
hh=6
mm=12
ss=55
lat=-35
lon=139
#print(average([year,month,day,hh,mm,ss]))
w=solzen(year, month, day, hh, mm, ss, lat, lon)
print w
#print(solzen([year,month,day,hh,mm,ss]))
