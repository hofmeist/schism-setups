import os
import sys
from pylab import *
import numpy as np
import netCDF4
from scipy.spatial import cKDTree
import netcdftime
from datetime import datetime


class aviso(object):

  def __init__(self,ncfile='na_aviso_2012.nc'):
    self.sshname='adt_mean'
    self.lonname='lon'
    self.latname='lat'
    self.timename='time'

    nc = netCDF4.Dataset(ncfile)
    sv = nc.variables
    self.ncv = sv
    xslice=slice(None)
    yslice=slice(None)
    self.lon = sv[self.lonname][xslice]
    self.lat = sv[self.latname][yslice]
    self.lon2,self.lat2 = np.meshgrid(self.lon,self.lat)
    self.time = sv[self.timename][:]
    self.timeunits = sv[self.timename].units
    self.ut = netcdftime.utime(self.timeunits)
    self.dates = self.ut.num2date(self.time)
    self.ssh = sv[self.sshname][yslice,xslice]

    print('  build spatial tree')
    self.mask = self.ssh.mask.squeeze()
    self.water = where(self.mask==False)
    vlon2 = self.lon2[self.water]
    vlat2 = self.lat2[self.water]
    self.tree = cKDTree(zip(vlon2,vlat2))


  def interpolate(self,nodelon,nodelat,tidx=0):

    dist,inds = self.tree.query((nodelon,nodelat),k=3)
    w = 1/dist
    return (sum(self.ssh[self.water][inds]*w)/sum(w))


if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = '/work/gg0877/hofmeist/aviso/na_aviso_2012.nc'

  h = aviso(ncfile=ncfile)

  lons=[-8.,14.,25.]
  lats=[70.,65.,83.]

  for lon,lat in zip(lons,lats):
    ssh = h.interpolate(lon,lat,tidx=0)
    print('lonlat=(%0.1f,%0.1f) = %0.3fm'%(lon,lat,ssh))

