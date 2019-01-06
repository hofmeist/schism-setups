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
    with open('plotproj.pickle','rb') as f:
      (proj,)=pickle.load(f)
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

cmap = cm.jet
#cmap=cm.BuPu
#cmap.set_under(color='w')

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

os.system('mkdir -p jpgs/%s'%varname)
for tidx,t in enumerate(dates):
  vs = var[tidx+tidx_offset].squeeze()
  plot_surface=True
  plot_bottom=False
  if plot_surface:
    fig=figure()
    fig.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
    if varname=='elev':
      cmap=cm.RdYlGn
      cmap.set_under('gray')
    tripcolor(x,y,nv,vs,cmap=cmap,rasterized=True)
    if uselim:
      clim(vmin,vmax)
    else:
      clim(0,vs.max())
    cbtitle = titlestr
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cax = axes([0.03,0.2,0.25,0.03])
    cb=colorbar(cax=cax,orientation='horizontal')
    for ll in cax.get_xmajorticklabels():
      ll.set_rotation(60.)
    cb.set_label(u'%s %s'%(cbtitle,unitsstr))
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_%s.jpg'%(varname,varname,tstring),dpi=200)
    close()



