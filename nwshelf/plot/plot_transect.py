import matplotlib
matplotlib.use('Agg')
import sys
sys.path.append('/pf/g/g260078/pythoninstall/pythonlib')
from plotting import cm_Parula

from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import os

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
tnum,pnum,zznum=s.shape
s = ma.masked_equal(s,-9999.)
nc.close()

levels=arange(znum)

tree = cKDTree(zip(x,y))

if len(sys.argv)>3:
    lat0 = float(sys.argv[3])
else:
    lat0 = 0.0

if len(sys.argv)>4:
    climmin,climmax = [float(el) for el in sys.argv[4].split(',')]
    clim_use_defaults=False
else:
    clim_use_defaults=True

#x0 = 100000.
lonmin=3.0
lonmax=8.7

xtrans = linspace(lonmin,lonmax,500.)
ytrans = lat0*ones(xtrans.shape)

dist,inds = tree.query(zip(xtrans,ytrans),k=10)
weight = 1.0/dist**2

tidx=0
strans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)
ztrans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)

os.system('mkdir -p %s'%varn)
for tidx in range(tnum):

  print('  tidx %03d'%tidx)
  for n in range(znum):
    #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    strans[:,n] = s[tidx,n,inds].mean(axis=1)
    ztrans[:,n] = z[tidx,n,inds].mean(axis=1)
  strans = ma.masked_where(strans<-5.0,strans)

  l2d,x2d = meshgrid(levels,xtrans)

  figure(figsize=(15,5))

  # fill z-levels
  for n in range(len(depth)):
    nidx = where(zf[tidx,:,n].squeeze()==-9999.)
    zf[tidx,nidx,n] = zf[tidx,lmin[n]-1,n]

  plot_grid=True
  gridcol=(0.5,0.5,0.5)
  cmap=cm.YlGnBu_r
  cmap=cm.RdYlBu_r
  sfac=1.0

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
    cmap=cm_Parula()
    if clim_use_defaults:
      climmin=10.
      climmax=strans.max()
    if varn=='salt':
      ctitle='salinity'
    elif varn=='temp':
      ctitle='temperature\n[degC]'
    elif varn in ['fab_6','fab_7']:
      ctitle=u'phytoplankton\n[mgC/m\u00b3]'
    elif varn=='fab_1':
      ctitle=u'nitrate\n[mmolN/m\u00b3]'
      sfac=1.0/6.625/12.01
    elif varn=='fab_3':
      ctitle=u'phosphate\n[mmolP/m\u00b3]'
      sfac=1.0/12.01/106.0
    else:
      ctitle=varn+'\n[mgC/m3]'

  pc = pcolormesh(x2d,ztrans,sfac*strans,shading='interp',cmap=cmap)

  if plot_grid:
    #for yy,zz in zip(x2d,ztrans.squeeze()):
    #  plot(yy,zz,'k-',lw=0.3,color=gridcol)

    for yy,zz in zip(x2d.T,ztrans.squeeze().T):
      plot(yy,zz,'k-',lw=0.3,color=gridcol)


  cb=colorbar(pc)
  cb.set_label(ctitle)

  xlim(lonmin,lonmax)
  ylim(-60.,3.0)
  clim(sfac*climmin,sfac*climmax)
  xlabel('lon [degE]')
  ylabel('z [m]')

  savefig('%s/%s_%s_lat%03d_%03d.png'%(varn,period.split('/')[-1],varn,int(lat0),tidx),dpi=300)
  #show()
  close()

