from pylab import *
#from matplotlib.collections import PolyCollection
from mpl_toolkits.basemap import Basemap
import sys,os,pickle
#from plotting import *
import netCDF4
import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import *

s = schism_setup()


# set map boundaries
xl,yl = (-15.0,60.0)
xu,yu = (100,75.0)

if os.path.isfile('plotproj.pickle'):
    (proj,)=np.load('plotproj.pickle')
else:
    if False:
      proj = Basemap(projection='npstere',boundinglat=55.,lon_0=0.0,resolution='i')
    else:
      proj = Basemap(projection='lcc',
                       resolution='i',area_thresh=10.0,
                        llcrnrlon=xl,
                        llcrnrlat=yl,
                        urcrnrlon=xu,
                        urcrnrlat=yu,
                        lat_0=70.0,
                        lon_0=20.0)

    f=open('plotproj.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

xx,yy = proj(s.lon,s.lat)
nv = asarray(s.nv)-1

if len(sys.argv)>1:
  hfile = sys.argv[1]
else:
  hfile = 'hotstart.nc'

nc = netCDF4.Dataset(hfile)
ncv = nc.variables
v = ncv['tr_nd'][:,0,:].squeeze()

cmap = cm.ocean_r
cmap = cm.jet

f = figure(figsize=(10,12))

subplot(211)
tripcolor(xx,yy,nv,v[:,1],shading='flat',cmap=cmap)
colorbar(label='S [psu]')

proj.drawcoastlines()
proj.fillcontinents((0.9,0.9,0.8))
#savefig('%s_bathymetry.png'%(filename.split('.')[0]),dpi=600)

subplot(212)
tripcolor(xx,yy,nv,v[:,0],shading='flat',cmap=cmap)
colorbar(label='T [degC]')

proj.drawcoastlines()
proj.fillcontinents((0.9,0.9,0.8))


show()

    
