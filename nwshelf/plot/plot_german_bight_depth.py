import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime

if len(sys.argv)>2:
  varname = sys.argv[2]
else:
  varname='salt'
  print('  usage: plot_german_bight.py file.nc variable')

if len(sys.argv)>3:
  tidx=int(sys.argv[3])
else:
  tidx=-1

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

lonb=[6.5, 8.8]
latb=[53.5, 54.6]

if os.path.isfile('proj_gb.pickle'):
    (proj,)=np.load('proj_gb.pickle')
else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="h",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj_gb.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

x,y = proj(lon,lat)

varname='depth'
var = ncv['depth']
#time = array([0.0])
cmap = cm.jet
cmap.set_under(color='gray')

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
  dates = dates[tidx]
  tidx_offset=tidx
else:
  tidx_offset=0

os.system('mkdir -p jpgs')
if True:
#for tidx,t in enumerate(dates):
  vs = var[:].squeeze()
  #mask = vs == -99.
  #mask = mask_triangles(mask,nv)
  if True:
    figure()
    if varname=='elev':
      cmap=cm.RdYlGn
      cmap.set_under('gray')
    #tripcolor(x,y,nv,vs,cmap=cmap,mask=mask,rasterized=True)
    tripcolor(x,y,nv,vs,cmap=cmap,rasterized=True)
    if varname=='salt':
      clim(15,35)
      cbtitle='surface salinity'
    elif varname=='temp':
      clim(1,10)
      cbtitle=u'surface temperature\n[\u00b0C]'
    elif varname=='elev':
      clim(-2,2)
      cbtitle='ssh [m]'
    elif varname=='depth':
      clim(-2,2)
      cbtitle='depth [m]'
    proj.drawcoastlines()
    #proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title('%s\n'%(cbtitle),size=10.)
    savefig('jpgs/%s_germanbight.jpg'%(varname),dpi=600)
    close()
  


