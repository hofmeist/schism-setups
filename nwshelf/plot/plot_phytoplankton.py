import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('path', help='path of netcdf files including stack number')
parser.add_argument('-tidx', help='time index')
parser.add_argument('-vrange', help='values range [--vrange=vmin,vmax]')
args = parser.parse_args()

print args

if args.tidx is not None:
  tidx=int(args.tidx)
else:
  tidx = -1

if 'vrange' is not None:
  try:
    s1,s2 = args.vrange.split(',')
    vmin,vmax = float(s1),float(s2)
    uselim=True
  except:
    uselim=False
else:
  uselim=False
  


nc = netCDF4.Dataset(args.path+'_fab_6.nc')
ncv = nc.variables

nc2 = netCDF4.Dataset(args.path+'_fab_7.nc')
ncv2 = nc2.variables

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

var = ncv['fab_5']
var2 = ncv2['fab_6']
#time = array([0.0])
cmap = cm.jet
cmap = cm.YlGn
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

os.system('mkdir -p jpgs/%s'%'phytoplankton')
varname = 'phytoplankton'
for tidx,t in enumerate(dates):
  v = var[tidx+tidx_offset,:].squeeze()+var2[tidx+tidx_offset,:].squeeze()
  if varname=='elev':
    vs = v
    plot_surface=True
    plot_bottom=False
  else:
    vs = v[-1,:].squeeze()
    vb = v[bidx,arange(nbidx)]
    plot_surface=True
    plot_bottom=True
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  if plot_surface:
    figure()
    if varname=='elev':
      cmap=cm.RdYlGn
      cmap.set_under('gray')
    tripcolor(x,y,nv,vs,cmap=cmap,rasterized=True)
    if varname=='salt':
      clim(5,35)
      cbtitle='surface salinity'
    elif varname=='temp':
      clim(1,vs.max())
      cbtitle=u'surface temperature\n[\u00b0C]'
    elif varname=='elev':
      clim(-2,2)
      cbtitle='ssh [m]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vs.max())
      cbtitle=varname
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title(u'%s\n%s\n'%(cbtitle,u'[mgC/m\u00b3]'),size=10.)
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_surface_%s.jpg'%(varname,varname,tstring),dpi=200)
    close()

  if plot_bottom:
    figure()
    tripcolor(x,y,nv,vb,cmap=cmap,rasterized=True)
    if varname=='salt':
      clim(5,35)
      cbtitle='bottom salinity'
    elif varname=='temp':
      clim(1,vb.max())
      cbtitle=u'bottom temperature\n[\u00b0C]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vb.max())
      cbtitle=varname
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title(u'%s\n%s\n'%(cbtitle,u'[mgC/m\u00b3]'),size=10.)
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_bottom_%s.jpg'%(varname,varname,tstring),dpi=200)
    #show()
    close()


