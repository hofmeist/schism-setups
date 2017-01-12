from numpy import *
import sys,os
import netCDF4
from scipy.spatial import cKDTree

try:
  ncfile = sys.argv[1]
except:
  print('usage: find_station.py ncfile')
  sys.exit(1)

stationfile='stations.dat'

stations={}
nodes={}
with open(stationfile) as f:
  for line in f.readlines():
    data = line.split()
    stations[data[0]] = (float(data[1]),float(data[2]))

nc = netCDF4.Dataset(ncfile)
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1

tree = cKDTree(zip(lon,lat))

of = open('stations_nodes.dat','w')
for station in stations:
  lon,lat=stations[station]
  d,idx = tree.query((lon,lat),k=1)
  nodes[station] = idx
  of.write('%s %0.2f %0.2f %d\n'%(station,lon,lat,idx) )
of.close()


