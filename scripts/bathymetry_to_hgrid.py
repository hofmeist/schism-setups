#from schism import *
import pickle
import netCDF4
from pylab import *

f = open('coast_proj.pickle','rb')
m, = pickle.load(f)
f.close()

nc = netCDF4.Dataset('emodnet_bathymetry.nc')
ncv = nc.variables

lonv=ncv['lon'][:]
latv=ncv['lat'][:]
depth = ncv['depth'][:].flat[:]

lo,la = meshgrid(lonv,latv)

coords_geo = zip(lo.flat,la.flat)
xc,yc = m(lo.flat[:],la.flat[:])

idx = where(depth.mask==False)
x = xc[idx]
y = yc[idx]
d = -depth.data[idx]

del depth,xc,yc
fo = open('xyd_bathymetry.pickle','wb')
pickle.dump((x,y,d),fo,protocol=-1)
fo.close()

nc.close()
