from pylab import *
import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_output

if len(sys.argv)<3:
  print('usage find_station_in_output.py schout_name.nc stations.dat')

filename = sys.argv[1]
listname = sys.argv[2]

s = schism_output(filename)
s.init_node_tree()

fi = open(listname)
f = open('%s_schoutnodes.dat'%listname[:-4],'w')

for line in fi.readlines():
  dat = line.split()
  lon = float(dat[1])
  lat = float(dat[2])
  name = dat[0]
  idx = s.find_nearest_node(lon,lat)
  f.write('%s %0.2f %0.2f %d\n'%(name,lon,lat,idx))

f.close()
fi.close()
s.nc.close()
