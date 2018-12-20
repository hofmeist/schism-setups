import matplotlib
matplotlib.use('Agg')
from pylab import *
import netCDF4
import netcdftime as nctime
import sys
from mpl_toolkits.basemap import Basemap
import pickle,os
import ttide as tt

if len(sys.argv)>2:
  n_jobs=int(sys.argv[2])
  do_parallel=True
else:
  n_jobs=1
  do_parallel=False

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
#sigma = ncv['sigma'][:]
#nsigma = len(sigma)
#bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:]/86400. # d

varname='elev'
var = ncv[varname]
#time = array([0.0])

inum = len(nc.dimensions['nSCHISM_hgrid_node'])
m2_amp = zeros((inum,))
m2_pha = zeros((inum,))
s2_amp = zeros((inum,))
s2_pha = zeros((inum,))
m4_amp = zeros((inum,))
m4_pha = zeros((inum,))

ut = nctime.utime(ncv['time'].units)
hours = ncv['time'][:]/3600.
hours = hours - hours[0]
dthours = hours[1]-hours[0]
nhours = arange(hours[0],hours[-1]+0.5,1.0)
dthours=1.0

nnc = netCDF4.Dataset('tideanalysis.nc','w',format='NETCDF3_CLASSIC')
nnc.createDimension('node',inum)

vv=nnc.createVariable('m2_pha','f8',('node',))
vv.missing_value=-99
vv=nnc.createVariable('m2_amp','f8',('node',))
vv.missing_value=-99
vv=nnc.createVariable('s2_pha','f8',('node',))
vv.missing_value=-99
vv=nnc.createVariable('s2_amp','f8',('node',))
vv.missing_value=-99
vv=nnc.createVariable('m4_pha','f8',('node',))
vv.missing_value=-99
vv=nnc.createVariable('m4_amp','f8',('node',))
vv.missing_value=-99

def process_parallel(i):
  try:
    nnc = netCDF4.Dataset('schout_2.nc')
    e = interp(nhours,hours,nnc.variables['elev'][:,i])
    nnc.close()
    tides = tt.t_tide(e,dt=dthours,out_style=None)
  except:
    tides=None
  return tides

def write_result(result):
  for i,tides in enumerate(result):
   if tides is not None: 
    m2idx = list(tides['nameu']).index(b'M2  ')
    m4idx = list(tides['nameu']).index(b'M4  ')
    s2idx = list(tides['nameu']).index(b'S2  ')
    m2_amp[i] = tides['tidecon'][m2idx][0]
    m4_pha[i] = tides['tidecon'][m2idx][2]
    m4_amp[i] = tides['tidecon'][m4idx][0]
    m2_pha[i] = tides['tidecon'][m4idx][2]
    s2_amp[i] = tides['tidecon'][s2idx][0]
    s2_pha[i] = tides['tidecon'][s2idx][2]
  else:
    m2_amp[i] = -99.
    s2_amp[i] = -99.
    m4_amp[i] = -99.
    m2_pha[i] = -99.
    s2_pha[i] = -99.
    m4_pha[i] = -99.
  nnc.variables['m2_pha'][i]=m2_pha[i]
  nnc.variables['m2_amp'][i]=m2_amp[i]
  nnc.variables['s2_pha'][i]=s2_pha[i]
  nnc.variables['s2_amp'][i]=s2_amp[i]
  nnc.variables['m4_pha'][i]=m4_pha[i]
  nnc.variables['m4_amp'][i]=m4_amp[i]

def process_point(i):
  try:
    e = interp(nhours,hours,ncv['elev'][:,i])
    tides = tt.t_tide(e,dt=dthours,out_style=None)
    m2idx = list(tides['nameu']).index(b'M2  ')
    m4idx = list(tides['nameu']).index(b'M4  ')
    s2idx = list(tides['nameu']).index(b'S2  ')
    m2_amp[i] = tides['tidecon'][m2idx][0]
    m2_pha[i] = tides['tidecon'][m2idx][2]
    m4_amp[i] = tides['tidecon'][m4idx][0]
    m4_pha[i] = tides['tidecon'][m4idx][2]
    s2_amp[i] = tides['tidecon'][s2idx][0]
    s2_pha[i] = tides['tidecon'][s2idx][2]
  except:
    m2_amp[i] = -99.
    s2_amp[i] = -99.
    m4_amp[i] = -99.
    m2_pha[i] = -99.
    s2_pha[i] = -99.
    m4_pha[i] = -99.
  nnc.variables['m2_pha'][i]=m2_pha[i]
  nnc.variables['m2_amp'][i]=m2_amp[i]
  nnc.variables['s2_pha'][i]=s2_pha[i]
  nnc.variables['s2_amp'][i]=s2_amp[i]
  nnc.variables['m4_pha'][i]=m4_pha[i]
  nnc.variables['m4_amp'][i]=m4_amp[i]
  
if not(do_parallel):
  for i in range(inum):
    if (i%100 == 0):
      print(' i = %d'%i)
      nnc.sync()
    process_point(i)
else:
  from joblib import Parallel, delayed
  result = Parallel(n_jobs=n_jobs)(delayed(process_parallel)(i) for i in range(inum))
  with open('result.pickle','wb') as f:
    pickle.dump(result,f)
  write_result(result) 
  

if False:
  figure()
  tripcolor(x,y,nv,m2_amp,cmap=cm.jet,rasterized=True)
  proj.drawcoastlines()
  proj.fillcontinents((0.9,0.9,0.8))
  cb=colorbar()
  cb.ax.set_title('M2 [m]\n',size=10.)
  savefig('m2_amp.jpg'%(varname,varname,tidx),dpi=600)
  #show()
  close()


