import os
import sys
from pylab import *
import numpy as np
import netCDF4
from scipy.spatial import cKDTree

class woa():

  def __init__(self,ncfile='woa13_devac_04v2.nc'):
    nc = netCDF4.Dataset(ncfile)
    sv = nc.variables
    latslice=slice(173,262)
    lonslice=slice(320,524)
    latslice=slice(None,None)
    lonslice=slice(None,None)
    self.lon = sv['lon'][lonslice]
    self.lat = sv['lat'][latslice]
    self.d = -sv['depth'][:]
    self.time = sv['time'][:]
    self.tidx = 0
    self.s = sv['s_mn'][:,:,latslice,lonslice]
    self.t = sv['t_mn'][:,:,latslice,lonslice]
    self.lon2,self.lat2 = meshgrid(self.lon,self.lat)

    self.use_depth_slices=True

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
        #print('  build trees for depth %0.2f'%d)
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

    return (t.astype(np.float32),s.astype(np.float32))


if __name__=='__main__':

  #oa = woa(ncfile=sys.argv[1])
  oa = woa(ncfile='/work/gg0877/KST/MiMeMo/woa/woa_arctic_0.25.nc')

  depths=asarray([-5000.,-4000.,-3000.,-2000.,-1000.,-500.,-250.,-100.,0.0])
  nodelon=40.0
  nodelat=70.0

  t,s = oa.interpolate(depths,nodelon,nodelat,bidx=1)
  print('temp:')
  print(t)
  print('salt:')
  print(s)
