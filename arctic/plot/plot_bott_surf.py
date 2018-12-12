import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime
import argparse

def replace_superscripts(s):
  r = unicode(s.replace('^3',u'\u00b3'))
  r = unicode(r.replace('^2',u'\u00b2'))
  return r

parser = argparse.ArgumentParser()
parser.add_argument('ncfile', help='netcdf file')
parser.add_argument('varname',help='variable name')
parser.add_argument('-tidx', help='time index')
parser.add_argument('-vrange', help='values range [-vrange vmin,vmax]')
parser.add_argument('-title', help='title of colorbar')
parser.add_argument('-units', help='unit string')
parser.add_argument('-scalefactor', help='linear scaling factor')
args = parser.parse_args()

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

if args.title is not None:
  titlestr=unicode(args.title)
else:
  titlestr=args.varname

if args.units is not None:
  unitsstr=replace_superscripts(args.units)
else:
  unitsstr=''

if args.scalefactor is not None:
  fac = float(args.scalefactor)
else:
  fac=1.0

nc = netCDF4.Dataset(args.ncfile)
ncv = nc.variables
varname = args.varname

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
#sigma = ncv['sigma'][:]
#nsigma = len(sigma)
#bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:] # s
ut = utime(ncv['time'].units)
dates = ut.num2date(time)

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

x,y = proj(lon,lat)

var = ncv[varname]
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

try:
  bidx = ncv['node_bottom_index'][:]
  nbidx = len(bidx)
except:
  zvar = ncv['zcor'][0]
  bidx = zeros(lon.shape,dtype='int')
  for i in range(len(lon)):
    try:
      bidx[i] = max(where(zvar.mask[i])[0])
    except:
      bidx[i] = 0
  bidx = bidx+1
  nbidx = len(bidx)

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

os.system('mkdir -p jpgs/%s'%varname)
for tidx,t in enumerate(dates):
  v = var[tidx+tidx_offset].squeeze()
  if varname=='elev':
    vs = v
    plot_surface=True
    plot_bottom=False
  else:
    vs = fac*v[:,-1].squeeze()
    vb = fac*v[arange(nbidx),bidx]
    plot_surface=True
    plot_bottom=True
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  if plot_surface:
    fig=figure()
    fig.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
    if varname=='elev':
      cmap=cm.RdYlGn
      cmap.set_under('gray')
    tripcolor(x,y,nv,vs,cmap=cmap,rasterized=True)
    if varname=='salt':
      clim(5,35)
      cbtitle='surface salinity'
    elif varname=='temp':
      clim(1,vs.max())
      cbtitle=u'surface temperature [\u00b0C]'
    elif varname=='elev':
      clim(-2,2)
      cbtitle='ssh [m]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vs.max())
      cbtitle = titlestr
    if uselim:
      clim(vmin,vmax)
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cax = axes([0.85,0.05,0.02,0.4])
    cb=colorbar(cax=cax)
    cb.set_label(u'%s %s'%(cbtitle,unitsstr))
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_surface_%s.jpg'%(varname,varname,tstring),dpi=200)
    close()

  if plot_bottom:
    fig=figure()
    fig.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
    tripcolor(x,y,nv,vb,cmap=cmap,rasterized=True)
    if varname=='salt':
      clim(5,35)
      cbtitle='bottom salinity'
    elif varname=='temp':
      clim(1,vb.max())
      cbtitle=u'bottom temperature [\u00b0C]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vb.max())
      cbtitle=titlestr
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cax = axes([0.85,0.05,0.02,0.4])
    cb=colorbar(cax=cax)
    cb.set_label(u'%s %s'%(cbtitle,unitsstr))
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_bottom_%s.jpg'%(varname,varname,tstring),dpi=200)
    #show()
    close()


