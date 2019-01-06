import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
from pylab import *
import numpy as np
import netCDF4
from scipy.spatial import cKDTree
import netcdftime
from datetime import datetime
from avisodata import aviso


if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = '/work/gg0877/hofmeist/aviso/na_aviso_2012.nc'

  try:
    UseSetup = bool(sys.argv[2])
  except:
    UseSetup = True

  if UseSetup:
    nws = schism_setup()
    h = aviso(ncfile)
    times=[]
    elev=[]
    elev2d=[]

    ut = netcdftime.utime('seconds since 2012-01-01 00:00:00')
    all_times = ut.date2num([datetime(2012,1,1,0,0,0),datetime(2020,1,1,0,0,0)])

    for tidx,time in enumerate(all_times):
      elev=[]
      
      for i,inode in enumerate(nws.bdy_nodes):
        if (i%100) == 0:
          print('  interpolate i = %d'%i)
        bdylon = nws.londict[inode]
        bdylat = nws.latdict[inode]
        elev.append(h.interpolate(bdylon,bdylat))
      elev2d.append(asarray(elev))
      times.append(time)

    nws.write_bdy_netcdf('elev2D.th.nc',asarray(times),asarray(elev2d))

