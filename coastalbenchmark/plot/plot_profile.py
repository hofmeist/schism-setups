from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import sys

#dfile = sys.argv[1]
#varn = dfile.split('_')[1][:-3]
#period = dfile.split('_')[0]
period=30
dfile='30_hvel.nc'
varn='hvel_v'
#dfile='30_temp.nc'
#varn='temp'

nc = netCDF4.Dataset('%s_zcor.nc'%period)
ncv = nc.variables

depth = ncv['depth'][:]
x = ncv['SCHISM_hgrid_node_x'][:]
y = ncv['SCHISM_hgrid_node_y'][:]

tree = cKDTree(zip(x,y))
dist,inds = tree.query((00000.0,31000),k=1)
print('  found node %d appr. %0.1fm from (0.0,31500)'%(int(inds),float(dist)))
idx = int(inds)


z = ncv['zcor'][:,:,idx]
zf = z.copy()
z = ma.masked_equal(z,-9999.)
lmin = ncv['node_bottom_index'][idx]
znum = len(nc.dimensions['nSCHISM_vgrid_layers'])

nc.close()

nc = netCDF4.Dataset(dfile)
ncv=nc.variables
hours = (ncv['time'][:]-ncv['time'][0])/3600.
#u = ncv['hvel_u'][:,:,idx]
#u = ma.masked_equal(u,-9999.)
v = ncv[varn][:,:,idx]
v = ma.masked_equal(v,-9999.)
nc.close()

levels=arange(znum+1)
hours = hstack((hours,array([24])))
l2d,t2d = meshgrid(levels,hours)

z = vstack((z,z[0,:]))
z = hstack((z,z[:,-1:]))

v = vstack((v,v[0,:]))
v = hstack((v,v[:,-1:]))

figure(figsize=(5.5,8))

cmap=cm.RdYlBu
pcolor(t2d,z,v,cmap=cmap,shading='interp')

if True:
  if varn=='hvel_v':
    clim(-0.1,0.1)
  if varn == 'temp':
    clim(10,20)
xlabel('time [h]')
ylabel('z [m]')
ylim(-100.,10.0)
xlim(0,24)
cb=colorbar()
#cb.set_label('y velocity [m/s]')

show()
