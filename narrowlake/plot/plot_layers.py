from pylab import *
import netCDF4

nc = netCDF4.Dataset('outputs/schout_1.nc')
ncv = nc.variables

depth = ncv['depth'][1:]
x = ncv['SCHISM_hgrid_node_x'][1:]/1000.
y = ncv['SCHISM_hgrid_node_y'][1:]/1000.
z = ncv['zcor'][:,:,1:]
zf = z.copy()
z = ma.masked_equal(z,-9999.)
lmin = ncv['node_bottom_index'][1:]

znum = len(nc.dimensions['nSCHISM_vgrid_layers'])

levels=arange(znum)

idx = where(y == 0.)
l2d,y2d = meshgrid(levels,x[idx])
tidx=0

figure(figsize=(12,10))

# fill z-levels
for n in range(len(depth)):
  nidx = where(zf[tidx,:,n].squeeze()==-9999.)
  zf[tidx,nidx,n] = zf[tidx,lmin[n]-1,n]

for yy,zz in zip(y2d,z[tidx,:,idx].squeeze()):
  plot(yy,zz,'k.-',lw=0.3)

for yy,zz in zip(y2d.T,zf[tidx,:,idx].squeeze().T):
  plot(yy,zz,'k.-',lw=0.3)

plot(yy,-depth[idx],'-',color=(0.3,0.3,0.3),lw=2.0)

xlim(0,20.)
xlabel('x [km]')
ylabel('z [m]')

savefig('layers_boundary.pdf')

