from pylab import *
import numpy
from scipy.spatial import cKDTree
import pickle

f = open('xyd_bathymetry.pickle','rb')
x,y,d=pickle.load(f)
f.close()

f = open('coast_proj.pickle','rb')
m,=pickle.load(f)
f.close()

slon,slat = numpy.load('structured_lon_lat.pickle')
xmin,ymin,dx,dy,nx,ny = numpy.load('oxy_dxy_nxy.pickle')
sx,sy = m(slon,slat)

# build tree
print('  build tree')
tree = cKDTree(zip(x,y))

# find weights and distances
print('  query weights')
dist,inds = tree.query(zip(sx.flat[:],sy.flat[:]), k=100)
weights = 1.0 / dist**2

# do interpolation
print('  interpolate')
depths = np.mean(d[inds],axis=1)
depths = depths.reshape(slon.shape)

# convert to resolution:
depths[where(depths<5.0)] = 5.0
dt = 120.
res = sqrt(depths*9.81) * dt * 1.5 # scale resolution to CFL=1.5
res[where(res<5000.)] = 5000.

# plot png in grayscale
f = figure()
f.set_size_inches(nx/10.,ny/10.)
ax=axes([0.0,0.0,1.0,1.0])
ax.set_axis_off()
pcolor(res,cmap=cm.Greys)
savefig('resolution_grey.png',dpi=10.)
show()

# dump structured field
s = open('structured_size.dat','w')
s.write('%0.2f %0.2f %0.2f\n'%(xmin,ymin,0.0))
s.write('%0.2f %0.2f %0.2f\n'%(dx,dy,1.0))
s.write('%d %d %d\n'%(nx,ny,1))
for length in res.T.flat[:]:
  s.write('%0.2f\n'%length)
s.close()



