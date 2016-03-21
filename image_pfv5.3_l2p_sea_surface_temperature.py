#!/usr/bin/env python

import os
import sys
import argparse
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as image
from matplotlib.ticker import MultipleLocator, NullFormatter
from os import system
from solzen import solzen

# testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.
def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

#parser = argparse.ArgumentParser(description='')
#parser.add_argument('-i','--input', help='Input netCDF file name',required=True)
#parser.add_argument('-o','--output',help='Output png file name', required=True)
#args = parser.parse_args()

parser = argparse.ArgumentParser(description='')
parser.add_argument('strings', nargs='+')
args = parser.parse_args()
num = len(args.strings)
print(len(args.strings))
#print(args.strings[num-1], args.strings[num-2])
#print(args.strings[num-2])
array_file=np.arange(num-2)


# create figure, axes instances.
fig = plt.figure()

rgbArray = np.zeros((256,3))
rgbArray = np.loadtxt("./rgb_rainbow_white.txt") / 255
myrainbow = colors.ListedColormap(rgbArray[16:250])
myrainbow.set_over(color='gray')
myrainbow.set_under(color='white')

ax = fig.add_axes([0.05,0.15,0.9,0.78])

# open landmask dataset.
landnc = Dataset('/nodc/projects/satdata.2/Pathfinder_v53/Data_PFV53/LandMask/land_ocean_lake_river_mask_pfv53.nc')

# read landmask data. correct sst over the land.
latlm = landnc.variables['lat'][:]
lonlm = landnc.variables['lon'][:]
lmask = landnc.variables['mask'][:]
lmask = np.ma.masked_not_equal(lmask, 0)


# create Basemap instance.
# coastlines not used, so resolution set to None to skip
# continent processing (this speeds things up a bit)
m = Basemap(projection='cyl',lon_0=0, resolution='l', suppress_ticks=False)

majorLocatorX = MultipleLocator(45)
ax.xaxis.set_major_locator(majorLocatorX)
ax.xaxis.set_major_formatter(NullFormatter())

majorLocatorY = MultipleLocator(30)
ax.yaxis.set_major_locator(majorLocatorY)
ax.yaxis.set_major_formatter(NullFormatter())

# draw parallels and meridians, but don't bother labelling them.
parallels = m.drawparallels(np.array([-60, -30, 0, 30 ,60]), linewidth=0, \
                            labels=[True,True,False,False], fontsize=10)
for r in parallels:
   parallels[r][1][0].set_rotation(90)
   parallels[r][1][1].set_rotation(270)

meridians = m.drawmeridians(np.array([-135, -90, -45, 0, 45, 90, 135]), linewidth=0, \
                            labels=[False,False,True,True], fontsize=10)


for kk in array_file:
   # open dataset.
   dataset = Dataset(args.strings[kk], 'r', format ='NETCDF4')
   print(args.strings[kk])
  
   # read sst.  Will automatically create a masked array using
   # missing_value variable attribute. 'squeeze out' singleton dimensions.
   sst = dataset.variables['sea_surface_temperature'][:].squeeze() - 273.15
   sst_scale_factor = dataset.variables['sea_surface_temperature'].scale_factor
   sst_add_offset = dataset.variables['sea_surface_temperature'].add_offset
   sst_valid_min = dataset.variables['sea_surface_temperature'].valid_min
   sst_valid_max = dataset.variables['sea_surface_temperature'].valid_max
   sst_valid_min = (sst_valid_min - 273.15 + sst_add_offset) * sst_scale_factor
   sst_valid_max = (sst_valid_max - 273.15 + sst_add_offset) * sst_scale_factor
   
   # read lats and lons (representing centers of grid boxes).
##   if kk == 0:
   lats = dataset.variables['lat'][:]
   lons = dataset.variables['lon'][:]
##      print(np.shape(np.reshape(lons,988144)))
##      print(np.shape(lons))	
   qflg = dataset.variables['quality_level'][:].squeeze()
   l2pf = dataset.variables['l2p_flags'][:].squeeze()
##   else:
##      lons = np.concatenate([lons, dataset.variables['lon'][:]])
##   print(len(lons))
##   print(np.shape(lons))
##   #sst = np.ma.masked_where(qflg < 4, sst)
   sst = ma.masked_outside(sst, sst_valid_min, sst_valid_max)
   
   fn = os.path.basename(args.strings[kk])
   datetime = fn[0:14]	  
   year=int(datetime[0:4])
   month=int(datetime[4:6])
   day=int(datetime[6:8])
   hh=int(datetime[8:10])
   mm=int(datetime[10:12])
   ss=int(datetime[12:14])
   ncols=np.shape(lats)[0]
   nrows=np.shape(lats)[1]
#   solarzen = [[0+np.nan] * nrows] * ncols
   lat=np.reshape(lats,ncols*nrows)
   lon=np.reshape(lons,ncols*nrows)
#   print np.shape(lat), np.shape(lon)
   w=solzen(year, month, day, hh, mm, ss, lat, lon)
#  print(year, month, day, hh, mm, ss, w) 
   solarzen=np.reshape(w, (-1, 409))
#   print(min(solarzen), max(solarzen), np.shape(solarzen))

   if int(args.strings[num-1]) == 0:
      sst = np.ma.masked_where(solarzen > 90.0, sst)  #Nighttime data is masked here 
#      print 'its daytime' 
   else:
      sst = np.ma.masked_where(solarzen <= 90.0, sst) #Daytime data is masked here 
#      print 'its nighttime' 
   # plot sst, then ice with pcolor
   im = plt.scatter(lons, lats, c=sst, marker='.', s=0.2, \
                cmap=myrainbow, edgecolors=None, linewidth=0, \
                vmin=-5, vmax=40)

# plot land mask
jm = m.pcolormesh(lonlm,latlm,lmask,cmap=colors.ListedColormap(['silver']))

# add colorbar
cbaxes = fig.add_axes([0.1, 0.14, 0.8, 0.025])
cb = plt.colorbar(im, cax=cbaxes, orientation='horizontal')
cb.outline.set_visible(False)
cb.ax.set_xlabel(u'SST (\u00B0C)', rotation=0)
plt.setp(cb.ax.axes.get_xticklines(), visible=False)

# add a title.
fn = os.path.basename(args.strings[0])
indx = fn.find('_G_')
dattim = fn[indx+3:indx+10]
daynight = fn[indx+11:].split('-')[0]
ax.set_title("Pathfinder v5.3 L2P SST for {}-{}-{} ({})".format(fn[:4], fn[4:6], fn[6:8], fn[:14]), position=(0.5, 1.1),\
		fontsize=12)

# Read and show in the NOAA logo in the upper left corner:
#newax = fig.add_axes([0.039, 0.759, 0.08, 0.08])
#newax.imshow(image.imread('./NOAAglobe.png'))
#newax.axis('off')

plt.show()

plt.gcf().savefig(args.strings[num-2], dpi=100)

