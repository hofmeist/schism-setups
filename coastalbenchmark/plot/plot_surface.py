from pylab import *
import netCDF4
import sys

if len(sys.argv)>2:
  var = sys.argv[2]
else:
  print('  usage: plot_surface.py file.nc variable')
  sys.exit(1)

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

x = ncv['SCHISM_hgrid_nodes_x'][:]
y = ncv['SCHISM_hgrid_nodes_y'][:]
sigma = ncv['sigma'][:]
nsigma = len(sigma)
bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:]
time = ncv['time'][:]/86400. # d


var = ncv[var]
time = array([0.0])

for tidx,t in enumerate(time):
  figure()
  tripcolor(x,y,nv-1,var[tidx,-1,:].squeeze(),cmap=cmap,rasterized=True)
  savefig('%s_surface_%05d.png'%(var,tidx),dpi=300)
  close()


