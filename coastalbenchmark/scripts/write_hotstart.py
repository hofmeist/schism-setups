import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
from pylab import *
import numpy as np

cbs = schism_setup()

# write t,s on nodes
s = {}
t = {}

for i,x,y,d in zip(cbs.inodes,cbs.x,cbs.y,cbs.depths):
  s[i] = interp(y,[-1000.,-10.],[0.,30.])*ones((cbs.znum))
  depths = cbs.vgrid[i].filled(-1)*d
  t[i] = interp(depths,[-66.6,-33.3],[10,20])

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


