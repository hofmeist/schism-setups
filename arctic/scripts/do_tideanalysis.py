import netCDF4
import netcdftime as nctime
import sys
import pickle,os
import ttide as tt
from tqdm import tqdm
from pylab import arange,zeros,ones,interp

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

def create_result(inum,ncfile='tideanalysis.nc'):
  nnc = netCDF4.Dataset(ncfile,'w',format='NETCDF3_CLASSIC')
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
  return nnc

def process_parallel(i):
  try:
    nnc = netCDF4.Dataset('schout_2.nc')
    e = interp(nhours,hours,nnc.variables['elev'][:,i])
    nnc.close()
    tides = tt.t_tide(e,dt=dthours,out_style=None)
  except:
    tides=None
  return tides

def process_chunk_parallel(elev):
  tides=[]
  for i in range(elev.shape[1]):
    try:
      e = interp(nhours,hours,elev[:,i])
      tides.append(tt.t_tide(e,dt=dthours,out_style=None))
    except:
      tides.append(None)
  return tides

def process_point(i):
  try:
    e = interp(nhours,hours,ncv['elev'][:,i])
    tides = tt.t_tide(e,dt=dthours,out_style=None)
  except:
    tides=None
  return tides

def process_timeseries_parallel(elev):
  try:
    e = interp(nhours,hours,elev)
    tides = tt.t_tide(e,dt=dthours,out_style=None)
  except:
    tides=None
  return tides

def write_result(result,nnc):
  for i,tides in enumerate(result):
    write_point(nnc,i,tides)
  nnc.sync()

def write_point(nnc,i,tides):
    if tides is not None: 
      m2idx = list(tides['nameu']).index(b'M2  ')
      m4idx = list(tides['nameu']).index(b'M4  ')
      s2idx = list(tides['nameu']).index(b'S2  ')
      m2_amp = tides['tidecon'][m2idx][0]
      m2_pha = tides['tidecon'][m2idx][2]
      m4_amp = tides['tidecon'][m4idx][0]
      m4_pha = tides['tidecon'][m4idx][2]
      s2_amp = tides['tidecon'][s2idx][0]
      s2_pha = tides['tidecon'][s2idx][2]
    else:
      m2_amp = -99.
      s2_amp = -99.
      m4_amp = -99.
      m2_pha = -99.
      s2_pha = -99.
      m4_pha = -99.
    nnc.variables['m2_pha'][i]=m2_pha
    nnc.variables['m2_amp'][i]=m2_amp
    nnc.variables['s2_pha'][i]=s2_pha
    nnc.variables['s2_amp'][i]=s2_amp
    nnc.variables['m4_pha'][i]=m4_pha
    nnc.variables['m4_amp'][i]=m4_amp





# create netcdf
nnc = create_result(inum)

if not(do_parallel):
  for i in tqdm(range(inum),ascii=True):
    if (i%100 == 0):
      nnc.sync()
    tides = process_point(i,nnc)
    write_point(nnc,i,tides)

else:
  from joblib import Parallel, delayed
  elev = ncv['elev'][:]

  # if timeseries or chunked version
  # (hand over subarray instead of timeseries)
  if False:
    result = Parallel(n_jobs=n_jobs)(delayed(process_timeseries_parallel)(elev[:,i]) for i in tqdm(range(inum),ascii=True))

  else:
    chunksize=100
    chunked_result = Parallel(n_jobs=n_jobs)(delayed(process_chunk_parallel)(elev[:,i*chunksize:min(inum,(i+1)*chunksize)]) for i in tqdm(range(int(inum/chunksize)+1),ascii=True))
    result=[]
    for res in chunked_result:
      result.extend(res)

  # save result as pickle
  with open('result.pickle','wb') as f:
    pickle.dump(result,f)

  # write to netcdf
  write_result(result,nnc)

# close netcdf
nnc.close() 

