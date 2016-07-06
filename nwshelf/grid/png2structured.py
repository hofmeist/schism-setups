from pylab import *
from scipy import misc
import numpy
import sys

a = numpy.flipud(misc.imread(sys.argv[1]))

size_factor = 0.9
bg_size = 7000.
 
size = bg_size-size_factor*bg_size*(1.-a[:,:,:3].mean(axis=2)/255.)
(xmin,ymin,dx,dy,xnum,ynum) = numpy.load('oxy_dxy_nxy.pickle')

x = xmin + dx*arange(xnum)
y = ymin + dy*arange(ynum)

if True:
  pcolor(x,y,size,cmap=cm.gray)
  colorbar()
  axis('equal')
  show()

# write struct
if True:
  s = open('structured.dat','w')
  s.write('%0.2f %0.2f %0.2f\n'%(xmin,ymin,0.0))
  s.write('%0.2f %0.2f %0.2f\n'%(dx,dy,1.0))
  s.write('%d %d %d\n'%(xnum,ynum,1))
  for size in size.T.flat[:]:
    s.write('%0.2f\n'%size)
  s.close()
