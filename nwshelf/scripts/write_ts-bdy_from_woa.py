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
    self.d = -sv['depth'][:]
    self.time = sv['time'][:]
    self.timeunits = sv['time'].units
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

bdyvgrid = asarray([nws.vgrid[ii].filled(-1.) for ii in nws.bdy_nodes ])

tbdy=[]
sbdy=[]
dbdy=[]
ibdy=[]

f_temp = open('TEM_3D.th','wb')
f_salt = open('SAL_3D.th','wb')
for time in array([0.0,32*86400.]).astype('float32'):
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
    time.tofile(f_temp)
    time.tofile(f_salt)
    for i,inode in enumerate(nws.bdy_nodes):
      if (i%100) == 0:
        print('  interpolate i = %d'%i)
      bdylon = nws.londict[inode]
      bdylat = nws.latdict[inode]
      depths = nws.vgrid[inode].filled(-1)*nws.depthsdict[inode]
      t,s = oa.interpolate(depths,bdylon,bdylat,bidx=1)
      tbdy.append(t)
      sbdy.append(s)
      dbdy.append(depths)
      ibdy.append(i*ones(depths.shape))
      t.astype('float32').tofile(f_temp)
      s.astype('float32').tofile(f_salt)

f_temp.close()
f_salt.close()

tbdy=asarray(tbdy)
sbdy=asarray(sbdy)
dbdy=asarray(dbdy)
ibdy=asarray(ibdy)

