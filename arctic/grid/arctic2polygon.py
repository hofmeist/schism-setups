from pylab import *
from mpl_toolkits.basemap import Basemap
from shapely import geometry as sg
import cPickle as pickle
    
def check_boundary(x,y,bdys, threshold=100.):
  xl,yl,xu,yu = bdys
  if (abs(x - xl)<threshold or abs(x - xu)<threshold or abs(y - yl)<threshold or abs(y - xu)<threshold):
    return True
  else:
    return False

# set surrounding points
xl=-50.0
xu=80.0
yu=89.0
yl=50.0

try:
  pf = open('coast_proj.pickle','rb')
  m, = pickle.load(pf)
  pf.close()
  write_pickle=False
except:
  write_pickle=True
  if True:
    m = Basemap(projection='npstere',boundinglat=55.,lon_0=0.0,resolution='i')
  else:
    m = Basemap(projection='lcc',
                       resolution='c',area_thresh=10.0,
                        llcrnrlon=xl,
                        llcrnrlat=yl,
                        urcrnrlon=xu,
                        urcrnrlat=yu,
                        lat_0=70.0,
                        lon_0=10.0)

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


ipynewland=[]
bdyp = []

uselines=False
usesplines=True
use_insurface=True

# define surrounding domain polygon
#surr_poly = [(xl,yl),(xl,yu),(xu,yu),(xu,yl)]
#surr_poly = [(-40.,70.),(-130.,60.),(120.,50.),(50.,55.),(-10.,70.)]
#surr_poly = [(-40.,70.),(-40.,85.),(88.,85.),(88,55.),(50.,55.),(-5.,68.)]

surr_poly = [(-23.5426, 71.3629),(-42.95,73.88),(27.49,83.54),(44.48303011437251, 80.60464417507895),(47.347944570886405, 80.00892777559511),(53.28073665931397, 79.68848057050573),(67.88,76.43),(57.80,74.919),(53.539,71.758),(63.,69.),(88,55.),(50.,55.),(-5.,68.)]

bdy_points = [[(-40.,85.),(88.,85.)],[(-5.,68.)]]

domain = sg.Polygon([ m(xx,yy) for xx,yy in surr_poly])
#domain = sg.Polygon([(mxl,myl),(mxl,myu),(mxu,myu),(mxu,myl)])

if False:
  f = figure()
  m.drawcoastlines()
  domain_points = [ m(xx,yy) for xx,yy in surr_poly]
  figure()
  for i,p in enumerate(land[:30]):
    x,y=zip(*p);x=list(x);y=list(y)
    plot(x,y,'-')
    plot(x[0],y[0],'ko'); text(x[0],y[0],str(i),size=10)
  #for x,y in domain_points:
  #  plot(x,y,'ro')
  show()

problems=[]
nz_join = sg.Polygon([m(xx,yy) for yy,xx in [(73.20,54.57),(74.28,56.18),(74.06,57.08),(73.06,55.46)]])
diffproblems=[]

# join Novaya Zemlya
north= sg.Point(m(60.,75.))
south=sg.Point(m(54,72))
for i,p in enumerate(sland[:80]):
  if p.contains(north):
    print('found Northern Island %d'%i)
    northidx=i
  if p.contains(south):
    print('found Southern Island %d'%i)
    southidx=i
sland[northidx]=sland[northidx].union(nz_join)
sland[northidx]=sland[northidx].union(sland[southidx])
sland.pop(southidx)
land[northidx] = zip(*sland[northidx].boundary.xy)
land.pop(southidx)

water = domain
# take out the first land polygons
landnum=80
for i,p in enumerate(sland[:landnum]):
  if domain.intersects(p):
    if domain.contains(p):
      print i,'skipped'
      continue
    water = water.difference(p)
    if not(water.geom_type == 'Polygon'):
      areas = asarray([g.area for g in water.geoms])
      idx = areas.argmax()
      water = water.geoms[idx]

# split the common polygon into land boundaries
landbdys=[]
open_boundary = water.boundary
for i,p in enumerate(sland[:landnum]):
  if water.intersects(p) and not(water.contains(p)):
    #line = water.intersection(p.buffer(1.e-5))
    line = water.intersection(p)#.buffer(1.e-5))
    points=[]
    print i,p.geom_type
    open_boundary = open_boundary.difference(line)
    print(line.geom_type)
    if line.geom_type == 'Polygon':
     #x,y = line.boundary.xy
     xvec,yvec = line.boundary.xy
     for xx,yy in zip(*line.boundary.xy):
       points.append((xx,yy))
     #points.append((g.boundary.xy[0][0],g.boundary.xy[1][0])) 
    #if False:
    #  print 'we got a polygon'
    else: 
     for g in line.geoms:
      if g.geom_type == 'LineString' or g.geom_type == 'Point':
        points.append((g.xy[0][0],g.xy[1][0]))
      elif g.geom_type == 'Polygon':
        for xx,yy in zip(*g.boundary.xy):
          points.append((xx,yy))
      else:
        print(g.geom_type)
        points.append((g.boundary.xy[0][0],g.boundary.xy[1][0]))
    # add last point:
    if g.geom_type == 'LineString':
      points.append((g.xy[0][1],g.xy[1][1]))
    #landbdys.append(points[::-1][:-1])
    landbdys.append(points)

splines=list(landbdys)
for l,p in zip(land[0:],sland[0:]):
  if water.contains(p):
  #if False:
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
  if True:
    for gg in open_boundary.geoms:
      xw,yw = gg.xy
      m.plot(xw,yw,color='orange')
  savefig('map.png',dpi=dpi)
  f = open('oxy_dxy_nxy.pickle','wb')
  dx = (m.xmax-m.xmin)/(width*dpi)
  dy = (m.ymax-m.ymin)/(width*ratio*dpi)
  pickle.dump((m.xmin,m.ymin,dx,dy,int(width*dpi),int(width*ratio*dpi)),f)
  f.close()
  #show()


class Points():
  i=1
  num=0
  xyres={}
  xy={}
  id_by_xy={}
  def __initialize__(self):
    self.i=1
    self.num=0
    self.xyres={}
    self.xy={}
    self.id_by_xy={}

  def add(self,x,y,res=1000.):
    pid = self.get_id(x,y)
    if pid != -1:
      return pid
    else:
      if not(type(res)=='str'):
        resstr=str(res)
      else:
        resstr=res
      self.xyres[self.i]=(x,y,resstr)
      self.xy[self.i]=(x,y)
      self.id_by_xy[(x,y)]=self.i
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

  def get_id(self,x,y):
    try:
      return self.id_by_xy[(x,y)]
    except:
      return -1
    

class PointsItem(list):
  type=None
  id=-1
  closed=False
  last=None
  reversed=False
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
    elif type=='linelist':
      self.type='linelist'
      self.closed=False

  def get_start_and_end_points(self,items):
    starts = {}
    ends = {}
    for itemid in self:
      subitem = items.getbyid(itemid)
      if subitem.type == 'linelist':
        starts[itemid] = items.getbyid(subitem[0])[0]
        ends[itemid] = items.getbyid(subitem[-1])[1]
      else:
        starts[itemid] = subitem[0]
        ends[itemid] = subitem[-1]
    return starts,ends

  def check_and_fix_sequence(self,items):
    oldl=list(self)
    starts,ends = self.get_start_and_end_points(items)
    print starts
    print ends

    # fix loops at the ends of polygons:
    for itemid in self:
      subitem = items.getbyid(itemid)
      if subitem.type == 'linelist':
        lines = [items.getbyid(litem) for litem in subitem]
        substarts,subends = zip(*lines)
        for ii,endpoint in enumerate(subends):
          if endpoint in starts.values():
            print('  found early end of list %d, take out left over points'%itemid)
            for toberemoved in subitem[ii+1:]:
              items.pop(items.index(items.getbyid(toberemoved)))
            subitem[:] = subitem[:ii+1]
    starts,ends = self.get_start_and_end_points(items)
    print starts
    print ends

    success = True
    newl = list([oldl.pop(0)])
    matchidx = ends[newl[-1]]
    while len(oldl)>0:
      try:
        nextid = starts.keys()[starts.values().index(matchidx)]
        nextone = oldl.pop(oldl.index(nextid))
        newl.append(nextone)
        matchidx = ends[nextone]
      except:
        try:
          nextid = ends.keys()[ends.values().index(matchidx)]
          # now reverse orientation
          nextone = oldl.pop(oldl.index(nextid))
          newl.append(-nextone)
          matchidx = starts[nextone]
        except:
          print 'cannot find match, cancel reordering',matchidx
          success=False
          break
    if success: self[:] = newl
      

  def dump(self,f,items):
    if self.type=='spline':
      f.write('BSpline(%d)={'%self.id)
      points = self
      if self.closed:
        points.append(self[0])
      for item in points[:-1]:
        f.write('%d,'%item)
      f.write('%d };\n'%points[-1])
      #f.write('Line Loop(%d)={%d};\n'%(self.id,self.id))
    elif self.type=='line':
      f.write('Line(%d) = '%self.id)
      f.write('{ %d, %d };\n'%(self[0],self[1]))
    elif self.type=='linelist':
      f.write('// this list of lines is not closed\n')
      f.write('//Line Loop(%d) = {'%self.id)
      for item in self[:-1]:
        f.write('%d, '%item)
      f.write('%d };\n'%self[-1])
    elif self.type=='lineloop':
      f.write('Line Loop(%d) = {'%self.id)
      for item in self[:-1]:
        if items.getbyid(item).type=='linelist':
          for ii in items.getbyid(item):
            f.write('%d, '%ii)
        else:
          f.write('%d, '%item)
      if items.getbyid(self[-1]).type=='linelist':
        for ii in items.getbyid(self[-1])[:-1]:
          f.write('%d, '%ii)
        f.write('%d };\n'%items.getbyid(self[-1])[-1])
      else:
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

# hold lists of land, island, and open boundary
landbdy=[]
islandbdy=[]
openbdy=[]

# make lists of point indizes for lines and splines
items=PointsItems()
surface=[]
boundary=[]
s=None
landnum=len(landbdys)

# add openbdy splines
for g in open_boundary.geoms:
  l = items.add('spline')
  xx,yy = g.xy
  for x,y in zip(xx,yy):
    l.append(points.add(x,y,'bres'))
  openbdy.append(l.id)
  boundary.append(l.id)

if False:
  figure()
  for s in splines:
    x,y=zip(*s)
    plot(x,y,'-',color='orange')
  for g in open_boundary.geoms:
    x,y = g.xy
    plot(x,y,'g-')
  #show()

if False:
# treatment as splines:
  for i,spline in enumerate(splines):
    s=items.add('spline',last=s)
    for p in spline:
      s.append(points.add(p[0],p[1],'cres'))

    if i>=landnum:
      # assume island
      s.closed=True
      surface.append(s)
      islandbdy.append(s.id)
    else:
      boundary.append(s.id)
      landbdy.append(s.id)
else:
#treatment as lines
  for i,spline in enumerate(splines):
    s=items.add('linelist',last=s)
    p1,p2=None,None
    for p in spline:
      p2 = points.add(p[0],p[1],'cres')
      if p1==None:
        p1=p2
      else:
        l = items.add('line')
        l.append(p1)
        l.append(p2)
        s.append(l.id)
        p1=p2

    if i>=landnum:
      # assume island
      s.closed=True
      s.type='lineloop'
      surface.append(s)
      islandbdy.append(s.id)
    else:
      boundary.append(s.id)
      landbdy.append(s.id)


s=items.add('lineloop',last=s)
s.extend(boundary)


if True:
  figure()
  if False:
    for i,p in enumerate(splines):
      x,y=zip(*p);x=list(x);y=list(y)
      plot(x,y,'k-')
      plot(x[0],y[0],'ko'); text(x[0],y[0],str(i),size=10)
    #plot(x[90:100],y[90:100],'o',color='k',ms=6.0)
  if False:
    for id in landbdy:
      x=[]
      y=[]
      for pid in items[id]:
        xx,yy = points.xy[pid]
        x.append(xx)
        y.append(yy)
      plot(x,y,'k-')
      plot(x[0],y[0],'ko'); text(x[0],y[0],str(id),size=10,color='k')
    


  for id in openbdy:
    x=[]
    y=[]
    for pid in items.getbyid(id):
      xx,yy = points.xy[pid]
      x.append(xx)
      y.append(yy)
    plot(x,y,'b-')
    plot(x[0],y[0],'bo'); text(x[0],y[0],str(id),size=10,color='b')
    
  for id in landbdy:
    x=[]
    y=[]
    item = items.getbyid(id)
    if item.type=='linelist':
      xx,yy=points.xy[items.getbyid(item[0])[0]]
      x.append(xx)
      y.append(yy)
      for iid in item:
        subitem = items.getbyid(iid)
        xx,yy=points.xy[subitem[1]]
        x.append(xx)
        y.append(yy)
    else:  
        xx,yy = points.xy[iid]
        x.append(xx)
        y.append(yy)
    plot(x,y,'-',color='orange')
    plot(x[0],y[0],'o',color='orange'); text(x[0],y[0],str(id),size=10,color='orange')
  show()

s.check_and_fix_sequence(items)

surface.append(s)

# todo: remove loops in linelists 


#dump data into .poly file:
f=open('coast.geo','w')
f.write("""
Mesh.CharacteristicLengthFromPoints = 1;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
""")
f.write('bres = %0.2f;\n'%10000.)
f.write('cres = %0.2f;\n'%10000.)

# set resolution at boundaries
for itemid in openbdy:
  for item in items:
    if item.id == itemid:
      break
  for pointid in item:
    points.modify(pointid,res='bres')

points.dump(f)

def write_linelist(f,item,notfirst=False):
  for ii in items.getbyid(item):
    if notfirst:
      f.write(', ')
    else:
      notfirst=True
    f.write('%d'%ii)
  return notfirst

def write_item(f,item,notfirst=False):
  if notfirst:
    f.write(', ')
  else:
    notfirst=True
  f.write('%d'%item)
  return notfirst
  

for item in items:
  item.dump(f,items)

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
f.write('Physical Line("islandbdy") = { ')
notfirst = False
for item in islandbdy:
  if items.getbyid(item).type in ['linelist','lineloop']:
    notfirst = write_linelist(f,item,notfirst)
  else:
    notfirst = write_item(f,item,notfirst)
f.write(' };\n')

# write single islands again
for ii,item in enumerate(islandbdy):
  if items.getbyid(item).type in ['linelist','lineloop']:
    f.write('Physical Line("islandbdy%d") = { '%ii)
    notfirst=False
    notfirst = write_linelist(f,item,notfirst)
    f.write(' };\n')

f.write('Physical Line("landbdy") = { ')
notfirst = False
for item in landbdy:
  if items.getbyid(item).type in ['linelist','lineloop']:
    notfirst = write_linelist(f,item,notfirst)
  else:
    notfirst = write_item(f,item,notfirst)
f.write(' };\n')

# write single landbdys again
for ii,item in enumerate(landbdy):
  if items.getbyid(item).type in ['linelist','lineloop']:
    f.write('Physical Line("landbdy%d") = { '%ii)
    notfirst=False
    notfirst = write_linelist(f,item,notfirst)
    f.write(' };\n')

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
Field[1].F = "20000.";

//Field[2] = Restrict;
//Field[2].IField = 1;
//Field[2].EdgesList = {%s};

Background Field = 1;
"""%(coastlist))

f.close()

#if write_pickle:
#  pf = open('coast_proj.pickle','wb')
#  pickle.dump((m,),pf,protocol=-1)
#  pf.close()
