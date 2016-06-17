import sys
sys.path.append('/pf/g/g260078/schism/setups/scripts')
from schism import *
from pylab import interp
import os

s = schism_setup(hgrid_file='hgrid.gr3')

def dump_gr3(self,filename,const=0.0,comment='gr3 by create_ic.py'):
  f = open(filename,'w')
  f.write('%s\n'%comment)
  f.write('%d %d\n'%(self.nelements,self.nnodes))
  for i,x,y in zip(self.inodes,self.x,self.y):
    f.write('%d %0.2f %0.2f %0.5f\n'%(i,x,y,const))
  f.close()

f = open('salt.ic','w')
f.write('salt initial condition\n')
f.write('%d %d\n'%(s.nelements,s.nnodes))
for i,x,y in zip(s.inodes,s.x,s.y):
  salt = interp(y,[49000.,51000.],[30.,10.])
  f.write('%d %0.2f %0.2f %0.5f\n'%(i,x,y,salt))
f.close()

f = open('elev.ic','w')
f.write('initial surface elevation\n')
f.write('%d %d\n'%(s.nelements,s.nnodes))
for i,x,y in zip(s.inodes,s.x,s.y):
  elev = interp(x,[0.,100000.],[1.0,-1.0])
  f.write('%d %0.2f %0.2f %0.5f\n'%(i,x,y,elev))
f.close()

f = open('tvd.prop','w')
for i in s.ielement:
  f.write('%d 1\n'%i)
f.close()

dump_gr3(s,'temp.ic',const=10.0,comment='intial temperature')

dump_gr3(s,'rough.gr3',const=0.001,comment='bottom roughness')

dump_gr3(s,'xlsc.gr3',const=0.5,comment='turbulent length scale')

dump_gr3(s,'diffmin.gr3',const=0.000000001,comment='diffmin')
dump_gr3(s,'diffmax.gr3',const=0.1,comment='diffmax')
os.system('ln -sf hgrid.gr3 hgrid.ll')

