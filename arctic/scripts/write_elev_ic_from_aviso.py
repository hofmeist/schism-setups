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
from avisodata import aviso


if __name__ == '__main__':

  try:
    ncfile = sys.argv[1]
  except:
    ncfile = '/work/gg0877/hofmeist/aviso/na_aviso_2012.nc'

  try:
    UseSetup = bool(sys.argv[2])
  except:
    UseSetup = True

  if UseSetup:
    nws = schism_setup()
    h = aviso(ncfile)
    elev=[]

    for i,inode in enumerate(nws.inodes):
      if (i%1000) == 0:
        print('  interpolate i = %d'%i)
      lon = nws.londict[inode]
      lat = nws.latdict[inode]
      elev.append(h.interpolate(lon,lat))

  
    nws.dump_gr3('elev.ic',values=elev,comment='elev.ic created from aviso 2012 average')


