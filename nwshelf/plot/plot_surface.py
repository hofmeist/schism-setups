from pylab import *
import netCDF4
import sys
from mpl_toolkits.basemap import Basemap
import pickle,os

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

for tidx,t in enumerate(time):
  figure()
  v = var[tidx,:].squeeze()
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  tripcolor(x,y,nv,v,cmap=cmap,rasterized=True)
  clim(-2,2)
  proj.drawcoastlines()
  proj.fillcontinents((0.9,0.9,0.8))
  cb=colorbar()
  cb.ax.set_title('%s\n'%(ncv[varname].long_name),size=10.)
  savefig('%s_surface_%05d.jpg'%(varname,tidx),dpi=100)
  #show()
  close()


