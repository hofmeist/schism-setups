from pylab import *
import netCDF4
import sys

try:
  tidx = int(sys.argv[2])
except:
  tidx = 0

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

nnodes = len(ncv['SCHISM_hgrid_node_x'])
nfaces = len(ncv['SCHISM_hgrid_face_x'])
lons = ncv['SCHISM_hgrid_node_x'][:]
lats = ncv['SCHISM_hgrid_node_y'][:]
elevs = ncv['elev'][tidx,:]


f = open('elev_new.ic','w')
f.write('initial surface elevation\n')
f.write('%d %d\n'%(nfaces,nnodes))

for n in range(nnodes):
  f.write('%d %0.2f %0.2f %0.5f\n'%(n+1,lons[n],lats[n],elevs[n]))

nc.close()
f.close()


