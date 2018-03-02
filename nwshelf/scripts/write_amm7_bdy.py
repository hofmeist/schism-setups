import os
from pylab import *
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import *
import numpy as np
import netCDF4
import netcdftime
from mpl_toolkits.basemap import interp as bminterp
from scipy.spatial import KDTree

class bdy_dataset():

  def __init__(self,filename='2012-01.amm7.nc'):
    self.filename=filename
    self.nc = netCDF4.MFDataset(filename)
    self.ncv = self.nc.variables
    self.utime = netcdftime.utime(self.ncv['time'].units)
    self.dates = self.utime.num2date(self.ncv['time'][:])
    self.lon = self.ncv['lon'][:]
    self.lat = self.ncv['lat'][:]
    sse = self.ncv['sossheig'][0]
    lon2,lat2 = meshgrid(self.lon,self.lat)
    llwater = array((lon2[~sse.mask],lat2[~sse.mask])).T
    llland = array((lon2[sse.mask],lat2[sse.mask])).T
    self.land = sse.mask
    self.water = ~sse.mask
    self.nearest_water = KDTree(llwater).query(llland)[1]

  def get_bdy(self,timeidx,lon,lat,depths):
    # bilinear interpolation of sea surface elevation
    sse = self.ncv['sossheig'][timeidx]
    print '  interpolate index %d'%timeidx
    # fill lans with nearest water value
    sse[self.land] = sse[self.water][self.nearest_water]
    elevs = bminterp(sse,self.lon,self.lat,lon,lat)
    return elevs.data
  
  def close(self):
    self.nc.close()

# read setup
s = schism_setup()

# write bctides.in and create list of boundary nodes
bf = open('bctides.in','w')
bf.write("""01/01/2012 00:00:00 PST
0 0.0
0
1 nope
""")

bdy_nodes=[]
for seg in s.bdy_segments[:1]:
  # write segment into bctides.in
  bf.write('%d 4 0 4 4\n'%len(seg))
  bf.write('1.0\n1.0\n')

  bdy_nodes.extend(seg)
n = len(bdy_nodes)
bf.close()

ddict = dict(zip(s.inodes,s.depths))
xdict = dict(zip(s.inodes,s.lon))
ydict = dict(zip(s.inodes,s.lat))
depth = asarray([ ddict[ii] for ii in bdy_nodes ])
x = asarray([ xdict[ii] for ii in bdy_nodes ])
y = asarray([ ydict[ii] for ii in bdy_nodes ])

# open amm7 file
if len(sys.argv)>1:
  filename=sys.argv[1]
else:
  filename='/data/hofmeist/myocean/2012-01.amm7.nc'

bdydat = bdy_dataset(filename=filename)
ut = netcdftime.utime('seconds since 2012-01-01 00:00:00')

all_times = ut.date2num(bdydat.dates).astype('float32')
times = []
elevs = []

# interpolate elevation data at x,y
for idx,time in enumerate(all_times):
  if float(time) >= 0.0 and (time not in all_times[:idx]):
    times.append(all_times[idx])
    elevs.append(bdydat.get_bdy(idx,x,y,depth).astype('float32'))

# write data into netcdf
s.write_bdy_netcdf('amm7_elev2D.th.nc',asarray(times),asarray(elevs))

# close amm7 file
#bdydat.close()
