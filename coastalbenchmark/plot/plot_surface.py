from pylab import *
import netCDF4
import sys

if len(sys.argv)>2:
  varname = sys.argv[2]
else:
  print('  usage: plot_surface.py file.nc variable')
  sys.exit(1)

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

x = ncv['SCHISM_hgrid_node_x'][:]
y = ncv['SCHISM_hgrid_node_y'][:]
sigma = ncv['sigma'][:]
nsigma = len(sigma)
bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:]/86400. # d


var = ncv[varname]
#time = array([0.0])
cmap = cm.YlGnBu_r
cmap.set_under(color='w')

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
  v = var[tidx,-1,:].squeeze()
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  tripcolor(x,y,nv,v,cmap=cmap,rasterized=True)
  clim(0,30)
  cb=colorbar()
  cb.ax.set_title('%s\n'%(ncv[varname].long_name),size=10.)
  savefig('%s_surface_%05d.jpg'%(varname,tidx),dpi=100)
  #show()
  close()


