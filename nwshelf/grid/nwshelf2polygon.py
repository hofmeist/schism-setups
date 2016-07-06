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
xl=-20.0
xu=35.5
yu=66.0
yl=42.0

try:
  pf = open('coast_proj.pickle','rb')
  m, = pickle.load(pf)
  pf.close()
  write_pickle=False
except:
  write_pickle=True
  m = Basemap(projection='lcc',
                       resolution='h',area_thresh=10.0,
                       llcrnrlon=xl,
                       llcrnrlat=yl,
                       urcrnrlon=xu,
                       urcrnrlat=yu,
                       lat_0=57.0,
                       lon_0=8.0)
  pf = open('coast_proj.pickle','wb')
  pickle.dump((m,),pf)
  pf.close()

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


# add Helgoland islands
hcoords = [(7.891,54.169),(7.899,54.175),(7.892,54.184),(7.884,54.189),(7.869,54.189)]
hcoords = [ m(xx,yy) for xx,yy in hcoords ]
land.append(hcoords)
sland.append(sg.Polygon(hcoords))
hcoords1 = hcoords

hcoords = [(7.909,54.180),(7.919,54.181),(7.920,54.190),(7.901,54.188)]
hcoords = [ m(xx,yy) for xx,yy in hcoords ]
land.append(hcoords)
sland.append(sg.Polygon(hcoords))


newland=[]
bdyp = []

uselines=False
usesplines=True
use_insurface=True

# define surrounding domain polygon
surr_poly = [(-3.512445497362097,48.2161557909471)]
bdy_points = [(-6.136914238450116,45.87745153013138),(-11.68646285627057,46.81219480720721),(-14.66281444147484,48.35879400983765),( -16.78629020287273,51.14994748269418),(-17.32685010037414,52.61891366715251),(-13.91379234803189,55.17526330450156),(-12.24315587645659,57.02598006650172),(-11.94626468878718,58.54635528325174),(-14.85861503604304,62.67096089023385),(-1.985536301921597,64.37556728426408)]
surr_poly.extend(bdy_points)
surr_poly.extend([(8.373735852262881,62.24248813549063),(21.,66.),(xu,yu),(xu,yl)])

nb = [m(xx,yy) for xx,yy in [(-0.7,62.),(-4.2,61.1)] ]
domain = sg.Polygon([ m(xx,yy) for xx,yy in surr_poly])
#domain = sg.Polygon([(mxl,myl),(mxl,myu),(mxu,myu),(mxu,myl)])

eissel_poly = [(5.39,53.1),(4.953,52.898),(4.84,52.07),(6.77,52.6)]
eissel = sg.Polygon([ m(xx,yy) for xx,yy in eissel_poly])

problems=[]
diffproblems=[]
# Shetland
problems.append(sg.Polygon([(1798050,1605860),(1798200,1604500),(1800100,1605540),(1799640,1606520)]))

# Scotland
problems.append(sg.Polygon([(1542200.,1147880),(1554980,1148680),(1553110,1161190),(1539810,1162520)]))

# Swine channel
diffproblems.append(sg.Polygon([(2732320,872762),(2732820,871486),(2733060,871394),(2732540,872762)]))

# widely open Swine channel
diffproblems.append(sg.Polygon([(2732880,871471),(2733790,867425),(2736680,867556)]))

# helgoland point (to increase resolution)
xhelgoland,yhelgoland = m(7.9,54.185)

water = domain
# take out the first 3 land polygons
landnum=1
for p in sland[:landnum]:
  if domain.intersects(p):
    water = water.difference(p)
    if not(water.geom_type == 'Polygon'):
      water = water.geoms[0]

# take out lake Eissel
water = water.difference(eissel)
#water = water.difference(p2)
#water = water.difference(problem)

# split the common polygon into land boundaries
landbdys=[]
for p in sland[:landnum]:
  if water.intersects(p):
    line = water.intersection(p)
    points=[]
    print p.geom_type
    for g in line.geoms:
      if g.geom_type == 'LineString':
        points.append((g.xy[0][0],g.xy[1][0]))
      else:
        points.append((g.boundary.xy[0][0],g.boundary.xy[1][0]))
    landbdys.append(points[::-1][1:])

splines=landbdys
for l,p in zip(land[landnum:],sland[landnum:]):
  if water.contains(p):
    for problem in problems:
      if problem.intersects(p):
        p = p.union(problem)
        xx,yy = p.boundary.xy
        l = zip(xx,yy)
    for diffproblem in diffproblems:
      if diffproblem.intersects(p):
        p = p.difference(diffproblem)
        xx,yy = p.boundary.xy
        l = zip(xx,yy)
    splines.append(l)

if True:
  f = open('problem_areas.txt','w')
  f.write('# problems, to be joined with island splines\n')
  for problem in problems:
    xx,yy = problem.boundary.xy
    f.write('%s\n'%str(m(xx,yy,inverse=True)))
  f.write('# problems, to be removed (difference) from island splines\n')
  for diffproblem in diffproblems:
    xx,yy = diffproblem.boundary.xy
    f.write('%s\n'%str(m(xx,yy,inverse=True)))
  f.write('# lake eissel\n')
  f.write('%s\n'%str(eissel_poly))
  f.close()

if True:
  xw,yw = water.boundary.xy
  ratio = (m.ymax-m.ymin)/(m.xmax-m.xmin)
  dpi=200
  width=4.0
  #lonw,latw = m(xw,yw,inverse=True)
  #newland.append(zip(xw,yw))
  f = figure(figsize=(width,width*ratio),dpi=dpi)
  f.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0)
  m.drawcoastlines()
  m.plot(xw,yw)
  savefig('map.png',dpi=dpi)
  f = open('oxy_dxy_nxy.pickle','wb')
  dx = (m.xmax-m.xmin)/(width*dpi)
  dy = (m.ymax-m.ymin)/(width*ratio*dpi)
  pickle.dump((m.xmin,m.ymin,dx,dy,int(width*dpi),int(width*ratio*dpi)),f)
  f.close()
  show()

if True:
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
  def getbyid(self,id):
    found = False
    for s in self:
      if s.id == id:
        found = True
        break
    if found:
      return s
    else:
      return None

insurface=[]
points = Points()

# add Helgoland
pid = points.add(xhelgoland,yhelgoland,'200.0')
insurface.append(pid)

# hold lists of land, island, and open boundary
landbdy=[]
islandbdy=[]
openbdy=[]

# make lists of point indizes for lines and splines
items=PointsItems()
surface=[]
boundary=[]
s=None
landnum=1
#only one continental land polygon
for i,spline in enumerate(splines):
  s=items.add('spline',last=s)
  for p in spline:
    s.append(points.add(p[0],p[1],'cres'))

  if i==0:
     l = items.add('spline')
     l.append(s[-1])
     # add point of open boundary
     lo,la = zip(*bdy_points)
     xb,yb = m(lo[::-1],la[::-1])
     for xbb,ybb in zip(xb,yb):
       l.append(points.add(xbb,ybb,'bres'))
     # e.g.: l.append(points.add(nb[0][0],nb[0][1],'bres'))
     l.append(s[0])
     l.closed=False
     boundary.append(l.id)
     openbdy.append(l.id)

  if i>=landnum:
    # assume island
    s.closed=True
    surface.append(s)
    islandbdy.append(s.id)
  else:
    boundary.append(s.id)
    landbdy.append(s.id)

s=items.add('lineloop')
s.extend(boundary)
surface.append(s)

#dump data into .poly file:
f=open('coast.geo','w')
f.write("""
Mesh.CharacteristicLengthFromPoints = 1;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
""")
f.write('bres = %0.2f;\n'%7000.)
f.write('cres = %0.2f;\n'%7000.)

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
Field[1].F = "7000.";

Field[2] = Restrict;
Field[2].IField = 1;
Field[2].EdgesList = {%s};

Background Field = 1;
"""%(coastlist))

f.close()

if write_pickle:
  pf = open('coast_proj.pickle','wb')
  pickle.dump((m,),pf,protocol=-1)
  pf.close()
