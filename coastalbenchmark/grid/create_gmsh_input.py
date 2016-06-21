from pylab import *
import numpy as np

def depth_by_xy(x,y,hland=-10.0,hmudflat=-3.0,hriver=5.0,hcoast=10.,hmouth=15.,hshelf=100.,wriver=1800.,wmouth=9000.,wcoast=20000.,wslope=20000.,lmouth=50000.,lestuary=100000.):
  """
  set up depths in the coastal benchmark setup
  """

  x = asarray(x)
  y = asarray(y)

  land = np.where(y<0.0,1,0)*np.where(np.abs(x)>0.5*wmouth,1,0)
  estuary = np.where(y<0.0,1,0)*np.where(np.abs(x)<0.5*wmouth,1,0)
  sea = np.where(y>0.0,1,0)

  hbase = np.abs(x)/(0.5*wmouth)*hmudflat + (hcoast-hmudflat)*(1.0+np.tanh(y/(0.5*lmouth)))
  hthalweg = hriver + (hmouth-hriver)*(y+lestuary)/lestuary
  westuary = wriver + (wmouth-wriver)*(1.0+tanh(y/(0.5*lmouth)))

  hestuary = hbase + (hthalweg-hbase)*np.exp(-(x/(0.25*westuary))**2)
  
  hbase0 = np.abs(x)/(0.5*wmouth)*hmudflat + (hcoast-hmudflat)*np.ones(y.shape)
  hestuary0 = hbase0 + (hmouth - hbase0)*np.exp(-(x/(0.25*wmouth))**2)
  
  hsea = np.maximum(hestuary0,hcoast + 0.5*(hshelf-hcoast)*(1.0+tanh((y-wcoast)/(0.25*wslope))))

  h = land*hland + estuary*hestuary + sea*hsea
  h = np.ma.masked_equal(h,hland)
  return h


xx = linspace(-50000,150000.,600.)
yy = linspace(-100000.,100000.,600.)
x2d,y2d = np.meshgrid(xx,yy)

h = depth_by_xy(x2d.flat,y2d.flat)
h2d = h.reshape(x2d.shape)
hland=-10.0;hmudflat=-3.0;hriver=5.0;hcoast=10.;hmouth=15.;hshelf=100.;wriver=1800.;wmouth=9000.;wcoast=20000.;wslope=20000.;lmouth=50000.;lestuary=100000.

rescoast=600.
resestuary=300.
ressea=3000.

# reduce resolution from coast to open sea
res = (ressea-rescoast)*np.maximum(zeros(h2d.shape),(h2d-hcoast))/(hshelf-hcoast)+rescoast

# smooth transition
trans = ((np.sqrt(x2d**2+y2d**2))/(10000.+0.5*wmouth))*(rescoast-resestuary) + resestuary
res[where(trans<rescoast)]=trans[where(trans<rescoast)]

# set high resolution in estuary
res[where(y2d<0.0)] = resestuary

pcolormesh(x2d,y2d,res,cmap=cm.Blues)
colorbar()
show()

