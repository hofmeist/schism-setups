
# coding: utf-8

# ### ICES validation

# In[ ]:

import pandas as pd
from pylab import *
import pickle
from scipy.spatial import cKDTree
import netCDF4
import sys,os
import numpy

if len(sys.argv)>1:
  setupid=sys.argv[1]
else:
  setupid='arcticice05'

#surface = df.query('depth < 6.0')
#day0 = datestr2num('2012-01-01 00:00:00')
#days = asarray([ datestr2num(str(d)) for d in surface['date']]) -day0

surface={}
nc = netCDF4.MFDataset('/work/gg0877/KST/MiMeMo/ICES/CTD/ICES_201*.nc')
ncv = nc.variables
surface['Longdeg'] = ncv['Lon'][:]
surface['Latdeg'] = ncv['Lat'][:]
ut = netCDF4.netcdftime.utime(ncv['Date'].units)
day0 = datestr2num('2012-01-01 00:00:00')
days = asarray([date2num(d)-day0 for d in ut.num2date(ncv['Date'][:])])
surface['salt'] = ncv['salt'][:,0]
surface['temp'] = ncv['temperature'][:,0]
nc.close()

def find_lateral_indices(x,y,px,py):
    '''based on lists of points x,y finx nearest neighbour for
    points with coordinates in px,py.
    returns a list of len(px)'''
    
    tree = cKDTree(list(zip(x,y)))
    dist,idxs = tree.query(list(zip(px,py)),k=1)
    return idxs

def find_1d_indices(x,px,k=2):
    '''find neares indices for px within x.
    returns dist,inds: a tuple of lists of shape=(len(px),k)'''
    if shape(x)[-1] != 1:
      xa = zeros((len(x),1))
      xa[:,0] = x
    else:
      xa=x
    if shape(px)[-1] != 1:
      pxa = zeros((len(px),1))
      pxa[:,0] = px
    else:
      pxa=px

    tree = cKDTree(xa)
    dist,inds = tree.query(pxa,k=k)
    return dist,inds

# read coordinates from netcdf
snc = netCDF4.MFDataset('%s/*/schout_*.nc'%setupid)
sncv = snc.variables
x = sncv['SCHISM_hgrid_node_x'][:]
y = sncv['SCHISM_hgrid_node_y'][:]

# read field of salinity from netcdf
salt = sncv['salt'][:,:,-1].squeeze()
temp = sncv['temp'][:,:,-1].squeeze()
model_days = sncv['time'][:]/86400.

# get grid indices
surface['idxs'] = find_lateral_indices(x,y,surface['Longdeg'],surface['Latdeg'])
dts,tidxs = find_1d_indices(model_days,days)

salt_ices = []
temp_ices = []
# interpolate, meanwhile get time positions
for idx,dt,tidx in zip(surface['idxs'],dts,tidxs):
    dtsum=sum(dt)
    if days[tidx[0]]>model_days.max():
      salt_ices.append(-9999.0)
      temp_ices.append(-9999.0)
    else:
      salt_ices.append(salt[tidx[0],idx]*(1.-dt[0]/dtsum)+salt[tidx[1],idx]*(1.-dt[1]/dtsum))
      temp_ices.append(temp[tidx[0],idx]*(1.-dt[0]/dtsum)+temp[tidx[1],idx]*(1.-dt[1]/dtsum))
    
surface['model_salt']=ma.masked_less(salt_ices,0.0).filled(numpy.nan)
surface['model_temp']=ma.masked_less(temp_ices,0.0).filled(numpy.nan)
surface['jd'] = days+day0

surfacedf = pd.DataFrame(surface)

f = open('dataframe_%s_surface.pickle'%setupid,'wb')
pickle.dump(surfacedf,f)
f.close()
