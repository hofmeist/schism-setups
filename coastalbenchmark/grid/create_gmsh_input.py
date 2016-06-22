from pylab import *
import numpy as np
import pickle

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


dx = 600.
dy = 600.
xx = arange(-50000,150000.+dx,dx)
yy = arange(-100000.,100000.+dy,dy)
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

# write structured_size.dat
xmin=-50000.
ymin=-100000.
ynum,xnum = res.shape
s = open('structured_size.dat','w')
s.write('%0.2f %0.2f %0.2f\n'%(xmin,ymin,0.0))
s.write('%0.2f %0.2f %0.2f\n'%(dx,dy,1.0))
s.write('%d %d %d\n'%(xnum,ynum,1))
for size in res.T.flat[:]:
  s.write('%0.2f\n'%size)
s.close()

# write xyd
p = open('xyd_bathymetry.pickle','wb')
hflat = asarray(h2d.mask.flat[:])
idx = where(hflat==False)
obj = (asarray(x2d.flat[idx]),asarray(y2d.flat[idx]),asarray(h2d.flat[idx]))
pickle.dump(obj,p,protocol=-1)
p.close()


# create gmsh boundaries
f = open('grid.geo','w')
f.write("""
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthExtendFromBoundary = 0;

res = 3000.;
""")

points = {1: (-50000.,0.0),2:(-0.5*wmouth,0.0),3:(-0.5*wmouth,-lestuary),4:(0.5*wmouth,-lestuary),5:(0.5*wmouth,0.0),6:(150000.,0.0),7:(150000.,100000.),8:(-50000.,100000.)}

lines = {11: (1,2), 12: (2,3), 13: (3,4), 14: (4,5), 15: (5,6), 16: (6,7), 17: (7,8), 18: (8,1)}

for point in points:
  f.write('Point(%d) = {%0.2f,%0.2f,0.0,res};\n'%(point,points[point][0], points[point][1]))

l = lines.keys()
l.sort()
for line in l:
  f.write('Line(%d) = {%d, %d};\n'%(line,lines[line][0],lines[line][1]))

f.write("""
Line Loop(20) = {11,12,13,14,15,16,17,18};
Plane Surface(30) = {20};

Physical Line("landbdy") = {11,12,13,14,15};
Physical Line("openbdy") = {16,17,18};
Physical Surface("water") = {30};

Field[1] = Structured;
Field[1].FileName = "structured_size.dat";
Field[1].TextFormat = 1;

Background Field = 1;
""")
f.close()
