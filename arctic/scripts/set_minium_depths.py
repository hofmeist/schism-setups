import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from pylab import *
from schism import *

s = schism_setup('../hgrid.gr3','../hgrid.ll')

h = asarray(s.depths)
h[where(h<5.0)] = 5.0

s.depths = list(h)
s.dump_hgridll('hgrid_min5.ll')

