from pylab import *
import pickle
from scipy.spatial import cKDTree
import numpy as np
from schism import *

f = open('xyd_bathymetry.pickle','rb')
x,y,d=pickle.load(f)
f.close()

f = open('coast_proj.pickle','rb')
m,=pickle.load(f)
f.close()

# get hgrid information
print('  read setup')
setup = schism_setup()
xmin = min(setup.x)
xmax = max(setup.x)
ymin = min(setup.y)
ymax = max(setup.y)

# make new grid
dx=2000.
dy=2000.
xn = arange(xmin-dx,xmax+2*dx,dx)
yn = arange(ymin-dy,ymax+2*dy,dy)
XN,YN = meshgrid(xn,yn)

# build tree
print('  build tree')
tree = cKDTree(zip(x,y))

# find weights and distances
print('  query weights')
dist,inds = tree.query(zip(XN.flat[:],YN.flat[:]), k=100)
weights = 1.0 / dist**2

# do interpolation
print('  interpolate')
depths = np.min(d[inds],axis=1)
#depths = np.sum( weights*d[inds],axis=1) / np.sum(weights,axis=1)

# create size field
maxlength=4000.
minlength=500.
maxdepth=50.
fac = minlength/maxlength
size = minlength * ones(depths.shape)
size[where(depths>=maxdepth)] = maxlength
idx=where(depths<maxdepth)
size[idx] = maxlength * np.maximum((depths[idx]/maxdepth),fac*ones(depths[idx].shape))

size = size.reshape((len(yn),len(xn)))
sizen = size.copy()

ynum,xnum = size.shape
st=2
for yy in range(ynum):
  for xx in range(xnum):
    minv = size[max(0,yy-st):min(ynum,yy+st),max(0,xx-st):min(xnum,xx+st)].min()
    meanv = size[max(0,yy-st):min(ynum,yy+st),max(0,xx-st):min(xnum,xx+st)].mean()
    sizen[yy,xx] = 0.5*(minv+meanv)

pcolor(sizen); colorbar(); show()

# dump structured field
s = open('structured_size.dat','w')
s.write('%0.2f %0.2f %0.2f\n'%(xmin,ymin,0.0))
s.write('%0.2f %0.2f %0.2f\n'%(dx,dy,1.0))
s.write('%d %d %d\n'%(len(xn),len(yn),1))
for length in sizen.T.flat[:]:
  s.write('%0.2f\n'%length)
s.close()


