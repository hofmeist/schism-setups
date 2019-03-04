import netCDF4
import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
#from find_nearest_node import get_nearest_node
from schism import schism_setup,schism_output

stations=['Andenes','Honningvag','NyAlesund','Vardo']

s = schism_setup()
so = schism_output('/work/gg0877/hofmeist/arctic/arctic007/2012-02/schout_2.nc')

f = open('stations.dat','w')
f.write('# name lon lat hgrid_idx schout_idx\n')

datapath='/work/gg0877/KST/MiMeMo/tide_gaughes/'

for station in stations:
  nc = netCDF4.Dataset(datapath+station+'.nc')
  ncv = nc.variables

  lon = float(ncv['lon'][:])
  lat = float(ncv['lat'][:])

  # find index in hgrid
  hgrid_idx = s.find_nearest_node(lon,lat)
  
  # find index in output
  schout_idx = so.find_nearest_node(lon,lat)

  f.write('%s %0.3f %0.3f %d %d\n'%(station,lon,lat,hgrid_idx,schout_idx))

so.nc.close()
  
