import matplotlib
matplotlib.use('Agg')
import sys
sys.path.append('/pf/g/g260078/pythoninstall/pythonlib')
from plotting import cm_Parula

from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import os
import argparse
try:
  from netcdftime import utime
except:
  from cftime import utime
import numpy as np
import cPickle as pickle

def replace_superscripts(s):
  r = unicode(s.replace('^3',u'\u00b3'))
  r = unicode(r.replace('^2',u'\u00b2'))
  r = unicode(r.replace('^0',u'\u00b0'))
  return r

parser = argparse.ArgumentParser()
parser.add_argument('ncfile', help='netcdf file')
parser.add_argument('varname',help='variable name')
parser.add_argument('-tidx', help='time index')
parser.add_argument('-vrange', help='values range [-vrange vmin,vmax]')
parser.add_argument('-title', help='title of colorbar')
parser.add_argument('-units', help='unit string')
parser.add_argument('-scalefactor', help='linear scaling factor')
args = parser.parse_args()

if args.tidx is not None:
  tidx=int(args.tidx)
else:
  tidx = -1

if 'vrange' is not None:
  try:
    s1,s2 = args.vrange.split(',')
    vmin,vmax = float(s1),float(s2)
    uselim=True
  except:
    uselim=False
else:
  uselim=False

if args.title is not None:
  titlestr=unicode(args.title)
else:
  titlestr=args.varname

if args.units is not None:
  unitsstr=replace_superscripts(args.units)
else:
  unitsstr=''

if args.scalefactor is not None:
  fac = float(args.scalefactor)
else:
  fac=1.0

ncfile = args.ncfile
varn = args.varname
period = ncfile.split('.nc')[0].split('_')[-1]

nc = netCDF4.Dataset('zcor_%s.nc'%period)
ncv = nc.variables

depth = ncv['depth'][0:]
x = ncv['SCHISM_hgrid_node_x'][0:]
y = ncv['SCHISM_hgrid_node_y'][0:]
try:
  lmin = ncv['node_bottom_index'][0:]
except:
  zvar = ncv['zcor'][0]
  lmin = zeros(x.shape,dtype='int')
  for i in range(len(x)):
    try:
      lmin[i] = max(where(zvar.mask[i])[0])
    except:
      lmin[i] = 0
  lmin = lmin+1

znum = len(nc.dimensions['nSCHISM_vgrid_layers'])

nc.close()


znc = netCDF4.Dataset('zcor_%s.nc'%period)
zncv = nc.variables
zv = zncv['zcor']

nc = netCDF4.Dataset(ncfile)
ncv=nc.variables
sv = ncv[varn]
tnum,pnum,zznum=sv.shape
#s = ma.masked_equal(s,-9999.)
time = ncv['time'][:] # s
ut = utime(ncv['time'].units)
dates = ut.num2date(time)

levels=arange(znum)

if False: #os.path.isfile('xy_tree.pickle'):
    (tree,)=np.load('xy_tree.pickle')
else:
    tree = cKDTree(zip(x,y))
    try:
      f=open('xy_tree.pickle','wb')
      pickle.dump((tree,),f)
      f.close()
    except:
      pass

if False:
  lat0 = 55.0
  lonmin=3.0
  lonmax=8.7
  xtrans = linspace(lonmin,lonmax,500.)
  ytrans = lat0*ones(xtrans.shape)
else:
  latmin=47.0
  latmax=51.0
  lonmin=-9
  lonmax=-6.5
  xtrans = linspace(lonmin,lonmax,200.)
  ytrans = linspace(latmin,latmax,200.)

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

dist,inds = tree.query(zip(xtrans,ytrans),k=10)
weight = 1.0/dist**2


strans=ma.masked_equal(ones((len(dist[:,0]),znum)),0.0)
ztrans=ones((len(dist[:,0]),znum))
lmintrans=ones((len(dist[:,0])),dtype='int')

os.system('mkdir -p %s'%varn)
for tidx,t in enumerate(dates):

  tidx = tidx+tidx_offset
  s = sv[tidx]
  #s = ma.masked_equal(s,-9999.)
  z = zv[tidx]
  z.mask[where(z==0.0)]=True
  z.mask[isnan(z)]=True
  zf = z.copy()
  #z = ma.masked_equal(z,-9999.)
  print('  tidx %03d'%tidx)
  #lmintrans = lmin[inds].mean(axis=1)
  for n in range(znum-1,-1,-1):
    #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    strans[:,n] = s[inds,n].mean(axis=1)
    ztrans[:,n] = z[inds,n].mean(axis=1)
  for i in range(len(dist[:,0])):
    bidx = ztrans[i,:].argmin()
    ztrans[i,:bidx] = ztrans[i,bidx]
  
  #strans = ma.masked_where(strans<-5.0,strans)

  l2d,x2d = meshgrid(levels,xtrans)

  figure(figsize=(15,5))

  # fill z-levels
  #for n in range(len(depth)):
  #  nidx = where(zf.mask[n,:])
  #  zf[n,nidx] = zf[n,lmin[n]]

  plot_grid=True
  gridcol=(0.5,0.5,0.5)
  cmap=cm.YlGnBu_r
  cmap=cm.RdYlBu_r
  sfac=1.0

  if uselim:
    climmin=vmin
    climmax=vmax
  else:
    climmin=strans.min()
    climmax=strans.max()
  ctitle = titlestr+'\n[%s]'%unitsstr

  if varn == 'diffusivity':
    norm=matplotlib.colors.LogNorm(vmin=climmin,vmax=climmax)
  else:
    norm=matplotlib.colors.Normalize(vmin=climmin,vmax=climmax)

  pc = pcolormesh(x2d,ztrans,fac*strans,shading='interp',cmap=cmap,norm=norm)

  if plot_grid:
    #for yy,zz in zip(x2d,ztrans.squeeze()):
    #  plot(yy,zz,'k-',lw=0.3,color=gridcol)

    for yy,zz in zip(x2d.T,ztrans.squeeze().T):
      plot(yy,zz,'k-',lw=0.3,color=gridcol)


  cb=colorbar(pc)
  cb.set_label(ctitle)

  xlim(lonmin,lonmax)
  ylim(-200.,3.0)
  #clim(sfac*climmin,sfac*climmax)
  xlabel('lon [degE]')
  ylabel('z [m]')

  tstring = t.strftime('%Y%m%d-%H%M')
  savefig('%s/transect_%s_%s.png'%(varn,varn,tstring),dpi=300)
  show()
  #close()

