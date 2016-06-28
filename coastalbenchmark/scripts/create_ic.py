import sys
sys.path.append('/home/hofmeist/schism/setups/scripts')
from pylab import *
from schism import *

s = schism_setup()

s.dump_tvd_prop()
s.dump_gr3('elev.ic',const=0.0,comment='intial surface elevation')
s.dump_gr3('temp.ic',const=10.0,comment='intial temperature')
s.dump_gr3('rough.gr3',const=0.001,comment='bottom roughness')
s.dump_gr3('xlsc.gr3',const=0.5,comment='turbulent length scale')
s.dump_gr3('diffmin.gr3',const=0.000000001,comment='diffmin')
s.dump_gr3('diffmax.gr3',const=0.1,comment='diffmax')

f = open('salt.ic','w')
f.write('salt initial condition\n')
f.write('%d %d\n'%(s.nelements,s.nnodes))
for i,x,y in zip(s.inodes,s.x,s.y):
  salt = interp(y,[-1000.,-10.],[0.,30.])
  f.write('%d %0.2f %0.2f %0.5f\n'%(i,x,y,salt))
f.close()

