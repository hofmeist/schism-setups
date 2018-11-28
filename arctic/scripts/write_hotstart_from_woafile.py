import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
from pylab import *
import numpy as np
import netCDF4
from scipy.spatial import cKDTree
from hycomdata import hycom


if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = '/work/gg0877/g260095/NATa1.00/expt_01.0/data/test_withmb/archm.2005_mm.nc'

  a = schism_setup()
  h = hycom(ncfile=ncfile)
  ecosmo_tracers=[]

  if len(sys.argv)>1:
    hotstart_filename=sys.argv[1]
  else:
    hotstart_filename='/work/gg0877/hofmeist/arctic/input/hotstart_auto.nc'
    hotstart_filename='hotstart.nc'

  a.create_hotstart(ntracers=2+len(ecosmo_tracers),filename=hotstart_filename)
  tr_nd = zeros((a.znum,2+len(ecosmo_tracers)))

  # create t,s fields:
  for nodeid,nodelon,nodelat,d in zip(a.inodes,a.lon,a.lat,a.depths):
    tr_nd[:,:] = 0.0
    if (nodeid%1000) == 0:
      print('  interpolate i = %d'%nodeid)
      a.hotstart_nc.sync()

    depths = a.vgrid[nodeid].filled(-1)*d
    bidx = a.bidx[nodeid]
    t,s = h.interpolate(depths,nodelon,nodelat,tidx=0,bidx=1)
    tr_nd[:,0] = t
    tr_nd[:,1] = s
    a.write_hotstart_tracers_on_nodes(nodeid-1,tr_nd)

  a.hotstart_nc.sync()
  a.fill_hotstart_tracers_from_nodes()
  a.close_hotstart()

