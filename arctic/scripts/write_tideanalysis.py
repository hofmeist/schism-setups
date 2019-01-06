import netCDF4
import sys
import pickle,os
from pylab import arange,zeros,ones,interp

f = open('result.pickle','rb')
result = pickle.load(f)
f.close()

inum = len(result)
m2_amp = zeros((inum,))
m2_pha = zeros((inum,))
s2_amp = zeros((inum,))
s2_pha = zeros((inum,))
m4_amp = zeros((inum,))
m4_pha = zeros((inum,))

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

for i,tides in enumerate(result):
  if tides is not None: 
    m2idx = list(tides['nameu']).index(b'M2  ')
    m4idx = list(tides['nameu']).index(b'M4  ')
    s2idx = list(tides['nameu']).index(b'S2  ')
    m2_amp[i] = tides['tidecon'][m2idx][0]
    m2_pha[i] = tides['tidecon'][m2idx][2]
    m4_amp[i] = tides['tidecon'][m4idx][0]
    m4_pha[i] = tides['tidecon'][m4idx][2]
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

nnc.close() 

