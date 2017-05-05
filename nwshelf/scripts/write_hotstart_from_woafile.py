import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
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
    self.lon = sv['lon'][lonslice]
    self.lat = sv['lat'][latslice]
    self.d = -sv['depth'][:]
    self.time = sv['time'][:]
    self.tidx = 0
    self.s = sv['s_mn'][:,:,latslice,lonslice]
    self.t = sv['t_mn'][:,:,latslice,lonslice]
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

    return (t.astype(np.float32),s.astype(np.float32))


nws = schism_setup()
oa = woa(ncfile=sys.argv[1])

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
    t[i],s[i] = oa.interpolate(depths,nodelon,nodelat,bidx=1)

  #write pickle
  #f = open('ts.pickle','wb')
  #pickle.dump((t,s),f)
  #f.close()

tracers=[]
tracers=['no3','nh4','pho','sil','oxy','dia','fla','bg','microzoo','mesozoo','det','opa','dom']
tracer_conc_const={'no3':5.0, \
                   'nh4':0.1, \
                   'pho':0.3, \
                   'sil':5.0, \
                   'oxy':85.0, \
                   'dia':1.0e-6, \
                   'fla':1.0e-6, \
                   'bg':1.0e-6, \
                   'microzoo':1.0e-6, \
                   'mesozoo':1.0e-6, \
                   'det':2.0, \
                   'opa':2.0, \
                   'dom':3.0}

redf1=6.625
redf6=12.01
redf3=6.625
redf2=106.0
tracer_factor={'no3': redf1*redf6,\
               'nh4': redf1*redf6,\
               'pho': redf2*redf6,\
               'sil': redf3*redf6,\
               'oxy': 1.0,\
               'dia': redf1*redf6,\
               'fla': redf1*redf6,\
               'bg': redf1*redf6,\
               'microzoo': redf1*redf6,\
               'mesozoo': redf1*redf6,\
               'det': redf1*redf6,\
               'opa': redf3*redf6,\
               'dom': redf1*redf6}

tracer_conc_element={} # to be filled later


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
  for tracer in tracers:
    #trcoll = [tracer_conc[ind] for ind in inds]
    #tracer_conc_element[tracer] = np.mean(trcoll,axis=0)
    tracer_conc_element[tracer] = tracer_factor[tracer]*tracer_conc_const[tracer]*ones(se.shape) 
  for k in range(nws.znum):
    valuelist = [0.0,te[k],se[k]]
    # if tracers are used:
    for tracer in tracers:
      valuelist.append(tracer_conc_element[tracer][k])
    asarray(valuelist).astype('float64').tofile(f)

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
    valuelist = [t[i][k],s[i][k]]
    for tracer in tracers:
      valuelist.append(tracer_conc_const[tracer])
    valuelist.extend([t[i][k],s[i][k]])
    for tracer in tracers:
      valuelist.append(tracer_conc_const[tracer])
    valuelist.extend([0.0,0.0,0.0,0.0,0.0,0.0,0.0])

    asarray(valuelist).astype('float64').tofile(f)

f.close()

