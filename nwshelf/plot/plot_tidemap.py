import matplotlib
matplotlib.use('Agg')
from pylab import *
import netCDF4
import sys
from mpl_toolkits.basemap import Basemap
import pickle,os
import ttide as tt

if len(sys.argv)>2:
  varname = sys.argv[2]
else:
  print('  usage: plot_surface.py file.nc variable')
  sys.exit(1)

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
#sigma = ncv['sigma'][:]
#nsigma = len(sigma)
#bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:]/86400. # d

lonb=[-18., 32.]
latb=[46., 67.]

if os.path.isfile('proj.pickle'):
    (proj,)=np.load('proj.pickle')
else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="h",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

x,y = proj(lon,lat)

var = ncv[varname]
#time = array([0.0])
cmap = cm.RdYlGn
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

inum = len(nc.dimensions['nSCHISM_hgrid_node'])
m2_amp = zeros((inum,))
m2_pha = zeros((inum,))
m4_amp = zeros((inum,))
m4_pha = zeros((inum,))

ut = netcdftime(ncv['time'].units)
hours = ncv['time'][:]/3600.
hours = hours - hours[0]
dthours = hours[1]-hours[0]

for i in range(inum):
  tides = tt.t_tide(ncv['elev'][:,i],dt=dthours,out_style=None)
  m2idx = tides['nameu'].index(b'M2  ')
  m4idx = tides['nameu'].index(b'M4  ')
  m2_amp[i] = tides['tidevcon'][m2idx][0]
  m4_pha[i] = tides['tidevcon'][m2idx][2]
  m4_amp[i] = tides['tidevcon'][m4idx][0]
  m2_pha[i] = tides['tidevcon'][m4idx][2]

if False:
  figure()
  tripcolor(x,y,nv,m2_amp,cmap=cm.jet,rasterized=True)
  proj.drawcoastlines()
  proj.fillcontinents((0.9,0.9,0.8))
  cb=colorbar()
  cb.ax.set_title('M2 [m]\n',size=10.)
  savefig('m2_amp.jpg'%(varname,varname,tidx),dpi=600)
  #show()
  close()


