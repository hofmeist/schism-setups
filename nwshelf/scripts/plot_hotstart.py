from pylab import *
import os
import sys
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
import netCDF4
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-file', help='hotstart file')
parser.add_argument('-tracer', help='tracer index')
parser.add_argument('-level', help='level index [nVert]')
parser.add_argument('-vrange', help='values range [-vrange vmin,vmax]')
args = parser.parse_args()
if args.tracer is not None:
  tracer=int(args.tracer)
else:
  tracer = 0
if args.level is not None:
  level=int(args.level)
else:
  tidx = -1
if args.file is not None:
  ncfile=args.file
else:
  ncfile = 'hotstart.nc'
try:
  s1,s2 = args.vrange.split(',')
  vmin,vmax = float(s1),float(s2)
  uselim=True
except:
  uselim=False



import cPickle as pickle
if not(os.path.isfile('setup.pickle')):
  nws = schism_setup()
  fh = open('setup.pickle','wb')
  pickle.dump(nws,fh,protocol=-1)
  fh.close()
else:
  nws = pickle.load(open('setup.pickle','rb'))


nv = asarray(nws.nv)-1

nc  = netCDF4.Dataset(ncfile)
ncv = nc.variables
vs = ncv['tr_nd'][:,level,tracer]

tripcolor(nws.x,nws.y,nv,vs,cmap=cm.jet)
if uselim:
  clim(vmin,vmax)
colorbar()
show()

