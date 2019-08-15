from pylab import *
import netCDF4
import sys,os
from matplotlib.ticker import FormatStrFormatter

if len(sys.argv)>1:
  path=sys.argv[1]
else:
  path='/work/gg0877/hofmeist/nwshelf/nwshelfmix01'

label_days=True

stations=['CelticSea_St1','CelticSea_St2','CelticSea_St4','CelticSea_St5','Malin_SE']
#stations=['Malin_SE']
yyyymm='2012-06'

def ncvariables(station,yyyymm,var):
  ncfile='%s/stations/%s/%s_%s_%s.nc'%(path,station,station,var,yyyymm)
  nc=netCDF4.Dataset(ncfile)
  return nc.variables

for station in stations:

  if station=='Malin_SE':
    startx,endx = 4,19
  else:
    startx,endx = 12,28
  zmin,zmax = -120,5.0

  zncv = ncvariables(station,yyyymm,'zcor')
  #sncv = ncvariables(station,yyyymm,'sigmat')
  tncv = ncvariables(station,yyyymm,'temp')
  dncv = ncvariables(station,yyyymm,'diffusivity')

  days = (zncv['time'][:]-zncv['time'][0])/86400.


  #sigmat = sncv['sigma_t'][:,:].squeeze()
  temp = tncv['temp'][:,:].squeeze()
  dff = dncv['diffusivity'][:,:].squeeze()
  zcor = zncv['zcor'][:,:].squeeze()
  zcor[where(isnan(zcor))] = 0.0
  zcor = ma.masked_equal(zcor,0.0)
  depth=zcor.min()
  years_array,tmp = meshgrid(days,zcor[0].squeeze())


  xlabelstr='days'

  f = figure(figsize=(14,6))
  arr = 210
  num=0

  if False:
   num+=1
   subplot(arr+num)
   pcolor(years_array,zcor.T,sigmat.T)
   ylim(depth,2)
   title('density')
   xlim(startx,endx)
   ylim(zmin,zmax)
   colorbar()


  if True:
   num+=1
   subplot(arr+num)
   contourf(years_array,zcor.T,temp.T,20)
   #ylim(depth,2)
   #title('temperature')
   xlim(startx,endx)
   ylim(zmin,zmax)
   colorbar(label=u'temperature [\u00b0C]')

  if True:
   num+=1
   subplot(arr+num)
   contourf(years_array,zcor.T,dff.T,20,norm=matplotlib.colors.LogNorm(0.000001,1.))
   #ylim(depth,2)
   #title('diffusivity')
   gca().xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
   xlim(startx,endx)
   ylim(zmin,zmax)
   colorbar(label=u'diffusivity [m\u00b2/s]')


  savefig('%s/stations/%s_%s_profiles.pdf'%(path,station,yyyymm))
  show()

