from pylab import *
import netCDF4

nc = netCDF4.Dataset('29_zcor.nc')
ncv = nc.variables

depth = ncv['depth'][1:]
x = ncv['SCHISM_hgrid_node_x'][1:]
y = ncv['SCHISM_hgrid_node_y'][1:]
z = ncv['zcor'][:,:,1:]
zf = z.copy()
z = ma.masked_equal(z,-9999.)
lmin = ncv['node_bottom_index'][1:]

znum = len(nc.dimensions['nSCHISM_vgrid_layers'])

levels=arange(znum)

idx = where(x == -50000.)
l2d,y2d = meshgrid(levels,y[idx])
tidx=6

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

xlim(0,50000.)
xlabel('y [m]')
ylabel('z [m]')

savefig('layers_boundary.pdf')

