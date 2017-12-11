import matplotlib
matplotlib.use('Agg')

from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import sys,os

dfile = sys.argv[1]

if len(sys.argv)>2:
  varn=sys.argv[2]
else:
  if varn=='hvel':
    varn='hvel_v'

nc = netCDF4.Dataset(dfile)
ncv = nc.variables

depth = ncv['depth'][:]
x = ncv['SCHISM_hgrid_node_x'][:]
y = ncv['SCHISM_hgrid_node_y'][:]
z = ncv['zcor'][:,:,:]
zf = z.copy()
z = ma.masked_equal(z,-9999.)
try:
  lmin = ncv['node_bottom_index'][:]
except:
  lmin = ones(depth.shape)
  z0 = z[0].squeeze()
  z0min = z0.min(axis=1)
  for n in range(len(x)):
    lmin[n] = int(where(z0[n,:] == float(z0min[n]))[0])+1

znum = len(nc.dimensions['nSCHISM_vgrid_layers'])
tnum = len(nc.dimensions['time'])

s = ncv[varn][:,:,:]
s = ma.masked_where(z.mask,s)
nc.close()

levels=arange(znum)

tree = cKDTree(zip(x,y))

x0 = 0.0

if len(sys.argv)>3:
    climmin,climmax = [float(el) for el in sys.argv[3].split(',')]
    clim_use_defaults=False
else:
    clim_use_defaults=True

ymax=20000.

ytrans = linspace(0.,ymax,500.)
xtrans = x0*ones(ytrans.shape)

dist,inds = tree.query(zip(ytrans,xtrans),k=3)
weight = 1.0/dist**2

tidx=10
strans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)
ztrans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)

os.system('mkdir -p %s'%varn)
for tidx in range(0,tnum,28):

  print('  tidx %03d'%tidx)
  for n in range(znum-1):
    #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    strans[:,n] = s[tidx,inds,n].mean(axis=1)
    ztrans[:,n] = z[tidx,inds,n].mean(axis=1)
  strans = ma.masked_where(strans<-5.0,strans)

  l2d,y2d = meshgrid(levels,ytrans)

  figure(figsize=(12,10))

  # fill z-levels
  #for n in range(len(depth)):
  #  nidx = where(zf[tidx,:,n].squeeze()==-9999.)
  #  zf[tidx,nidx,n] = zf[tidx,lmin[n]-1,n]

  plot_grid=True
  gridcol=(0.5,0.5,0.5)
  cmap=cm.YlGnBu_r
  cmap=cm.RdYlBu_r

  if varn=='tdff':
    strans = log10(strans)
    if clim_use_defaults:
      climmin=-7
      climmax=-0.2
    ctitle=u'turb. diffusivity\n[m\u00b2/s\u00b2]'
  elif varn=='hvel_v':
    if clim_use_defaults:
      climmin=-0.5
      climmax=0.5
    ctitle=u'cross-slope velocity\n[m/s]'
  elif varn=='hvel_u':
    if clim_use_defaults:
      climmin=-0.5
      climmax=0.5
    ctitle=u'along-slope velocity\n[m/s]'
  else:
    if clim_use_defaults:
      climmin=strans.min()
      climmax=strans.max()
    if varn=='salt':
      ctitle='salinity'
      climmin=35.0
      climmax=36.0
    elif varn=='temp':
      ctitle='temperature\n[degC]'
    else:
      ctitle=varn

  pc = pcolormesh(y2d,ztrans,strans,shading='interp',cmap=cmap)

  if plot_grid:
    #for yy,zz in zip(y2d,ztrans.squeeze()):
    #  plot(yy,zz,'k-',lw=0.3,color=gridcol)

    for yy,zz in zip(y2d.T,ztrans.squeeze().T):
      plot(yy,zz,'k-',lw=0.3,color=gridcol)


  cb=colorbar(pc)
  cb.set_label(ctitle)

  xlim(0.,ymax)
  ylim(-50.,1.0)
  clim(climmin,climmax)
  xlabel('x [m]')
  ylabel('z [m]')

  savefig('%s/%s_%03d.png'%(varn,varn,tidx),dpi=300)
  #show()
  close()

