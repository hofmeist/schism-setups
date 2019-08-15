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
from mpl_toolkits.basemap import interp as binterp

class hamtide(object):

  def __init__(self,bbox=[None,None,None,None]):
    """
    initialize from netcdf files
    """
    from scipy import interpolate
    self.T = {}
    self.T['M2'] = 12.421
    self.T['S2'] = 12.000
    self.T['O1'] = 25.819
    self.T['K1'] = 23.935
    self.T['N2'] = 12.659
    self.T['K2'] = 11.967
    self.T['P1'] = 24.066
    self.T['Q1'] = 26.868
    self.T['2N'] = 12.906

    self.kp = {} # kappa prime - equilibrium argument (Greenwich), year 2012
    self.kp['M2'] = 194.35
    self.kp['S2'] = 359.89
    self.kp['O1'] = 171.47
    self.kp['K1'] = 18.46
    self.kp['N2'] = 42.02
    self.kp['K2'] = 216.47
    self.kp['P1'] = 350.48
    self.kp['Q1'] = 19.25
    self.kp['2N'] = -9999. # unknown 2N2

    path='/work/gg0877/KST/Tides/hamtide'
    self.ampl={}
    self.phas={}
    islice=slice(bbox[0],bbox[1])
    jslice=slice(bbox[2],bbox[3])

    for tide in self.T:
      ncfile = path+'/%s.hamtide11a.nc'%tide.lower()
      nc = netCDF4.Dataset(ncfile)
      ncv = nc.variables
      tidename = tide.upper()
      
      self.lon=ncv['LON'][islice]
      self.lat=ncv['LAT'][jslice]
      self.ampl[tidename]=ncv['AMPL'][jslice,islice]
      self.phas[tidename]=ncv['PHAS'][jslice,islice]

  def findnearest(self,lon,lat):
    """
    find nearest neighbour
    """
    lon2,lat2 = np.meshgrid(self.lon,self.lat)
    iis,jjs = np.meshgrid(arange(len(self.lon)),arange(len(self.lat)))
    self.water = np.logical_not(self.ampl['M2'].mask)
    tree = cKDTree(list(zip(lon2[where(self.water)],lat2[where(self.water)])))
    
    dist,inds = tree.query(list(zip(lon,lat)),k=1)
    iiis = iis[where(self.water)][inds]
    jjjs = jjs[where(self.water)][inds]
    return iiis,jjjs

  def interpolate(self,lon,lat,tides=['M2','S2']):
    """
    interpolate the tides
    """
    ampl={}
    phas={}
    for tide in tides:
       ampl[tide] = binterp(self.ampl[tide],self.lon,self.lat,lon,lat)
       phas[tide] = binterp(self.phas[tide],self.lon,self.lat,lon,lat)

    return ampl,phas

if __name__ == '__main__':

  h = hamtide(bbox=[None,None,1000,1350])

  try:
    UseSetup = bool(sys.argv[1])
  except:
    UseSetup = False

  if UseSetup:
    a = schism_setup()



    # write bctides.in and create list of boundary nodes
    bf = open('bctides.in','w')
    bf.write("""01/01/2012 00:00:00 PST
8 20. ntip
O1
1 0.100514 6.759775e-05  1.11198 127.15503
K1
1 0.141565 7.292117e-05  1.06837 328.40845
Q1
1 0.019256 6.495457e-05  1.13118 234.12636
P1
1 0.046834 7.251056e-05  0.99506 279.25235
K2
2 0.030704 1.458423e-04  1.16389 117.45436
N2
2 0.046398 1.378797e-04  0.97671 206.12875
M2
2 0.242339 1.405189e-04  0.98160 98.26966
S2
2 0.113033 1.454441e-04  1.00123 239.89180
    """)

    tides = ['M2','S2','K1','O1','Q1','P1','N2','K2']
    bf.write('%d nbfr\n'%len(tides))
    for tide in tides:
      bf.write('%s\n'%tide)
      bf.write('1 %0.6e 1.0 %0.6f\n'%(2*pi/(h.T[tide]*3600.),h.kp[tide]))

    bf.write('%d nope\n'%len(a.bdy_segments))

    bdy_nodes=[]
    for seg in a.bdy_segments:
      lons = asarray([a.londict[ii] for ii in seg])
      lats = asarray([a.latdict[ii] for ii in seg])
      amp,pha = h.interpolate(lons,lats,tides=tides)
      iis,jjs = h.findnearest(lons,lats)
      for i in range(len(amp['M2'])):
        if amp['M2'].mask[i]:
          for tide in amp:
            amp[tide][i] = h.ampl[tide][jjs[i],iis[i]]
            pha[tide][i] = h.phas[tide][jjs[i],iis[i]]

      # write segment into bctides.in
      bf.write('%d 3 0 4 4\n'%len(seg))
      
      # write amplitude and phase
      for tide in tides:
        bf.write('%s\n'%tide)
        for i in range(len(seg)):
           bf.write('%0.3f %0.3f\n'%(amp[tide][i]/100.,pha[tide][i]))

      bdy_nodes.extend(seg)
    n = len(bdy_nodes)
    bf.close()

  else:
    
    lon,lat = asarray([8.0,8.0]),asarray([54.0,53.0])
    amp,pha = h.interpolate(asarray([8.0,8.0]),asarray([54.0,53.0]))

    iis,jjs = h.findnearest(lon,lat)

    for i in range(len(amp['M2'])):
      if amp['M2'].mask[i]:
        for tide in amp:
          amp[tide][i] = h.ampl[tide][jjs[i],iis[i]]
          pha[tide][i] = h.phas[tide][jjs[i],iis[i]]

    print(amp)
    print(pha)


