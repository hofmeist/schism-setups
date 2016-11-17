import os
from pylab import *
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import *
import numpy as np

def get_bdy(time,x,y,depths,theta=50.0,T = 12.0, a=2.0,wavedepth=100.):
  f = 2 * 2*pi/86146.*sin(pi/180.*theta)
  w = 2*pi/(T*3600.)
  c = sqrt(9.81*wavedepth)
  k = w/c
  return a*exp(-f*y/c)*cos(k*x - w*time)

s = schism_setup()
discharge = 2000.0 # [m3/s]
tempsurf = 20.0 # [degC]
tempbott = 10.0 # [degC]

bf = open('bctides.in','w')
bf.write("""01/01/2016 00:00:00 PST
0 0.0
0
4 nope
""")

bdy_nodes=[]
for seg in s.bdy_segments[:3]:
  # write segment into bctides.in
  bf.write('%d 4 0 4 2\n'%len(seg))
  bf.write('1.0\n30.0\n1.0\n')

  bdy_nodes.extend(seg)
n = len(bdy_nodes)

river_nodes = s.bdy_segments[3]
bf.write("""%d 0 2 2 2
%0.2f
%0.2f
1.0
0.0
1.0
"""%(len(river_nodes),-discharge,tempsurf))
bf.close()

ddict = dict(zip(s.inodes,s.depths))
xdict = dict(zip(s.inodes,s.x))
ydict = dict(zip(s.inodes,s.y))
depth = asarray([ ddict[ii] for ii in bdy_nodes ])
x = asarray([ xdict[ii] for ii in bdy_nodes ])
y = asarray([ ydict[ii] for ii in bdy_nodes ])
bdyvgrid = asarray([s.vgrid[ii].filled(-1.) for ii in bdy_nodes ])

times = arange(0.0,32.*86400.,900.).astype('float32')

if len(sys.argv)>1:
  amp = float(sys.argv[1])
else:
  amp=2.0

f = open('elev2D.th','wb')
for time in times:
  time.tofile(f)
  elevs = get_bdy(time,x,y,depth,a=amp).astype('float32')
  #print('%0.2f num elev = %d'%(time,len(elevs)))
  elevs.tofile(f)
f.close()

f = open('TEM_3D.th','wb')
for time in array([0.0,32*86400.]).astype('float32'):
  time.tofile(f)
  for i in range(len(bdy_nodes)):
    temp = interp(depth[i]*bdyvgrid[i],[-66.,-33.],[tempbott,tempsurf])
    temp.astype('float32').tofile(f)
f.close()
  

