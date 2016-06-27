from pylab import *
import sys
sys.path.append('/home/hofmeist/schism/setups/scripts')
from schism import *
import numpy as np

def get_bdy(time,x,y,depths,theta=50.0,T = 12.0, a=2.0):
  f = 2 * 2*pi/86146.*sin(pi/180.*theta)
  w = 2*pi/(T*3600.)
  c = sqrt(9.81*depths)
  k = w/c
  return a*exp(-f*y/c)*cos(k*x - w*time)

s = schism_setup()
discharge = 10.0 # [m3/s]

bf = open('bctides.in','w')
bf.write("""01/01/2016 00:00:00 PST
0 0.0
0
4 nope
""")

bdy_nodes=[]
for seg in s.bdy_segments[:3]:
  # write segment into bctides.in
  bf.write('%d 1 0 2 2\n'%len(seg))
  bf.write('10.0\n1.0\n30.0\n1.0\n')

  bdy_nodes.extend(seg)
n = len(bdy_nodes)

river_nodes = s.bdy_segments[3]
bf.write("""%d 0 2 2 2
%0.2f
10.0
1.0
0.0
1.0
"""%(len(river_nodes),-discharge))
bf.close()

n = s.num_bdy_nodes
ddict = dict(zip(s.inodes,s.depths))
xdict = dict(zip(s.inodes,s.x))
ydict = dict(zip(s.inodes,s.y))
depth = asarray([ ddict[ii] for ii in s.bdy_nodes ])
x = asarray([ xdict[ii] for ii in s.bdy_nodes ])
y = asarray([ ydict[ii] for ii in s.bdy_nodes ])

times = arange(0.0,30.*86400.,900.).astype('float32')

f = open('elev2D.th','wb')
for time in times:
  time.tofile(f)
  elevs = get_bdy(time,x,y,depth).astype('float32')
  elevs.tofile(f)
f.close()

