import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_output

def get_nearest_node(filename,lon,lat):
  s = schism_output(filename)
  s.init_node_tree()
  idx = s.find_nearest_node(lon.lat)
  s.nc.close()
  return idx

if __name__ == '__main__':

  if len(sys.argv)<3:
    print('usage find_station_in_output.py schout_name.nc lon,lat')

  filename = sys.argv[1]
  lon,lat = [float(n) for n in sys.argv[2].split(',')]

  idx = iget_nearest_node(filename,lon,lat)

  print(' Index for lon=%0.2f,lat=%0.2f is %d'%(lon,lat,idx))

