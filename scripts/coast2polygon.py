from pylab import *
from mpl_toolkits.basemap import Basemap
from shapely import geometry as sg
import pickle
    
def check_boundary(x,y,bdys, threshold=100.):
  xl,yl,xu,yu = bdys
  if (abs(x - xl)<threshold or abs(x - xu)<threshold or abs(y - yl)<threshold or abs(y - xu)<threshold):
    return True
  else:
    return False

# set surrounding points
xl=-0.5
xu=9.5
yu=55.9
yl=49.0

try:
  pf = open('coast_proj.pickle','rb')
  m, = pickle.load(pf)
  pf.close()
  write_pickle=False
except:
  write_pickle=True
  m = Basemap(projection='lcc',
                       resolution='h',area_thresh=0.5**2,
                       llcrnrlon=xl,
                       llcrnrlat=yl,
                       urcrnrlon=xu,
                       urcrnrlat=yu,
                       lat_0=53.0,
                       lon_0=8.0)

mxu,myu=m(xu,yu)
mxl,myl=m(xl,yl)

# get coast polygon
polys = m.coastpolygons
land=[]
sland=[]
for (xp,yp),ctype in zip(polys,m.coastpolygontypes):
  if ctype<2:
    land.append(zip(xp,yp))
    sland.append(sg.Polygon(zip(xp,yp)))

newland=[]
bdyp = []

uselines=False
usesplines=True
use_insurface=False

# define surrounding domain polygon
domain = sg.Polygon([(mxl,myl),(mxl,myu),(mxu,myu),(mxu,myl)])

water = domain
# take out the first 3 land polygons
landnum=3
for p in sland[:landnum]:
  water = water.difference(p)
  if not(water.geom_type == 'Polygon'):
    water = water.geoms[0]

# split the common polygon into land boundaries
landbdys=[]
for p in sland[:landnum]:
  line = water.intersection(p)
  points=[]
  for g in line.geoms:
    points.append((g.coords.xy[0][0],g.coords.xy[1][0]))
  landbdys.append(points[::-1])

splines=landbdys
splines.extend(land[landnum:])

if False:
  xw,yw = water.boundary.xy
  newland.append(zip(xw,yw))
  figure()
  plot(xw,yw)
  show()

figure()
for i,p in enumerate(splines):
  x,y=zip(*p);x=list(x);y=list(y)
  plot(x,y,'-')
  plot(x[0],y[0],'ko'); text(x[0],y[0],str(i),size=10)
#plot(x[90:100],y[90:100],'o',color='k',ms=6.0)
show()

class Points():
  i=1
  num=0
  xyres={}
  def __initialize__(self):
    self.i=1
    self.num=0
    self.xyres={}

  def add(self,x,y,res=1000.):
    if not(type(res)=='str'):
      resstr=str(res)
    else:
      resstr=res
    self.xyres[self.i]=(x,y,resstr)
    self.i+=1
    self.num+=1
    return self.i-1

  def dump(self,f):
    for id in self.xyres:
      x,y,res = self.xyres[id]
      f.write('Point(%d) = {%0.2f, %0.2f, %0.2f, %s};\n'%(id,x,y,0.0,res))

  def modify(self,id,res=None,x=None,y=None):
    xo,yo,reso = self.xyres[id]
    if not(res==None):
      reso=res
    self.xyres[id]=(xo,yo,reso)

class PointsItem(list):
  type=None
  id=-1
  closed=False
  last=None
  def __init__(self,id,type,closed=False,last=None):
    self.container=[]
    self.id=id
    self.closed=closed
    self.last=last
    if type=='spline':
      self.type='spline'
    elif type=='line':
      self.type='line'
    elif type=='lineloop':
      self.type='lineloop'
      self.closed=True

  def dump(self,f):
    if self.type=='spline':
      f.write('BSpline(%d)={'%self.id)
      points = self
      if self.closed:
        points.append(self[0])
      for item in points[:-1]:
        f.write('%d,'%item)
      f.write('%d };\n'%points[-1])
      f.write('Line Loop(%d)={%d};\n'%(self.id,self.id))
    elif self.type=='line':
      f.write('Line(%d) = '%self.id)
      f.write('{ %d, %d };\n'%(self[0],self[1]))
    elif self.type=='lineloop':
      f.write('Line Loop(%d) = {'%self.id)
      for item in self[:-1]:
        f.write('%d, '%item)
      f.write('%d };\n'%self[-1])

class PointsItems(list):
  num=0
  def __init__(self):
    self.num=0
    self.container=[]
  def add(self,itemtype,closed=False,last=None):
    self.num+=1
    s = PointsItem(id=self.num,type=itemtype,closed=closed,last=last)
    self.append(s)
    return s

points = Points()

# hold lists of land, island, and open boundary
landbdy=[]
islandbdy=[]
openbdy=[]

# make lists of point indizes for lines and splines
items=PointsItems()
surface=[]
boundary=[]
s=None
for i,spline in enumerate(splines):
  s=items.add('spline',last=s)
  for p in spline:
    s.append(points.add(p[0],p[1],'cres'))

  if i>0 and i<landnum:
    l = items.add('line')
    l.append(s.last[-1]) # last element of last spline
    l.append(s[0]) # first element of current spline
    boundary.append(l.id)
    openbdy.append(l.id)
    if i == landnum-1:
      l = items.add('line')
      l.append(s[-1]) # last element of current land spline
      l.append(items[0][0]) # first element of first land spline

  if i>=landnum:
    # assume island
    s.closed=True
    surface.append(s)
    islandbdy.append(s.id)
  else:
    boundary.append(s.id)
    landbdy.append(s.id)

  if i==landnum-1:
    boundary.append(l.id)
    openbdy.append(l.id)

s=items.add('lineloop')
s.extend(boundary)
surface.append(s)


#dump data into .poly file:
f=open('coast.geo','w')
f.write('bres = %0.2f;\n'%5000.)
f.write('cres = %0.2f;\n'%5000.)
insurface=[]

# set resolution at boundaries
for itemid in openbdy:
  for item in items:
    if item.id == itemid:
      break
  for pointid in item:
    points.modify(pointid,res='bres')

points.dump(f)

for item in items:
  item.dump(f)

surfaceid = items.num+1
f.write('Plane Surface(%d) = {'%surfaceid)
for item in surface[:-1]:
   f.write('%d, '%(item.id))
f.write('%d };\n'%surface[-1].id)
f.write('Physical Surface("water") = {%d};\n'%surfaceid)

if use_insurface:
  for ip in insurface:
    f.write('Point {%d} In Surface {%d};\n'%(ip,surfaceid))

# write physical groups
f.write('Physical Line("islandbdy") = {')
for item in islandbdy[:-1]:
  f.write('%d, '%item)
f.write('%d };\n'%islandbdy[-1])

f.write('Physical Line("landbdy") = {')
for item in landbdy[:-1]:
  f.write('%d, '%item)
f.write('%d };\n'%landbdy[-1])

f.write('Physical Line("openbdy") = {')
for item in openbdy[:-1]:
  f.write('%d, '%item)
f.write('%d };\n'%openbdy[-1])

# write land bdy list for zooming
coast=landbdy
coast.extend(islandbdy)
coastlist = str(coast)[1:-1]

f.write("""
Field[1] = MathEval;
Field[1].F = "2000.";

Field[2] = Restrict;
Field[2].IField = 1;
Field[2].EdgesList = {%s};

Background Field = 2;
"""%(coastlist))

f.close()

if write_pickle:
  pf = open('coast_proj.pickle','wb')
  pickle.dump((m,),pf,protocol=-1)
  pf.close()
