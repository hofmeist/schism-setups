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
from hycomdata import hycom


if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = '/work/gg0877/g260095/NATa1.00/expt_01.0/data/test_withmb/archm.2005_mm.nc'

  try:
    UseSetup = bool(sys.argv[2])
  except:
    UseSetup = True

  if UseSetup:
    nws = schism_setup()
    bdyvgrid = asarray([nws.vgrid[ii].filled(-1.) for ii in nws.bdy_nodes ])

  h = hycom(ncfile=ncfile)

  if UseSetup:
    times=[]
    temp=[]
    salt=[]
    s2d=[]
    t2d=[]

    ut = netcdftime.utime('seconds since 2012-01-01 00:00:00')
    all_times = ut.date2num(h.dates)

    for tidx,time in enumerate(all_times):
      s2d=[]
      t2d=[]
      for i,inode in enumerate(nws.bdy_nodes):
        if (i%100) == 0:
          print('  interpolate i = %d'%i)
        bdylon = nws.londict[inode]
        bdylat = nws.latdict[inode]
        depths = -nws.vgrid[inode].filled(-1)*max(nws.depthsdict[inode],6.0)
        t,s = h.interpolate(depths,bdylon,bdylat,tidx=tidx,bidx=1)
        s2d.append(s)
        t2d.append(s)
      temp.append(asarray(t2d))
      salt.append(asarray(s2d))
      times.append(time)

    nws.write_bdy_netcdf('SAL_3D.th.nc',asarray(times),asarray(salt).reshape(len(times),nws.num_bdy_nodes,nws.znum,1))
    nws.write_bdy_netcdf('TEM_3D.th.nc',asarray(times),asarray(temp).reshape(len(times),nws.num_bdy_nodes,nws.znum,1))
      
  else:
    depths=-1.0*asarray([-3000.,-2000.,-1000,-500,-200.,-100,-50,-25,-12,-6])
    t,s = h.interpolate(depths,40,75.0,tidx=0,bidx=1)

