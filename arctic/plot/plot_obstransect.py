import matplotlib
matplotlib.use('Agg')
import sys
sys.path.append('/pf/g/g260078/pythoninstall/pythonlib')
#from plotting import cm_Parula

from pylab import *
import netCDF4
from scipy.spatial import cKDTree 
import os
import argparse
from netcdftime import utime
import numpy as np
import pickle as pickle

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
parser.add_argument('-fname', help='file name string')
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

if args.fname is not None:
  fnamestr=args.fname
else:
  fnamestr=args.varname

ncfile = args.ncfile
varn = args.varname
period = ncfile.split('.nc')[0].split('_')[-1]
separate_files=False
if separate_files:
  zfile = 'zcor_%s'%period
else:
  zfile = ncfile

nc = netCDF4.Dataset(zfile)
ncv = nc.variables

depth = ncv['depth'][0:]
x = ncv['SCHISM_hgrid_node_x'][0:]
y = ncv['SCHISM_hgrid_node_y'][0:]
z = ncv['zcor'][0,:,0:]
#z = ma.masked_equal(z,-9999.)
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


znc = netCDF4.Dataset(zfile)
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
    tree = cKDTree(list(zip(x,y)))
    try:
      f=open('xy_tree.pickle','wb')
      pickle.dump((tree,),f)
      f.close()
    except:
      pass

if fnamestr=='obs':
  onc = netCDF4.Dataset('/work/gg0877/hofmeist/arctic/echosounder/PS106_data.nc')
  olon = onc.variables['lon'][:]
  olat = onc.variables['lat'][:]
  odays = onc.variables['time'][:]
  odays = odays - odays[0]
  odepth = onc.variables['depth'][:]
  sv_mean = onc.variables['sv_mean'][:]

  ylimmin=-760.
  plotgrid=False
else:
  latmin=74.0
  latmax=74.0
  lonmin=-20.5
  lonmax=60.0
  ylimmin=-4000.
  ntransect=500
  plotgrid=False
  

if False:
  if (latmax-latmin)<(lonmax-lonmin):
    uselon=True
  else:
    uselon=False
  xtrans = linspace(lonmin,lonmax,ntransect)
  ytrans = linspace(latmin,latmax,ntransect)
else:
  xtrans = olon
  ytrans = olat

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

dist,inds = tree.query(list(zip(xtrans,ytrans)),k=10)
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
  zf = z.copy()
  #z = ma.masked_equal(z,-9999.)
  print('  tidx %03d'%tidx)
  #lmintrans = lmin[inds].mean(axis=1)
  for n in range(znum-1,-1,-1):
    #strans[:,n] = np.sum(weight * s[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    #ztrans[:,n] = np.sum(weight * z[tidx,n,inds],axis=1)/np.sum(weight,axis=1)
    strans[:,n] = s[inds,n].mean(axis=1)
    ztrans[:,n] = z[inds,n].mean(axis=1)
  #for i in range(len(lmintrans)):
  #  ztrans[i,:lmintrans[i]] = ztrans[i,lmintrans[i]]
  
  #strans = ma.masked_where(strans<-5.0,strans)

  l2d,x2d = meshgrid(levels,odays)

  figure(figsize=(25,10))

  subplot(211)

  # fill z-levels
  #for n in range(len(depth)):
  #  nidx = where(zf.mask[n,:])
  #  zf[n,nidx] = zf[n,lmin[n]]

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
    norm=matplotlib.colors.Normalize(vmin=sfac*climmin,vmax=sfac*climmax)

  pc = pcolormesh(x2d,ztrans,sfac*strans,shading='interp',cmap=cmap,norm=norm)

  if plotgrid:
    #for yy,zz in zip(x2d,ztrans.squeeze()):
    #  plot(yy,zz,'k-',lw=0.3,color=gridcol)

    for yy,zz in zip(x2d.T,ztrans.squeeze().T):
      plot(yy,zz,'k-',lw=0.3,color=gridcol)


  cb=colorbar(pc)
  cb.set_label(ctitle)

  xlim(0,25)
  xlabel('day of cruise PS106')
  ylim(ylimmin,3.0)
  #clim(sfac*climmin,sfac*climmax)
  ylabel('z [m]')

  subplot(212)

  pcolormesh(odays,-odepth,sv_mean.T,shading='interp',cmap=cm.jet)
  clim(-100,0.0)
  xlim(0,25)
  xlabel('day of cruise PS106')
  colorbar(label='Sv')

  tstring = t.strftime('%Y%m%d-%H%M')
  savefig('jpgs/%s/transect_%s_%s_%s.png'%(varn,varn,fnamestr,tstring),dpi=300)
  #show()
  close()

