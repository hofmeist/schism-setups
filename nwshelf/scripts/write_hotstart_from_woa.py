import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
from pylab import *
import numpy as np
import netCDF4
from scipy.spatial import cKDTree

class woa():

  def __init__(self):
    tnc = netCDF4.Dataset('http://data.nodc.noaa.gov/thredds/dodsC/woa/WOA13/DATAv2/temperature/netcdf/decav/0.25/woa13_decav_t01_04v2.nc')
    tv = self.tnc.variables
    snc = netCDF4.Dataset('http://data.nodc.noaa.gov/thredds/dodsC/woa/WOA13/DATAv2/salinity/netcdf/decav/0.25/woa13_decav_s01_04v2.nc')
    sv = self.snc.variables
    latslice=slice(528,624)
    lonslice=slice(648,860)
    self.lon = ncv['lon'][lonslice]
    self.lat = ncv['lat'][latslice]
    self.d = ncv['depth'][:]
    self.t = ncv['time'][:]
    self.tidx = 0
    self.s = sv['s_mn'][:,:,latslice,lonslice]
    self.t = tv['t_mn'][:,:,latslice,lonslice]
    self.lon2,self.lat2 = meshgrid(self.lon,self.lat)

  def interpolate(depths,nodelon,nodelat,bidx=1):
    # start
    t = zeros((len(depths),))
    s = zeros((len(depths),))


    for ik,ndepth in enumerate(depths):
      # find vertical layer in climatology
      ddiff = abs(self.d - ndepth)
      didx = int(where(ddiff==ddiff.min())[0][0])
      vlon = self.lon2[where(self.s.mask[tidx,didx]==False)]
      vlat = self.lat2[where(self.s.mask[tidx,didx]==False)]
      tree = cKDTree(zip(vlon,vlat))
    
      svar = self.s[tidx,didx][where(self.s.mask[tidx,didx]==False)].flatten()
      tvar = self.t[tidx,didx][where(self.t.mask[tidx,didx]==False)].flatten()

      dist,inds = tree.query(nodelon,nodelat),k=4)
      w = 1 / dist
      s[bidx-1+ik] = np.sum(w*svar[inds],axis=0) / np.sum(w,axis=0)
      t[bidx-1+ik] = np.sum(w*tvar[inds],axis=0) / np.sum(w,axis=0)

    return (t,s)


nws = schism_setup()

# write t,s on nodes
s = {}
t = {}

# create t,s fields:
for i,nodelon,nodelat,d in zip(cbs.inodes,cbs.lon,cbs.lat,cbs.depths):
  depths = cbs.vgrid[i].filled(-1)*d
  bidx = nws.bixd[i]
  t[i],s[i] = interpolate_from_woa(depths,nodelon,nodelat,bidx)


# finally write hotstart file:
f = open('hotstart.in','wb')
asarray([0.0]).astype('float64').tofile(f)
asarray([0,1]).astype('int32').tofile(f)

# write element data
for ie in cbs.nvdict:
  asarray([ie,0]).astype('int32').tofile(f)
  inds = cbs.nvdict[ie]
  scoll = [s[ind] for ind in inds]
  tcoll = [t[ind] for ind in inds]
  se = np.mean(scoll,axis=0)
  te = np.mean(tcoll,axis=0)
  for k in range(cbs.znum):
    asarray([0.0,te[k],se[k]]).astype('float64').tofile(f)

for i in cbs.side_nodes:
  asarray([i,0]).astype('int32').tofile(f)
  inds = cbs.side_nodes[i]
  scoll = [s[ind] for ind in inds]
  tcoll = [t[ind] for ind in inds]
  se = np.mean(scoll,axis=0)
  te = np.mean(tcoll,axis=0)
  for k in range(cbs.znum):
    asarray([0.0,0.0,te[k],se[k]]).astype('float64').tofile(f)

for i in cbs.inodes:
  asarray([i]).astype('int32').tofile(f)
  asarray([0.0]).astype('float64').tofile(f)
  asarray([0]).astype('int32').tofile(f)
  for k in range(cbs.znum):
    asarray([t[i][k],s[i][k],t[i][k],s[i][k],0.0,0.0,0.0,0.0,0.0,0.0,0.0]).astype('float64').tofile(f)

f.close()

