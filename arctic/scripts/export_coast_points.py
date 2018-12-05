import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
from pylab import *
import numpy as np
import netCDF4

s = schism_setup('hgrid.gr3')

lons = asarray([s.londict[ii] for ii in s.land_nodes ])
lats = asarray([s.latdict[ii] for ii in s.land_nodes ])
#ilats = asarray([s.latdict[ii] for ii in s.island_nodes ])
#ilons = asarray([s.londict[ii] for ii in s.island_nodes ])
num=len(lons)#+len(ilons)

nc = netCDF4.Dataset('schism_river_points.nc','w',format='NETCDF3_CLASSIC')
nc.createDimension('x',num)
nc.createDimension('y',1)

lonv = nc.createVariable('lon','f8',('y','x'))
lonv.units = 'degrees east'
lonv[:]=lons
#lonv[1:len(lons)]=lons
#lonv[len(lons):]=ilons


latv = nc.createVariable('lat','f8',('y','x'))
latv.units = 'degrees north'
latv[:]=lats
#latv[1:len(lats)]=lats
#latv[len(lats):]=ilats


mv = nc.createVariable('mask','f8',('y','x'))
mv.units = '1=water,0=land'
mv.coordinates = 'lon lat'
mv[:]=ones((1,num))

nc.close()
