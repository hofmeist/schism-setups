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


if __name__ == '__main__':

  from woadata import woa
  ncfile = '/work/gg0877/KST/MiMeMo/woa/woa_arctic_0.25.nc'

  UseSetup = True

  if False:
    oa = []
    for tidx in range(12):
      oa.append( woa(ncfile=ncfile,tidx=tidx) )

  if UseSetup:
    a = schism_setup()
    bdyvgrid = asarray([a.vgrid[ii].filled(-1.) for ii in a.bdy_nodes ])
  
  f = open('bdy_coordinates.dat','w')
  for i,inode in enumerate(a.bdy_nodes):
    f.write('%d %d %0.3f %0.3f\n'%(i,inode,a.londict[inode],a.latdict[inode]))
  f.close()

  if False:
    temp=[]
    salt=[]
    dbdy=[]
    ibdy=[]
    tprev=[]
    sprev=[]

    # one year
    years=[2012,2013,2014,2015,2016,2017,2018]
    times = [0.0]
    months = [0] # set 1 Jan to data from 15 Jan
    ut = netcdftime.utime('seconds since %d-01-01 00:00:00'%years[0])
    for year in years:
      yearoffset = ut.date2num(datetime(year,1,1,0,0,0))
      times.extend(list(arange(0.5,12.1,0.5)*365./12.*86400.+yearoffset))
      for m in range(12):
        months.extend([m,-1])
    # look at times, before proceed
    plot(times)
    show()
  
    prevmonth=11
    for month,time in zip(months,array(times).astype('float32')):

     if UseSetup:
      if month==-1:
        imonth=prevmonth+1
        if imonth==12: imonth=0
      else:
        prevmonth=month
        imonth=month
        tprev=[]
        sprev=[]
      s2d=[]
      t2d=[]
      d2d=[]
      i2d=[]
      for i,inode in enumerate(a.bdy_nodes):
        if (i%100) == 0:
          print('  interpolate i = %d'%i)
        bdylon = a.londict[inode]
        bdylat = a.latdict[inode]
        depths = a.vgrid[inode].filled(-1)*a.depthsdict[inode]
        t,s = oa[imonth].interpolate(depths,bdylon,bdylat,bidx=1)
        if month==-1:
          tfinal = (t + tprev[i])*0.5
          sfinal = (s + sprev[i])*0.5
        else:
          tfinal = t
          sfinal = s
          tprev.append(t)
          sprev.append(s)
        t2d.append(tfinal)
        s2d.append(sfinal)
        d2d.append(depths)
        i2d.append(i*ones(depths.shape))
      salt.append(asarray(s2d))
      temp.append(asarray(t2d))
      dbdy.append(asarray(d2d))
     else:
      depths=[-3000.,-2000.,-1000,-500,-200.,-100,-50,-25,-12,-6]

      if month==-1:
        imonth=prevmonth+1
        if imonth==12: imonth=0
      else:
        prevmonth=month
        imonth=month
        tprev=0.0
        sprev=0.0
      t,s = oa[imonth].interpolate(depths,3.0,70.0,bidx=1)
      if month==-1:
          tfinal = (t + tprev)*0.5
          sfinal = (s + sprev)*0.5
      else:
          tfinal = t
          sfinal = s
          tprev=t
          sprev=s
      tbdy.append(tfinal)
      sbdy.append(sfinal)
      dbdy.append(depths)

  if False:
    a.write_bdy_netcdf('SAL_3D.th.nc',asarray(times),asarray(salt).reshape(len(times),a.num_bdy_nodes,a.znum,1))
    a.write_bdy_netcdf('TEM_3D.th.nc',asarray(times),asarray(temp).reshape(len(times),a.num_bdy_nodes,a.znum,1))

