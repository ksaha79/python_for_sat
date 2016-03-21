#!/usr/bin/env python

import datetime
import math
import argparse
import numpy as np
#--
# First make a datetime.datetime from 1985-02-17T06:00.
#--

dt = datetime.datetime ( 2016, 2, 22, 12, 10, 10 )

print "Input datetime:", dt
#parser = argparse.ArgumentParser(description='')
#parser.add_argument('strings', nargs='+')
#args = parser.parse_args()
#num = len(args.strings)
#print(len(args.strings))
#print(args.strings)

#dt = (args.strings[0],args.strings[1],args.strings[2],args.strings[3],args.strings[4],args.strings[5],args.strings[6],args.strings[7] )
#print dt
#print(args.strings[num-2])

#--
# Convert to Julian Date and display.
#--
my_date=dt
#def date_to_julian_day(my_date):
#    """Returns the Julian day number of a date."""
a = (14 - my_date.month)//12
y = my_date.year + 4800 - a
m = my_date.month + 12*a - 3
# return my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
jd=my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
print(my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045)

d=jd-2451544
# Keplerian Elements for the Sun (geocentric)
w = 282.9404+4.70935e-5*d               # longitude of perihelion degrees
a = 1.000000                            # mean distance, a.u.
e = 0.016709-1.151e-9*d                 # eccentricity
M = divmod((356.0470+0.9856002585*d),360.0) # mean anomaly degrees
L = w + M[1]                               # Sun's mean longitude degrees
oblecl = 23.4393-3.563e-7*d             # Sun's obliquity of the ecliptic

print(w, a, e, M, L, oblecl)

# auxiliary angle
EE = M[1]+(180.0/math.pi)*e*math.sin(M[1]*(math.pi/180.0))*(1+e*math.cos(M[1]*(math.pi/180.0)))
print(EE)

# rectangular coordinates in the plane of the ecliptic (x axis toward perhilion)
x = math.cos(EE*(math.pi/180.0))-e;
y = math.sin(EE*(math.pi/180.0))*math.sqrt(1-math.pow(e,2.0))
print(x,y)

# find the distance and true anomaly
r = math.sqrt(math.pow(x,2.0) + math.pow(y,2.0))
v = (math.atan2(y,x))*(180.0/math.pi)
print r, v

# find the longitude of the sun
sunlon = v + w
print sunlon

# compute the ecliptic rectangular coordinates
xeclip = r*math.cos(sunlon*(math.pi/180.0))
yeclip = r*math.sin(sunlon*(math.pi/180.0))
zeclip = 0.0
print(xeclip,yeclip,zeclip)

# rotate these coordinates to equitorial rectangular coordinates
xequat = xeclip
yequat = yeclip*math.cos(oblecl*(math.pi/180.0))+zeclip*math.sin(oblecl*(math.pi/180.0))
zequat = yeclip*math.sin(23.4406*(math.pi/180.0))+zeclip*math.cos(oblecl*(math.pi/180.0))
print(xequat,yequat,zequat)

# convert equatorial rectangular coordinates to RA and Decl:
alt=0.0 #Altitude of satellite
r = math.sqrt(math.pow(xequat,2.0) + math.pow(yequat,2.0) + math.pow(zequat,2.0))-(alt/149598000.0) # roll up the altitude correction
RA = (math.atan2(yequat,xequat))*(180.0/math.pi)
delta = (math.asin(zequat/r))*(180.0/math.pi)
print(r,RA,delta)

# Find the J2000 value
#J2000 = jd - 2451545.0 #==========>>>>>> not used anywhere ??????????
# hourvec = datevec(UTC,'yyyy/mm/dd HH:MM:SS');
UTH = my_date.hour + my_date.minute/60. + my_date.second/3600.
print UTH

# Calculate local siderial time
lon=[160.0,165.0]
lat=[-45.0,-40.0]
xgms=divmod((L+180),360.0)
GMST0=xgms[1]/15
SIDTIME = GMST0 + UTH + np.array(lon)/15
#SIDTIME = [(GMST0 + UTH + lonx/15) for lonx in lon]
print(GMST0, SIDTIME)

# Replace RA with hour angle HA
HA = (np.array(SIDTIME)*15.0 - RA)
print HA
#HA = [(stx*15.0 - RA) for stx in SIDTIME]
# convert to rectangular coordinate system
x = np.cos(np.array(HA)*(math.pi/180.0))*np.cos(delta*(math.pi/180.0))
y = np.sin(np.array(HA)*(math.pi/180.0))*np.cos(delta*(math.pi/180.0))
z = math.sin(delta*(math.pi/180.0))
#x = [math.cos(hax*(math.pi/180.0))*math.cos(delta*(math.pi/180.0)) for hax in HA]
#y = [math.sin(hax*(math.pi/180.0))*math.cos(delta*(math.pi/180.0)) for hax in HA]
#z = math.sin(delta*(math.pi/180.0))

# rotate this along an axis going east-west.
xhor = x*np.cos((90.0 - np.array(lat))*(math.pi/180.0))-z*np.sin((90.0 - np.array(lat))*(math.pi/180.0))
yhor = y
zhor = x*np.sin((90.0 - np.array(lat))*(math.pi/180.0))+z*np.cos((90.0 - np.array(lat))*(math.pi/180.0))
#zhor = [(xx*math.sin((90.0 - laty)*(math.pi/180.0))+z*math.cos((90.0 - laty)*(math.pi/180.0))) for laty, xx in zip(lat,x)]
#xhor = [(x*math.cos((90.0 - ly)*(math.pi/180.0))-z*math.sin((90.0 - ly)*(math.pi/180.0))) for ly, x in zip(lat,x)]
#yhor = y;

#Find the h and AZ
El = (np.arcsin(np.array(zhor)))*(180.0/math.pi)

# Atmospheric refraction correction (in degrees)
argument = np.array(El) + (10.3/(np.array(El) + 5.11))
refraction_corr = 1.02 / (60.0 * np.tan(np.array(argument) * math.pi/180.0))

# Solar zenith angle calculated
sza =  90.0 - np.array(El) - np.array(refraction_corr) 
print 'solar zenith angle=', sza
#return sza
