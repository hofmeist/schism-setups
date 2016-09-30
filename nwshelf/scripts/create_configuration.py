import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from pylab import *
from schism import *

s = schism_setup()

s.dump_tvd_prop()
s.dump_gr3('elev.ic',const=0.0,comment='intial surface elevation')
#s.dump_gr3('temp.ic',const=5.0,comment='intial temperature')
#s.dump_gr3('salt.ic',const=35.0,comment='initial salinity')
s.dump_gr3('rough.gr3',const=0.0001,comment='bottom roughness')
s.dump_gr3('diffmin.gr3',const=0.000000001,comment='diffmin')
s.dump_gr3('diffmax.gr3',const=0.1,comment='diffmax')

