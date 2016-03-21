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
#read the required FLAGS
qflg = dataset.variables['quality_level'][:].squeeze()

#lons2, lats2 = np.meshgrid(lons,lats)
#sst = ma.masked_where(qflg < 4, sst)
sst = ma.masked_outside(sst, sst_valid_min, sst_valid_max)

# create figure, axes instances.
fig = plt.figure()

rgbArray = np.zeros((256,3))
rgbArray = np.loadtxt("./rgb_ghrsst_col.txt") / 255
ghrsst_col = colors.ListedColormap(rgbArray[:])
ghrsst_col.set_over(color='gray')
ghrsst_col.set_under(color='white')
ax = fig.add_axes([0.05,0.15,0.9,0.78])

# create Basemap instance.
# coastlines not used, so resolution set to None to skip
# continent processing (this speeds things up a bit)
m = Basemap(projection='ortho',lon_0=0, lat_0=0, resolution='l')
x1,y1=m(lons,lats)
#m.drawcoastlines()
m.fillcontinents(color = '#777575') # blue can be changed to any color that you would like

# draw parallels and meridians 
m.drawparallels(np.arange(-90.,90.,30.), linewidth=1, fontsize=5)
#                            labels=[False,True,True,False])
#
m.drawmeridians(np.arange(0.,360.,30.), linewidth=1, fontsize=5)
#                labels=[True,False,False,True])
#
m.drawmapboundary()
# plot sst, then ice with pcolor
#im = plt.scatter(lons, lats, c=sst, marker='.', s=0.2, \
#                cmap=ghrsst_col, edgecolors=None, linewidth=0, \
#                vmin=-5, vmax=40)
meridian=np.arange(-180.,180.,30.)
parallels=np.arange(-90.,90.,30.)

for i in np.arange(len(meridian)):
    plt.annotate(np.str(meridian[i]),xy=m(meridian[i],0),xycoords='data', fontsize=8)
for i in np.arange(len(parallels)):
    plt.annotate(np.str(parallels[i]),xy=m(0,parallels[i]),xycoords='data', fontsize=8)

im = plt.scatter(x1, y1, c=sst, marker='.', s=0.2, \
                cmap=ghrsst_col, edgecolors=None, linewidth=0, \
                vmin=-5, vmax=40)
# add a title.
fn = os.path.basename(args.input)
indx = fn.find('_G_')
dattim = fn[indx+3:indx+10]
daynight = fn[indx+9:].split('-')[0]
plt.title("MSG03 L2P sea_surface_temperature for {} ({})".format(dattim, daynight),fontsize=12)
#ax.text(0.8,0.15,"QF>3",fontsize=10)
ax.text(0.8,0.15,"all QF",fontsize=10)

# add colorbar
cbaxes = fig.add_axes([0.85, 0.25, 0.015, 0.6])  #rect [left, bottom, width, height]  
cb = plt.colorbar(im, cax=cbaxes, orientation='vertical')
cb.outline.set_visible(False)
cb.ax.set_ylabel(u'SST (\u00B0C)', rotation=90)
plt.setp(cb.ax.axes.get_xticklines(), visible=False)

# add a title.
#fn = os.path.basename(args.input)
#indx = fn.find('_G_')
#dattim = fn[indx+3:indx+10]
#daynight = fn[indx+9:].split('-')[0]
#ax.set_title("MSG03 L2P sea_surface_temperature for {} ({})".format(dattim, daynight), \
#             position=(0.5, 1.1), fontsize=12)

fig=plt.gcf()
plt.show()

fig.savefig(args.output, dpi=100)

