from pylab import *
import pickle
from scipy.spatial import cKDTree
import numpy as np
from schism import *

f = open('xyd_bathymetry.pickle','rb')
x,y,d=pickle.load(f)
f.close()

try:
  f = open('coast_proj.pickle','rb')
  m,=pickle.load(f)
  f.close()
  use_proj=True
except:
  use_proj=False

# build tree
print('  build tree')
tree = cKDTree(zip(x,y))

# get hgrid information
print('  read setup')
setup = schism_setup()

# find weights and distances
print('  query weights')
dist,inds = tree.query(zip(setup.x,setup.y), k=4)
weights = 1.0 / dist**2

# do interpolation
print('  interpolate')
setup.depths = np.sum( weights*d[inds],axis=1) / np.sum(weights,axis=1)

# dump to hgrid_new.gr3
if not(hasattr(setup,'lon')):
  setup.lon = setup.x
if not(hasattr(setup,'lat')):
  setup.lat = setup.y

setup.dump_hgridll(filename='hgrid_new.gr3')

if use_proj:
  # get lon/lat of nodes
  print('  map coordinates and write hgrid_new.ll')
  setup.lon,setup.lat = m(setup.x,setup.y,inverse=True)

  # dump hgrid.ll
  setup.dump_hgridll('hgrid_new.ll')


