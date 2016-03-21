import datetime
import math
import argparse
import numpy as np
def solzen(year, month, day, hh, mm, ss, lat, lon):
#    print( year, month, day, hh, mm, ss, lat, lon )
    dt = datetime.datetime (year, month, day, hh, mm, ss)
    
    #--
    # Convert to Julian Date and display.
    #--

    my_date=dt
#    print '===>',my_date
#    def date_to_julian_day(my_date):
#    """Returns the Julian day number of a date."""
    a = (14 - my_date.month)//12
    y = my_date.year + 4800 - a
    m = my_date.month + 12*a - 3
    # return my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
    jd=my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
#    print(my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045)
    d=jd-2451544

    # Keplerian Elements for the Sun (geocentric)
    w = 282.9404+4.70935e-5*d               # longitude of perihelion degrees
    a = 1.000000                            # mean distance, a.u.
    e = 0.016709-1.151e-9*d                 # eccentricity
    M = divmod((356.0470+0.9856002585*d),360.0) # mean anomaly degrees
    L = w + M[1]                               # Sun's mean longitude degrees
    oblecl = 23.4393-3.563e-7*d             # Sun's obliquity of the ecliptic
#    print(w, a, e, M, L, oblecl)

    # auxiliary angle
    EE = M[1]+(180.0/math.pi)*e*math.sin(M[1]*(math.pi/180.0))*(1+e*math.cos(M[1]*(math.pi/180.0)))
#    print(EE)

    # rectangular coordinates in the plane of the ecliptic (x axis toward perhilion)
    x = math.cos(EE*(math.pi/180.0))-e;
    y = math.sin(EE*(math.pi/180.0))*math.sqrt(1-math.pow(e,2.0))
#    print(x,y)

    # find the distance and true anomaly
    r = math.sqrt(math.pow(x,2.0) + math.pow(y,2.0))
    v = (math.atan2(y,x))*(180.0/math.pi)
#    print r, v

    # find the longitude of the sun
    sunlon = v + w
#    print sunlon

    # compute the ecliptic rectangular coordinates
    xeclip = r*math.cos(sunlon*(math.pi/180.0))
    yeclip = r*math.sin(sunlon*(math.pi/180.0))
    zeclip = 0.0
#    print(xeclip,yeclip,zeclip)

    # rotate these coordinates to equitorial rectangular coordinates
    xequat = xeclip
    yequat = yeclip*math.cos(oblecl*(math.pi/180.0))+zeclip*math.sin(oblecl*(math.pi/180.0))
    zequat = yeclip*math.sin(23.4406*(math.pi/180.0))+zeclip*math.cos(oblecl*(math.pi/180.0))
#    print(xequat,yequat,zequat)
    
    # convert equatorial rectangular coordinates to RA and Decl:
    alt=0.0 #Altitude of satellite
    r = math.sqrt(math.pow(xequat,2.0) + math.pow(yequat,2.0) + math.pow(zequat,2.0))-(alt/149598000.0) # roll up the altitude correction
    RA = (math.atan2(yequat,xequat))*(180.0/math.pi)
    delta = (math.asin(zequat/r))*(180.0/math.pi)
#    print(r,RA,delta)
    
    # Find the UTH value
    UTH = my_date.hour + my_date.minute/60. + my_date.second/3600.
#    print UTH    

    # Calculate local siderial time
    xgms=divmod((L+180),360.0)
    GMST0=xgms[1]/15
    SIDTIME = GMST0 + UTH + np.array(lon)/15
#    print(GMST0, SIDTIME)

    #Replace RA with hour angle HA
    HA = np.array(SIDTIME)*15.0 - RA
#    print HA

    #convert to rectangular coordinate system
    x = np.cos(np.array(HA)*(math.pi/180.0))*np.cos(delta*(math.pi/180.0))
    y = np.sin(np.array(HA)*(math.pi/180.0))*np.cos(delta*(math.pi/180.0))
    z = math.sin(delta*(math.pi/180.0))
    
    # rotate this along an axis going east-west.
    xhor = x*np.cos((90.0 - np.array(lat))*(math.pi/180.0))-z*np.sin((90.0 - np.array(lat))*(math.pi/180.0))
    yhor = y
    zhor = x*np.sin((90.0 - np.array(lat))*(math.pi/180.0))+z*np.cos((90.0 - np.array(lat))*(math.pi/180.0))
    #Find the h and AZ
    #Az = (math.atan2(yhor,xhor))*(180.0/math.pi) + 180.0;     (not used ????)
    El = (np.arcsin(np.array(zhor)))*(180.0/math.pi)
    # Atmospheric refraction correction (in degrees)
    argument = np.array(El) + (10.3/(np.array(El) + 5.11)) 
    refraction_corr = 1.02 / (60.0 * np.tan(np.array(argument) * math.pi/180.0))

    # Solar zenith angle calculated
    sza =  90.0 - np.array(El) - np.array(refraction_corr)
#    print sza



    return sza
