import matplotlib
matplotlib.use('Agg')

from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import sys,os

dfile = sys.argv[1]
varn = dfile.split('_')[1][:-3]
period = dfile.split('_')[0]

if len(sys.argv)>2:
  varn=sys.argv[2]
else:
  if varn=='hvel':
    varn='hvel_v'

nc = netCDF4.Dataset('%s_zcor.nc'%period)
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

nc = netCDF4.Dataset(dfile)
ncv=nc.variables
s = ncv[varn][:,:,1:]
s = ma.masked_equal(s,-9999.)
nc.close()

levels=arange(znum)

tree = cKDTree(zip(x,y))

x0 = 0.0
#x0 = 100000.
ymax=30000.
ymax=100000.

ytrans = linspace(-50000.,ymax,1000.)
xtrans = x0*ones(ytrans.shape)

dist,inds = tree.query(zip(xtrans,ytrans),k=10)
weight = 1.0/dist**2

tidx=6
strans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)
ztrans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)

os.system('mkdir -p %s'%varn)
for tidx in range(24):

  print('  tidx %03d'%tidx)
  for n in range(znum):
    #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    strans[:,n] = s[tidx,n,inds].mean(axis=1)
    ztrans[:,n] = z[tidx,n,inds].mean(axis=1)
  strans = ma.masked_where(strans<-5.0,strans)

  l2d,y2d = meshgrid(levels,ytrans)

  figure(figsize=(12,10))

  # fill z-levels
  for n in range(len(depth)):
    nidx = where(zf[tidx,:,n].squeeze()==-9999.)
    zf[tidx,nidx,n] = zf[tidx,lmin[n]-1,n]

  plot_grid=True
  gridcol=(0.5,0.5,0.5)
  cmap=cm.YlGnBu_r
  cmap=cm.RdYlBu_r

  if varn=='tdff':
    strans = log10(strans)
    climmin=-7
    climmax=-0.2
    ctitle=u'turb. diffusivity\n[m\u00b2/s\u00b2]'
  elif varn=='hvel_v':
    climmin=-0.5
    climmax=0.5
    ctitle=u'cross-slope velocity\n[m/s]'
  elif varn=='hvel_u':
    climmin=-0.5
    climmax=0.5
    ctitle=u'along-slope velocity\n[m/s]'
  else:
    climmin=10.
    climmax=strans.max()
    if varn=='salt':
      ctitle='salinity'
    elif varn=='temp':
      ctitle='temperature\n[degC]'

  pc = pcolormesh(y2d,ztrans,strans,shading='interp',cmap=cmap)

  if plot_grid:
    #for yy,zz in zip(y2d,ztrans.squeeze()):
    #  plot(yy,zz,'k-',lw=0.3,color=gridcol)

    for yy,zz in zip(y2d.T,ztrans.squeeze().T):
      plot(yy,zz,'k-',lw=0.3,color=gridcol)


  cb=colorbar(pc)
  cb.set_label(ctitle)

  xlim(-50000.,ymax)
  ylim(-100.,3.0)
  clim(climmin,climmax)
  xlabel('y [m]')
  ylabel('z [m]')

  savefig('%s/%s_%s_%03d.png'%(varn,period.split('/')[-1],varn,tidx),dpi=300)
  #show()
  close()

