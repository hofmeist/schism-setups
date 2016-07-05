from pylab import *
import netCDF4
from scipy.spatial import cKDTree 

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

nc.close()

nc = netCDF4.Dataset('29_salt.nc')
ncv=nc.variables
s = ncv['salt'][:,:,1:]
s = ma.masked_equal(s,-9999.)
nc.close()

levels=arange(znum)

tree = cKDTree(zip(x,y))

ytrans = linspace(-50000.,30000,1000.)
xtrans = 0.0*ones(ytrans.shape)

dist,inds = tree.query(zip(xtrans,ytrans),k=3)
weight = 1.0/dist**2

tidx=3
strans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)
ztrans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)

for n in range(znum):
  #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
  #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
  strans[:,n] = s[tidx,n,inds].mean(axis=1)
  ztrans[:,n] = z[tidx,n,inds].mean(axis=1)
strans = ma.masked_where(strans<0.0,strans)

l2d,y2d = meshgrid(levels,ytrans)

figure(figsize=(12,10))

# fill z-levels
for n in range(len(depth)):
  nidx = where(zf[tidx,:,n].squeeze()==-9999.)
  zf[tidx,nidx,n] = zf[tidx,lmin[n]-1,n]

plot_grid=False
gridcol=(0.5,0.5,0.5)

pc = pcolormesh(y2d,ztrans,strans,shading='interp')

if plot_grid:
  for yy,zz in zip(y2d,z[tidx,:,idx].squeeze()):
    plot(yy,zz,'k-',lw=0.3,color=gridcol)

  for yy,zz in zip(y2d.T,zf[tidx,:,idx].squeeze().T):
    plot(yy,zz,'k-',lw=0.3,color=gridcol)


colorbar(pc)

xlim(-50000.,30000.)
ylim(-100.,3.0)
clim(10,30)
xlabel('y [m]')
ylabel('z [m]')

show()

