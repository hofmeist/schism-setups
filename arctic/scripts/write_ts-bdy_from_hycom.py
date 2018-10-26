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


class hycom(object):

  def __init__(self,ncfile='hycom.nc'):
    self.saltname='ECO_no3'
    self.tempname='ECO_pho'
    self.lonname='longitude'
    self.latname='latitude'
    self.depthname='depth'
    self.timename='time'

    nc = netCDF4.Dataset(ncfile)
    sv = nc.variables
    self.ncv = sv
    xslice=slice(173,262) # 45.-67.
    yslice=slice(320,455) # -20.-13.625
    xslice=slice(None)
    yslice=slice(None)
    self.lon2 = sv[self.lonname][yslice,xslice]
    self.lat2 = sv[self.latname][yslice,xslice]
    self.d = -sv[self.depthname][:]
    self.time = sv[self.timename][:]
    self.timeunits = sv[self.timename].units
    self.s = sv[self.saltname][:,:,yslice,xslice]
    self.t = sv[self.tempname][:,:,yslice,xslice]

    if False:
      self.s_tree={}
      self.t_tree={}
      self.s_var={}
      self.t_var={}
      import numpy
      for tidx,time in enumerate(self.time):
        print('  build trees for month=%d'%(tidx+1))
        ynum,xnum = self.lon2.shape
        latst = self.lat2.reshape(1,ynum,xnum)*100.
        lonst = self.lat2.reshape(1,ynum,xnum)*100.
        self.lat3 = numpy.concatenate([latst]*len(self.d))
        self.lon3 = numpy.concatenate([lonst]*len(self.d))
        self.d3 = self.lon3.copy()
        for k,d in enumerate(self.d):
          self.d3[k,:,:] = d
        #self.d3,self.lat3,self.lon3 = meshgrid(self.d,self.lat*100.,self.lon*100.,indexing='ij')
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
    else:
      print('  build spatial tree')
      self.mask = self.t.mask[0,0].squeeze()
      self.water = where(self.mask==False)
      vlon2 = self.lon2[self.water]
      vlat2 = self.lat2[self.water]
      self.tree = cKDTree(zip(vlon2,vlat2))


  def interpolate(self,depths,nodelon,nodelat,tidx=1,bidx=1):

    if False:
      for ik,ndepth in enumerate(depths[bidx-1:]):
        # find vertical layer in climatology
        dist,inds = self.s_tree[month].query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        s[bidx-1+ik] = np.sum(w*self.s_var[month][inds],axis=0) / np.sum(w,axis=0)

        dist,inds = self.t_tree[month].query((nodelon*100.,nodelat*100.,ndepth))
        w = 1 / dist
        t[bidx-1+ik] = np.sum(w*self.t_var[month][inds],axis=0) / np.sum(w,axis=0)
    else:
      dist,inds = self.tree.query((nodelon,nodelat),k=4)
      w = 1/dist
      varprof = ma.masked_equal(zeros((len(self.d),)),-1.0)
      for k,d in enumerate(self.d):
        #varprof[k] = np.sum(w*self.ncv[self.tempname][0,k][self.water][inds],axis=0)/np.sum(w,axis=0)
        varprof[k] = np.nanmean(self.ncv[self.tempname][0,k][self.water][inds],axis=0)
        if isnan(varprof[k]):
          varprof.mask[k]=True

      # check if all values are masked
      if type(varprof.mask)==np.bool_:
        t = interp(depths,-self.d,varprof)
      else:
        t = interp(depths,-self.d[where(~varprof.mask)],varprof[where(~varprof.mask)])
      # plot for debugging
      if True:
        plot(-self.d,varprof,'r-')
        plot(depths,t,'yo')
        show()

      s = t
    return (t,s)


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
    for i,inode in enumerate(nws.bdy_nodes):
      if (i%100) == 0:
        print('  interpolate i = %d'%i)
      bdylon = nws.londict[inode]
      bdylat = nws.latdict[inode]
      depths = -nws.vgrid[inode].filled(-1)*nws.depthsdict[inode]
      t,s = h.interpolate(depths,bdylon,bdylat,tidx=0,bidx=1)
  else:
    depths=-1.0*asarray([-3000.,-2000.,-1000,-500,-200.,-100,-50,-25,-12,-6])
    t,s = h.interpolate(depths,40,75.0,tidx=0,bidx=1)

