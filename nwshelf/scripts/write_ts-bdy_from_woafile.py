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


class woa(object):

  def __init__(self,ncfile='woa13_decav_04v2.nc'):
    nc = netCDF4.Dataset(ncfile)
    sv = nc.variables
    latslice=slice(173,262) # 45.-67.
    lonslice=slice(320,455) # -20.-13.625
    self.lon = sv['lon'][lonslice]
    self.lat = sv['lat'][latslice]
    self.d = -sv['depth'][:]
    self.time = sv['time'][:]
    self.timeunits = sv['time'].units
    self.s = sv['s_mn'][:,:,latslice,lonslice]
    self.t = sv['t_mn'][:,:,latslice,lonslice]
    self.lon2,self.lat2 = meshgrid(self.lon,self.lat)

    if True:
      self.s_tree={}
      self.t_tree={}
      self.s_var={}
      self.t_var={}
      for tidx,time in enumerate(self.time):
        print('  build trees for month=%d'%(tidx+1))
        self.d3,self.lat3,self.lon3 = meshgrid(self.d,self.lat*100.,self.lon*100.,indexing='ij')
        vlon3 = self.lon3[where(self.s.mask[tidx]==False)]
        vlat3 = self.lat3[where(self.s.mask[tidx]==False)]
        vd3 = self.d3[where(self.s.mask[tidx]==False)]
        self.s_tree[tidx]=cKDTree(zip(vlon3,vlat3,vd3))

        vlon3 = self.lon3[where(self.t.mask[tidx]==False)]
        vlat3 = self.lat3[where(self.t.mask[tidx]==False)]
        vd3 = self.d3[where(self.t.mask[tidx]==False)]
        self.t_tree[tidx]=cKDTree(zip(vlon3,vlat3,vd3))

        self.s_var[tidx] = self.s[tidx][where(self.s.mask[tidx]==False)].flatten()
        self.t_var[tidx] = self.t[tidx][where(self.t.mask[tidx]==False)].flatten()
		

  def interpolate(self,depths,nodelon,nodelat,month=1,bidx=1):
    # start
    t = zeros((len(depths),))
    s = zeros((len(depths),))


    for ik,ndepth in enumerate(depths[bidx-1:]):
        # find vertical layer in climatology
        dist,inds = self.s_tree[month].query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        s[bidx-1+ik] = np.sum(w*self.s_var[month][inds],axis=0) / np.sum(w,axis=0)

        dist,inds = self.t_tree[month].query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        t[bidx-1+ik] = np.sum(w*self.t_var[month][inds],axis=0) / np.sum(w,axis=0)

    return (t,s)

if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = 'woa13_decav_04v2.nc'

  try:
    UseSetup = bool(sys.argv[2])
  except:
    UseSetup = True

  if UseSetup:
    nws = schism_setup()
    bdyvgrid = asarray([nws.vgrid[ii].filled(-1.) for ii in nws.bdy_nodes ])

  oa = woa(ncfile=ncfile)

  tbdy=[]
  sbdy=[]
  dbdy=[]
  ibdy=[]
  tprev=[]
  sprev=[]

  if UseSetup:
    f_temp = open('TEM_3D.th','wb')
    f_salt = open('SAL_3D.th','wb')

  # one year
  years=[2012,2013,2014,2015]
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
#from netcdftime import utime
#years = [2010,2011,2012]
#years = [2010]
#ut = utime('seconds since $d-01-01 00:00:00'%years[0])
#climut = utime(oa.timeunits)
#for yy in years:
#  if yy == years[0]:
#    climtimes = [0.0].append(oa.time)
#  for climtime in oa.time:
#    clim_dt = climut.num2date()-climut.num2date(climut.origin)
#    time = ut.date2num(datetime(yy,1,1,0,0,0)+clim_dt).astype('float32')
    if UseSetup:
      if month==-1:
        imonth=prevmonth+1
        if imonth==12: imonth=0
      else:
        prevmonth=month
        imonth=month
        tprev=[]
        sprev=[]
      time.tofile(f_temp)
      time.tofile(f_salt)
      for i,inode in enumerate(nws.bdy_nodes):
        if (i%100) == 0:
          print('  interpolate i = %d'%i)
        bdylon = nws.londict[inode]
        bdylat = nws.latdict[inode]
        depths = nws.vgrid[inode].filled(-1)*nws.depthsdict[inode]
        t,s = oa.interpolate(depths,bdylon,bdylat,month=imonth,bidx=1)
        if month==-1:
          tfinal = (t + tprev[i])*0.5
          sfinal = (s + sprev[i])*0.5
        else:
          tfinal = t
          sfinal = s
          tprev.append(t)
          sprev.append(s)
        tbdy.append(tfinal)
        sbdy.append(sfinal)
        dbdy.append(depths)
        ibdy.append(i*ones(depths.shape))
        tfinal.astype('float32').tofile(f_temp)
        sfinal.astype('float32').tofile(f_salt)
    else:
      depths=[-3000.,-2000.,-1000,-500,-200.,-100,-50,-25,-12,-6]
      t,s = oa.interpolate(depths,-18.,50.0,month=month,bidx=1)
      tbdy.append(t)
      sbdy.append(s)
      dbdy.append(depths)

  if UseSetup:
    f_temp.close()
    f_salt.close()
    

  tbdy=asarray(tbdy)
  sbdy=asarray(sbdy)
  dbdy=asarray(dbdy)
  ibdy=asarray(ibdy)

  timebdy=asarray(times)

  import pickle
  f = open('bdy.pickle','wb')
  pickle.dump((timebdy,ibdy,dbdy,sbdy,tbdy),f,protocol=-1)
  f.close()
