import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime
import argparse
import numpy as np

def replace_superscripts(s):
  r = unicode(s.replace('^3',u'\u00b3'))
  r = unicode(r.replace('^2',u'\u00b2'))
  return r

parser = argparse.ArgumentParser()
parser.add_argument('ncfile', help='netcdf file')
parser.add_argument('-tidx', help='time index')
parser.add_argument('-vrange', help='values range [-vrange vmin,vmax]')
parser.add_argument('-title', help='title of colorbar')
parser.add_argument('-level', help='vertical level')
args = parser.parse_args()

if args.tidx is not None:
  tidx=int(args.tidx)
  plotmean=False
else:
  plotmean=True
titlestr='avg. velocity [cm/s]'

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
  # use titlestr as set
  pass

if args.level is not None:
  if ',' in args.level:
    upper_level = int(args.level.split(',')[1])
    if upper_level==-1:
      upper_level=None
    else:
      upper_level=upper_level+1
    lower_level = int(args.level.split(',')[0])
    level = lower_level
    vslice = slice(lower_level,upper_level)
  else:
    level=int(args.level)
    vslice = slice(level,None)
else:
  level=-10
  vslice = slice(level,None)

nc = netCDF4.Dataset(args.ncfile)
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
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

hvel = ncv['hvel_mean'][:]
zcor = ncv['zcor'][:]

integrate_layers=True
if (integrate_layers):
  # use level to integrate from level upwards
  zslice = zcor[:,:,vslice]
  uvel = np.trapz(hvel[:,:,vslice,0],x=zslice,axis=2)
  #uvel = uvel/(zslice.max(axis=2)-zslice.min(axis=2))
  vvel = np.trapz(hvel[:,:,vslice,1],x=zslice,axis=2)
  #vvel = vvel/(zslice.max(axis=2)-zslice.min(axis=2))
else:
  uvel = hvel[:,:,level,0]
  vvel = hvel[:,:,level,1]

if not(plotmean):
  u = uvel[tidx]
  v = vvel[tidx]
else:
  u = uvel.mean(axis=0)
  v = vvel.mean(axis=0)

vel = np.sqrt(u**2+v**2)*100 # cm/s
in_Sv=True
if (in_Sv):
  vel = vel/1000 # cm/s -> Sv/100km
  titlestr = 'avg. transport [Sv/100km]'

#cmap = cm.jet
cmap=cm.PuBuGn
#cmap.set_under(color='w')

if not(plotmean):
  dates = [dates[tidx],]
  tidx_offset=tidx

idxs =arange(len(x))
np.random.shuffle(idxs)
idxs = idxs[:20000]

os.system('mkdir -p jpgs/vel')
if True:
  if True:
    fig=figure()
    fig.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
    pc=tripcolor(x,y,nv,vel,cmap=cmap,rasterized=True)

    del hvel,zcor,uvel,vvel
    urot,vrot = proj.rotate_vector(u[idxs],v[idxs],lon[idxs],lat[idxs])
    del u,v
    #proj.quiver(x[idxs],y[idxs],u[idxs],v[idxs],pivot='mid',alpha=0.5)
    #urot=u[idxs]; vrot=v[idxs]
    if (uselim):
      upper_scale=vmax
    else:
      upper_scale=10.0 # deep transports
      upper_scale=0.1 # surface transports
    urot = ma.masked_where(vel[idxs]<0.05*upper_scale,urot)
    vrot = ma.masked_where(vel[idxs]<0.05*upper_scale,vrot)
    #quiverkws={'scale_units':'x','scale':10./10000.} # for deep transports
    quiverkws={'scale_units':'x','scale':upper_scale/10000.}
    proj.quiver(x[idxs],y[idxs],urot,vrot,pivot='mid',alpha=0.5,**quiverkws)

    # test vector
    #xx,yy = proj(0.0,75.)
    #urot,vrot = proj.rotate_vector(asarray([0.0]),asarray([30.0]),asarray([0.0]),asarray([75.]))
    #proj.quiver(xx,yy,urot,vrot,color='r')

    if uselim:
      pc.set_clim(vmin,vmax)
    else:
      pass
      #pc.set_clim(0,20.)
    cbtitle = titlestr
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    cax = axes([0.03,0.2,0.25,0.03])
    cb=colorbar(pc,cax=cax,orientation='horizontal')
    for ll in cax.get_xmajorticklabels():
      ll.set_rotation(60.)
    cb.set_label(u'%s'%(cbtitle))
    if plotmean:
      tstring='monthly'
    else:
      tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/vel/meantransport_%s.jpg'%(tstring),dpi=300)
    show()
    close()



