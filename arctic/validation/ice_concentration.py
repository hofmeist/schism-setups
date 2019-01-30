import netCDF4
import sys
import matplotlib
#matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime
import argparse
from datetime import datetime
import netcdftime

icefile = '/work/gg0877/KST/MiMeMo/osi-saf450'
nc = netCDF4.MFDataset(icefile+'/osi_saf450*.nc')
ncv = nc.variables

lon = ncv['lon'][:]
lat = ncv['lat'][:]
iceconc = ncv['ice_conc']

ut = netcdftime.utime(nc.variables['time'].units)
dates = ut.num2date(nc.variables['time'][:])

years = arange(2012,2016)
vmonth = 5

if True:
      # set map boundaries
      xl,yl = (-15.0,60.0)
      xu,yu = (100,75.0)

      proj = Basemap(projection='lcc',
                       resolution='c',area_thresh=10.0,
                        llcrnrlon=xl,
                        llcrnrlat=yl,
                        urcrnrlon=xu,
                        urcrnrlat=yu,
                        lat_0=70.0,
                        lon_0=20.0)


x,y = proj(lon,lat)
xyear,yyear = proj(-45.0,75.0)

for vmonth in range(1,13):

  f = figure(figsize=(8,10))
  sub = 100*len(years)+21

  for i,year in enumerate(years):
    startidx = where(dates == datetime(year,vmonth,1,12,0,0))[0]
    if vmonth<12:
     nextmonth=vmonth+1
    else:
     nextmonth=1
    endidx = where(dates == datetime(year,nextmonth,1,12,0,0))[0]

    subplot(sub+i*2)
 
    ice = iceconc[startidx:endidx].mean(axis=0)
    ice = ma.masked_where(ice<1.0,ice)
    pcolor(x,y,ice,cmap=cm.PuRd_r) 
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))
    #print('  %d: %d-%d'%(year,startidx,endidx))

    text(xyear,yyear,str(year),size=14)

    # now model results
    subplot(sub+i*2+1)
 
    mnc = netCDF4.MFDataset('/work/gg0877/hofmeist/arctic/arcticice04/%d-%02d/schout_*.nc'%(year,vmonth))
    mncv=mnc.variables 
    mlon = mncv['SCHISM_hgrid_node_x'][:]
    mlat = mncv['SCHISM_hgrid_node_y'][:]
    mx,my = proj(mlon,mlat)
    nv = mncv['SCHISM_hgrid_face_nodes'][:,:3]-1
    ice = mncv['ICE_tracer_2'][:].mean(axis=0)
    iceelements = ice[nv].mean(axis=1)
    mnc.close()
    ice = ma.masked_where(ice<1.0,ice)
    tripcolor(mx,my,nv,0.15*ones(ice.shape),cmap=cm.Greys,rasterized=True,vmin=0.0,vmax=1.0) 
    tripcolor(mx,my,nv,ice,mask=iceelements<0.05,cmap=cm.PuRd_r,rasterized=True) 
    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))

  savefig('ice_concentration_validation_%02d.pdf'%vmonth)
