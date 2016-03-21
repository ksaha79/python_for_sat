#!/usr/bin/env python

import os
import sys
import argparse
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use("AGG")
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator, NullFormatter

parser = argparse.ArgumentParser(description='')
parser.add_argument('-i','--input', help='Input netCDF file name',required=True)
parser.add_argument('-o','--output',help='Output png file name', required=True)
args = parser.parse_args()

# open dataset.
dataset = Dataset(args.input, 'r', format='NETCDF4')

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
lats = dataset.variables['lat'][:]
lons = dataset.variables['lon'][:]

lons2, lats2 = np.meshgrid(lons,lats)

sst = ma.masked_outside(sst, sst_valid_min, sst_valid_max)

# create figure, axes instances.
fig = plt.figure()

#rgbArray = np.zeros((256,3))
#rgbArray = np.loadtxt("./rgb_rainbow_white.txt") / 255 
#myrainbow = colors.ListedColormap(rgbArray[16:255])
#myrainbow.set_over(color='gray')
#myrainbow.set_under(color='white')

rgbArray = np.zeros((256,3))
rgbArray = np.loadtxt("./rgb_ghrsst_col.txt") / 255
ghrsst_col = colors.ListedColormap(rgbArray[:])
ghrsst_col.set_over(color='gray')
ghrsst_col.set_under(color='white')

ax = fig.add_axes([0.05,0.15,0.9,0.78])

# create Basemap instance.
# coastlines not used, so resolution set to None to skip
# continent processing (this speeds things up a bit)
m = Basemap(projection='cyl',lon_0=0, resolution='l')
majorLocatorX = MultipleLocator(45)
ax.xaxis.set_major_locator(majorLocatorX)
ax.xaxis.set_major_formatter(NullFormatter())

majorLocatorY = MultipleLocator(30)
ax.yaxis.set_major_locator(majorLocatorY)
ax.yaxis.set_major_formatter(NullFormatter())

#m.drawcoastlines()
m.fillcontinents(color = 'darkgray') # blue can be changed to any color that you would like

## draw invisible parallels and meridians just for keeping the frame
#m.drawparallels(np.arange(-60,61,30), linewidth=0, \
#                            labels=[False,False,False,False])
#
#m.drawmeridians(np.arange(-135,136,45), linewidth=0, \
#                labels=[False,False,False,False])
#

# draw parallels and meridians, but don't bother labelling them.
parallels = m.drawparallels(np.array([-60, -30, 0, 30 ,60]), linewidth=0, \
                            labels=[True,True,False,False], fontsize=10)
for r in parallels:
   parallels[r][1][0].set_rotation(90)
   parallels[r][1][1].set_rotation(270)

meridians = m.drawmeridians(np.array([-135, -90, -45, 0, 45, 90, 135]), linewidth=0, \
                            labels=[False,False,True,True], fontsize=10)

# plot sst, then ice with pcolor
im = plt.scatter(lons2, lats2, c=sst, marker='.', s=0.2, \
                cmap=ghrsst_col, edgecolors=None, linewidth=0, \
                vmin=-5, vmax=40)

# add colorbar
cbaxes = fig.add_axes([0.1, 0.14, 0.8, 0.025]) 
cb = plt.colorbar(im, cax=cbaxes, orientation='horizontal')
cb.outline.set_visible(False)
cb.ax.set_xlabel(u'SST (\u00B0C)', rotation=0)
plt.setp(cb.ax.axes.get_xticklines(), visible=False)

# add a title.
fn = os.path.basename(args.input)
indx = fn.find('_G_')
dattim = fn[indx+3:indx+10]
daynight = fn[indx+11:].split('-')[0]
ax.set_title("L3C sea_surface_temperature for {} ({})".format(dattim, daynight), \
             position=(0.5, 1.1), fontsize=12)

plt.show()

plt.gcf().savefig(args.output, dpi=100)

