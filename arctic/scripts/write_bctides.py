import os
from pylab import *
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import *

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
0
""")

bf.write('%d nope\n'%len(a.bdy_segments))

bdy_nodes=[]
for seg in a.bdy_segments:
  # write segment into bctides.in
  bf.write('%d 0 0 4 4\n'%len(seg))
  bf.write('1.0\n1.0\n')

  bdy_nodes.extend(seg)
n = len(bdy_nodes)
bf.close()
