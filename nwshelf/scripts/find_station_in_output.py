from pylab import *
import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_output

if len(sys.argv)<3:
  print('usage find_station_in_output.py schout_name.nc lon,lat')

filename = sys.argv[1]
lon,lat = [float(n) for n in sys.argv[2].split(',')]

s = schism_output(filename)

s.init_node_tree()

idx = s.find_nearest_node(lon,lat)

print(' Index for lon=%0.2f,lat=%0.2f is %d'%(lon,lat,idx))

s.nc.close()
