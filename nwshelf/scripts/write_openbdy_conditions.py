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


write_ts=True
write_const_ts=False
s = schism_setup()

bf = open('bctides.in','w')
bf.write("""01/01/2012 00:00:00 PST
0 0.0
0
1 nope
""")

bdy_nodes=[]
for seg in s.bdy_segments[:1]:
  # write segment into bctides.in
  if write_ts:
    bf.write('%d 4 0 4 4\n'%len(seg))
    bf.write('1.0\n1.0\n')
  else:
    # use constant salt and temperature
    bf.write('%d 4 0 2 2\n'%len(seg))
    bf.write('5.0\n1.0\n35.0\n1.0\n')

  bdy_nodes.extend(seg)
n = len(bdy_nodes)

#river_nodes = s.bdy_segments[3]
#bf.write("""%d 0 2 2 2
#%0.2f
#%0.2f
#1.0
#0.0
#1.0
#"""%(len(river_nodes),-discharge,tempsurf))
bf.close()

ddict = dict(zip(s.inodes,s.depths))
xdict = dict(zip(s.inodes,s.lon))
ydict = dict(zip(s.inodes,s.lat))
depth = asarray([ ddict[ii] for ii in bdy_nodes ])
x = asarray([ xdict[ii] for ii in bdy_nodes ])
y = asarray([ ydict[ii] for ii in bdy_nodes ])

if write_const_ts:
    bdyvgrid = asarray([s.vgrid[ii].filled(-1.) for ii in bdy_nodes ])

if len(sys.argv)>1:
  filename=sys.argv[1]
else:
  filename='/data/hofmeist/myocean/2012-01.amm7.nc'

bdydat = bdy_dataset(filename=filename)
ut = netcdftime.utime('seconds since 2012-01-01 00:00:00')

times = ut.date2num(bdydat.dates).astype('float32')

f = open('elev2D.th','wb')
for idx,time in enumerate(times):
  if float(time) >= 0.0 and (time not in times[:idx]):
    time.tofile(f)
    elevs = bdydat.get_bdy(idx,x,y,depth).astype('float32')
    #print('%0.2f num elev = %d'%(time,len(elevs)))
    elevs.tofile(f)
f.close()

bdydat.close()

if write_const_ts:
  f = open('TEM_3D.th','wb')
  for time in array([0.0,32*86400.]).astype('float32'):
    time.tofile(f)
    for i in range(len(bdy_nodes)):
      temp = interp(depth[i]*bdyvgrid[i],[-66.,-33.],[tempbott,tempsurf])
      temp.astype('float32').tofile(f)
  f.close()
  

