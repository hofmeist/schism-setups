from pylab import *
import pickle
import numpy as np
from schism import *

try:
  f = open('coast_proj.pickle','rb')
  m,=pickle.load(f)
  f.close()
  use_proj=True
except:
  use_proj=False

# get hgrid information
print('  read setup')
setup = schism_setup()

if use_proj:
  # get lon/lat of nodes
  print('  map coordinates')
  setup.lon,setup.lat = m(setup.x,setup.y,inverse=True)

  # calculate rotation angles for winds:
  print('  write rotation angles for winds')
  f = open('windrot_geo2proj.gr3','w')
  f.write('windrot_geo2proj.gr3\n')
  f.write('%d %d\n'%(setup.nelements,setup.nnodes))
  angles=[]
  for n,x,y,lo,la in zip(setup.inodes,setup.x,setup.y,setup.lon,setup.lat):
    u,v = m.rotate_vector(asarray([0.0]),asarray([1.0]),asarray([lo]),asarray([la]))
    angle = arcsin(float(u))*180/pi
    f.write('%d %0.6f %0.6f %0.2f\n'%(n,x,y,angle))
    angles.append(angle)
  f.close()

# maybe plot figure:
#figure()
#tripcolor(setup.x,setup.y,asarray(setup.nv)-1,angles)
#colorbar()
