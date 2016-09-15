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
    tv = tnc.variables
    snc = netCDF4.Dataset('http://data.nodc.noaa.gov/thredds/dodsC/woa/WOA13/DATAv2/salinity/netcdf/decav/0.25/woa13_decav_s01_04v2.nc')
    sv = snc.variables
    latslice=slice(528,624)
    lonslice=slice(648,860)
    self.lon = sv['lon'][lonslice]
    self.lat = sv['lat'][latslice]
    self.d = sv['depth'][:]
    self.t = sv['time'][:]
    self.tidx = 0
    self.s = sv['s_mn'][:,:,latslice,lonslice]
    self.t = tv['t_mn'][:,:,latslice,lonslice]
    self.lon2,self.lat2 = meshgrid(self.lon,self.lat)

    self.use_depth_slices=False

    if not(self.use_depth_slices):
      self.d3,self.lat3,self.lon3 = meshgrid(self.d,self.lat*100.,self.lon*100.,indexing='ij')
      vlon3 = self.lon3[where(self.s.mask[self.tidx]==False)]
      vlat3 = self.lat3[where(self.s.mask[self.tidx]==False)]
      vd3 = self.d3[where(self.s.mask[self.tidx]==False)]
      self.s_tree=cKDTree(zip(vlon3,vlat3,vd3))

      vlon3 = self.lon3[where(self.t.mask[self.tidx]==False)]
      vlat3 = self.lat3[where(self.t.mask[self.tidx]==False)]
      vd3 = self.d3[where(self.t.mask[self.tidx]==False)]
      self.t_tree=cKDTree(zip(vlon3,vlat3,vd3))

      self.s_var = self.s[self.tidx][where(self.s.mask[self.tidx]==False)].flatten()
      self.t_var = self.t[self.tidx][where(self.t.mask[self.tidx]==False)].flatten()

    else:
      #build trees
      self.s_tree={}
      self.t_tree={}
      self.svar={}
      self.tvar={}
      for ik,d in enumerate(self.d):
        print('  build trees for depth %0.2f'%d)
        vlon = self.lon2[where(self.s.mask[self.tidx,ik]==False)]
        vlat = self.lat2[where(self.s.mask[self.tidx,ik]==False)]
        self.s_tree[ik] = cKDTree(zip(vlon,vlat))
        vlon = self.lon2[where(self.t.mask[self.tidx,ik]==False)]
        vlat = self.lat2[where(self.t.mask[self.tidx,ik]==False)]
        self.t_tree[ik] = cKDTree(zip(vlon,vlat))
        self.svar[ik] = self.s[self.tidx,ik][where(self.s.mask[self.tidx,ik]==False)].flatten()
        self.tvar[ik] = self.t[self.tidx,ik][where(self.t.mask[self.tidx,ik]==False)].flatten()

  def interpolate(self,depths,nodelon,nodelat,bidx=1):
    # start
    t = zeros((len(depths),))
    s = zeros((len(depths),))


    for ik,ndepth in enumerate(depths[bidx-1:]):
      # find vertical layer in climatology
      if self.use_depth_slices:
        didx = np.abs(self.d - ndepth).argmin()

      #didx = int(where(ddiff==ddiff.min())[0][0])
      #vlon = self.lon2[where(self.s.mask[self.tidx,didx]==False)]
      #vlat = self.lat2[where(self.s.mask[self.tidx,didx]==False)]
      #tree = cKDTree(zip(vlon,vlat))
    
      #svar = self.s[self.tidx,didx][where(self.s.mask[self.tidx,didx]==False)].flatten()
      #tvar = self.t[self.tidx,didx][where(self.t.mask[self.tidx,didx]==False)].flatten()

        dist,inds = self.s_tree[didx].query((nodelon,nodelat),k=4)
        w = 1 / dist
        s[bidx-1+ik] = np.sum(w*self.svar[didx][inds],axis=0) / np.sum(w,axis=0)

        dist,inds = self.t_tree[didx].query((nodelon,nodelat),k=4)
        w = 1 / dist
        t[bidx-1+ik] = np.sum(w*self.tvar[didx][inds],axis=0) / np.sum(w,axis=0)
      else:
        dist,inds = self.s_tree.query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        s[bidx-1+ik] = np.sum(w*self.s_var[inds],axis=0) / np.sum(w,axis=0)

        dist,inds = self.t_tree.query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        t[bidx-1+ik] = np.sum(w*self.t_var[inds],axis=0) / np.sum(w,axis=0)

    return (t,s)


nws = schism_setup()
oa = woa()

import os.path
import pickle

if os.path.isfile('ts.pickle'):
  t,s = pickle.load(open('ts.pickle','rb'))

else:
  # write t,s on nodes
  s = {}
  t = {}

  # create t,s fields:
  for i,nodelon,nodelat,d in zip(nws.inodes,nws.lon,nws.lat,nws.depths):
    if (i%10000) == 0:
      print('  interpolate i = %d'%i)
    #if i == 5000:
    #  break 
    depths = nws.vgrid[i].filled(-1)*d
    bidx = nws.bidx[i]
    t[i],s[i] = oa.interpolate(depths,nodelon,nodelat,bidx)

  #write pickle
  f = open('ts.pickle','wb')
  pickle.dump((t,s),f)
  f.close()


# finally write hotstart file:
f = open('hotstart.in','wb')
asarray([0.0]).astype('float64').tofile(f)
asarray([0,1]).astype('int32').tofile(f)

# write element data
for ie in nws.nvdict:
  asarray([ie,0]).astype('int32').tofile(f)
  inds = nws.nvdict[ie]
  scoll = [s[ind] for ind in inds]
  tcoll = [t[ind] for ind in inds]
  se = np.mean(scoll,axis=0)
  te = np.mean(tcoll,axis=0)
  for k in range(nws.znum):
    asarray([0.0,te[k],se[k]]).astype('float64').tofile(f)

for i in nws.side_nodes:
  asarray([i,0]).astype('int32').tofile(f)
  inds = nws.side_nodes[i]
  scoll = [s[ind] for ind in inds]
  tcoll = [t[ind] for ind in inds]
  se = np.mean(scoll,axis=0)
  te = np.mean(tcoll,axis=0)
  for k in range(nws.znum):
    asarray([0.0,0.0,te[k],se[k]]).astype('float64').tofile(f)

for i in nws.inodes:
  asarray([i]).astype('int32').tofile(f)
  asarray([0.0]).astype('float64').tofile(f)
  asarray([0]).astype('int32').tofile(f)
  for k in range(nws.znum):
    asarray([t[i][k],s[i][k],t[i][k],s[i][k],0.0,0.0,0.0,0.0,0.0,0.0,0.0]).astype('float64').tofile(f)

f.close()

