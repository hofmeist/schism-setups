#from schism import *
import pickle
import netCDF4
from pylab import *
import sys

if len(sys.argv)>1:
  bathyfile = sys.argv[1]
else:
  bathyfile = 'emodnet_bathymetry.nc'

f = open('coast_proj.pickle','rb')
m, = pickle.load(f)
f.close()

nc = netCDF4.Dataset(bathyfile)
ncv = nc.variables

lonv=ncv['lon'][:]
latv=ncv['lat'][:]
depth = ncv['depth'][:].astype('float32').flat[:]

lo,la = meshgrid(lonv,latv)
print('done meshgrid')

#coords_geo = zip(lo.flat,la.flat)
xc,yc = m(lo.flat[:],la.flat[:])
del lo,la
print('done projection')

idx = where(depth.mask==False)
x = xc[idx]
y = yc[idx]
d = -depth.data[idx]

del depth,xc,yc
print('start pickling')

fo = open('xyd_bathymetry.pickle','wb')
pickle.dump((x,y,d),fo,protocol=-1)
fo.close()

nc.close()
