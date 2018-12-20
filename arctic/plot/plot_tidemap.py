from pylab import *
#from matplotlib.collections import PolyCollection
from mpl_toolkits.basemap import Basemap
import sys,os,pickle
#from plotting import *
import netCDF4
import sys,os

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

    with open('plotproj.pickle','wb') as f:
      pickle.dump((proj,),f)

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
nc.close

xx,yy = proj(lon,lat)

tnc = netCDF4.Dataset('tideanalysis.nc')
tncv = tnc.variables

ename = 'm2_amp'
pname = 'm4_pha'
em2 = tncv[ename][:]
pm2 = tncv[pname][:]

ename = 's2_amp'
pname = 's2_pha'
es2 = tncv[ename][:]
ps2 = tncv[pname][:]

ename = 'm4_amp'
pname = 'm2_pha'
em4 = tncv[ename][:]
pm4 = tncv[pname][:]


tnc.close()

cmap = cm.YlGnBu
#cmap = cm.jet

f = figure(figsize=(10,12))

subplot(211)
pc = tripcolor(xx,yy,nv,em2,shading='flat',cmap=cmap,rasterized=True)
tricontour(xx,yy,nv,pm2,levels=list(range(0,350,30)),linewidths=1.0,colors='k')
colorbar(pc,label='M2 amplitude [m]')

proj.drawcoastlines(color=(0.45,0.45,0.4))
proj.fillcontinents((0.9,0.9,0.8))
#savefig('%s_bathymetry.png'%(filename.split('.')[0]),dpi=600)

subplot(212)
pc = tripcolor(xx,yy,nv,es2,shading='flat',cmap=cmap,rasterized=True)
tricontour(xx,yy,nv,ps2,levels=list(range(0,350,30)),linewidths=1.0,colors='k')
colorbar(pc,label='S2 amplitude [m]')

proj.drawcoastlines(color=(0.45,0.45,0.4))
proj.fillcontinents((0.9,0.9,0.8))

#subplot(213)
#pc = tripcolor(xx,yy,nv,em4,shading='flat',cmap=cmap,rasterized=True)
#tricontour(xx,yy,nv,pm4,levels=list(range(0,350,30)),linewidths=1.0,colors='k')
#colorbar(pc,label='M4 amplitude [m]')

proj.drawcoastlines(color=(0.45,0.45,0.4))
proj.fillcontinents((0.9,0.9,0.8))


savefig('m2_s2_cotidal_map.pdf',dpi=600)

    
