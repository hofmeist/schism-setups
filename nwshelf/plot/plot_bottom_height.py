import netCDF4
import sys
import matplotlib
#matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime

#if len(sys.argv)>2:
#  varname = sys.argv[2]
#else:
#  print('  usage: plot_bottom_height.py file.nc variable')
#  sys.exit(1)

if len(sys.argv)>2:
  tidx=int(sys.argv[2])
else:
  tidx=0

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
#sigma = ncv['sigma'][:]
#nsigma = len(sigma)
#bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:] # s
ut = utime(ncv['time'].units)
dates = ut.num2date(time)

lonb=[-18., 32.]
latb=[46., 67.]

if os.path.isfile('proj_bottsurf.pickle'):
    (proj,)=np.load('proj_bottsurf.pickle')
else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="i",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj_bottsurf.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

x,y = proj(lon,lat)

var = ncv['zcor']
#time = array([0.0])
cmap = cm.jet
#cmap.set_under(color='w')

def mask_triangles(masknodes,nv):
  idx = where(masknodes)[0]
  nvmask = []
  for nodes in nv:
    if any(in1d(nodes,idx)):
      nvmask.append(True)
    else:
      nvmask.append(False)
  return asarray(nvmask)

bidx = ncv['node_bottom_index'][:]
nbidx = len(bidx)

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

os.system('mkdir -p jpgs/h')
for tidx,t in enumerate(dates):
  z = var[tidx+tidx_offset,:].squeeze()
  z1 = z[bidx+1,arange(nbidx)].squeeze()
  z2 = z[bidx+2,arange(nbidx)].squeeze()
  z0 = z[bidx,arange(nbidx)].squeeze()
  hbot = z1-z0
  habv = z2-z1
  hfac = hbot/habv
  #habovebot=(z[2,:]-z[1,:]).squeeze()
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  if True:
    figure()
    cmap = cm.jet
    cbtitle='bottom layer height'
    tripcolor(x,y,nv,hfac,cmap=cmap,rasterized=True)
    clim(0,1)
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title(u'%s\n'%(cbtitle),size=10.)
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/h/h_%s.jpg'%(tstring),dpi=600)
    close()

