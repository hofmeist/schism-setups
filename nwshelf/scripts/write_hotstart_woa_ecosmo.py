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
class ecosmo():

  def __init__(self,ncfile='ecosmoII.2012-01-01.nc'):
    nc = netCDF4.Dataset(ncfile)
    sv = nc.variables
    self.sv = sv
    latslice=slice(None)
    lonslice=slice(None)
    self.lon = sv['lon'][lonslice]
    self.lat = sv['lat'][latslice]
    self.no3 = sv['no3'][:,:,latslice,lonslice]
    dz = sv['ddzz'][:,83,77] # deepest point off Norway
    dz[-1] = dz[-2] # set last layer to same height as prelast for interpolation
    self.d = -dz.cumsum(axis=0)+0.5*dz
    self.time = sv['time'][:]
    self.tidx = 0
    self.lat2,self.lon2 = meshgrid(self.lat,self.lon)

    self.use_depth_slices=True
    self.prefetched=True 
    self.tv={}

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
      self.tree={}
      self.valmask={}
      for ik,d in enumerate(self.d):
        print('  build tree for depth %0.2f'%d)
        self.valmask[ik] = where(self.no3.mask[self.tidx,ik]==False)
        vlon = self.lon2[self.valmask[ik]]
        vlat = self.lat2[self.valmask[ik]]
        self.tree[ik] = cKDTree(zip(vlon,vlat))

  def prefetch_for_interpolation(self,tracers):
    if tracers==None:
      print('  ecosmo prefetch: give list of tracers')
      return
    for tr in tracers:
      self.tv[tr]={}
      for didx,d in enumerate(self.d):
        self.tv[tr][didx] = self.sv[tr][self.tidx,didx][self.valmask[didx]]
    self.prefetched=True 
    self.prefetched_tracers=tracers
 

  def interpolate(self,depths,nodelon,nodelat,bidx=1,tracers=None,factors=None):
    # start
    if tracers==None:
      print('  ecosmo interpolate: give list of tracers')
      return

    val = zeros((len(depths),len(tracers)))
    if factors==None:
      factors={key: 1.0 for key in tracers}

    if True:
     for ik,ndepth in enumerate(depths[bidx-1:]):
      # find vertical layer in climatology
      if self.use_depth_slices:
        didx = np.abs(self.d - ndepth).argmin()

        if False:
          dist,inds = self.tree[didx].query((nodelon,nodelat),k=4)
          newdidx = didx
        else:
          dist,inds = self.tree[didx].query((nodelon,nodelat),k=4)
          sdist,sinds = self.tree[0].query((nodelon,nodelat),k=4)
          newdidx=didx
          while sum(dist)>2.0*sum(sdist):
            newdidx=newdidx-1
          #print('  sum(dist) ratio: %0.2f, going one layer upwards to %d'%(sum(dist)/sum(sdist),newdidx))
            dist,inds = self.tree[newdidx].query((nodelon,nodelat),k=4)
        w = 1 / dist
        scaling = 1.0/np.sum(w,axis=0)
        # this step seems most time-consuming
        if self.prefetched:
          for trnum,trname in enumerate(tracers):
            val[bidx-1+ik,trnum] = factors[trname]*scaling*np.sum(w*self.tv[trname][newdidx][inds],axis=0)
        else:
          #masked_inds = where(self.sv['no3'][self.tidx,newdidx][self.valmask[newdidx]][inds]>-9999.)
          masked_inds = self.valmask[newdidx]
          for trnum,trname in enumerate(tracers):
            val[bidx-1+ik,trnum] = factors[trname]*scaling*np.sum(w*self.sv[trname][self.tidx,newdidx][masked_inds][inds],axis=0)

    return (val)

  def interpolate_var(self,varname,depths,nodelon,nodelat,bidx=1):
    # start
    val = zeros((len(depths),))

    for ik,ndepth in enumerate(depths[bidx-1:]):
      # find vertical layer in climatology
      if self.use_depth_slices:
        didx = np.abs(self.d - ndepth).argmin()

        dist,inds = self.tree[didx].query((nodelon,nodelat),k=4)
        sdist,sinds = self.tree[0].query((nodelon,nodelat),k=4)
        newdidx=didx
        while sum(dist)>2.0*sum(sdist):
          newdidx=newdidx-1
          #print('  sum(dist) ratio: %0.2f, going one layer upwards to %d'%(sum(dist)/sum(sdist),newdidx))
          dist,inds = self.tree[newdidx].query((nodelon,nodelat),k=4)
        w = 1 / dist
        val[bidx-1+ik] = np.sum(w*self.sv[varname][self.tidx,newdidx][self.valmask[newdidx]][inds],axis=0) / np.sum(w,axis=0)

    return (val)


nws = schism_setup()
#oa = woa(ncfile=sys.argv[1])
oa = woa(ncfile='/work/gg0877/hofmeist/nwshelf/input/woa13_decav_04v2.nc')
e  = ecosmo(ncfile='/work/gg0877/hofmeist/nwshelf/input/ecosmoII.2012-01-01.nc')

import os.path
import pickle

if os.path.isfile('ts.pickle'):
  t,s = pickle.load(open('ts.pickle','rb'))

else:
  # write t,s on nodes
  s = {}
  t = {}

  tracers=['no3','nh4','pho','sil','oxy','dia','fla','bg','microzoo','mesozoo','det','opa','dom']
  ecosmo_tracers=['no3','nh4','po4','sio','o2','diat','flags','cyan','zoos','zool','det','det','dom'] #'opa'?
  #ecosmo_tracers=[] 
  tracer_conc_const={'no3':5.0, \
                   'nh4':0.1, \
                   'pho':0.3, \
                   'po4':0.3, \
                   'sil':5.0, \
                   'sio':5.0, \
                   'oxy':85.0, \
                   'o2':85.0, \
                   'dia':1.0e-6, \
                   'diat':1.0e-6, \
                   'fla':1.0e-6, \
                   'flags':1.0e-6, \
                   'bg':1.0e-6, \
                   'cyan':1.0e-6, \
                   'microzoo':1.0e-6, \
                   'mesozoo':1.0e-6, \
                   'zoos':1.0e-6, \
                   'zool':1.0e-6, \
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
               'po4': redf2*redf6,\
               'sil': redf3*redf6,\
               'sio': redf3*redf6,\
               'oxy': 1.0,\
               'o2': 1.0,\
               'dia': redf1*redf6,\
               'diat': redf1*redf6,\
               'fla': redf1*redf6,\
               'flags': redf1*redf6,\
               'bg': redf1*redf6,\
               'cyan': redf1*redf6,\
               'microzoo': redf1*redf6,\
               'mesozoo': redf1*redf6,\
               'zoos': redf1*redf6,\
               'zool': redf1*redf6,\
               'det': redf1*redf6,\
               'opa': redf3*redf6,\
               'dom': redf1*redf6}

  ecosmo_factors={'no3': redf1*redf6,\
               'nh4': redf1*redf6,\
               'po4': redf2*redf6,\
               'sio': redf3*redf6,\
               'o2': 1.0,\
               'diat': 1.0,\
               'flags': 1.0,\
               'cyan': 1.0,\
               'zoos': 1.0,\
               'zool': 1.0,\
               'det': 1.0,\
               'opa': 1.0,\
               'dom': 1.0}

  tr_nd = zeros((nws.znum,2+len(ecosmo_tracers)))
  nws.create_hotstart(ntracers=2+len(ecosmo_tracers))
  e.prefetch_for_interpolation(tracers=ecosmo_tracers)
  print('  prefetched tracers:')
  print(e.prefetched_tracers)
  print(e.tv.keys())
  print(e.tv['no3'].keys())

  # create t,s fields:
  for nodeid,nodelon,nodelat,d in zip(nws.inodes,nws.lon,nws.lat,nws.depths):
    if (nodeid%10000) == 0:
      print('  interpolate i = %d'%nodeid)
      nws.hotstart_nc.sync()

    #if nodeid == 2000:
    #  break 
    depths = nws.vgrid[nodeid].filled(-1)*d
    bidx = nws.bidx[nodeid]
    t,s = oa.interpolate(depths,nodelon,nodelat,bidx=1)
    tr_nd[:,0] = t
    tr_nd[:,1] = s
    # if interpolate from ecosmoII dataset
    if False:
      tr_nd[:,2:] = e.interpolate(depths,nodelon,nodelat,bidx=1,tracers=ecosmo_tracers,factors=ecosmo_factors)
    else:
      for trnum,trname in enumerate(ecosmo_tracers):
        tr_nd[:,2+trnum] = tracer_factor[trname]*tracer_conc_const[trname]

    nws.write_hotstart_tracers_on_nodes(nodeid,tr_nd)

  nws.fill_hotstart_tracers_from_nodes()
  nws.close_hotstart()


