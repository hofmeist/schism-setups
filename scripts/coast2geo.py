from pylab import *
from mpl_toolkits.basemap import Basemap
    

# set surrounding points
xl=3.0
xu=9.0
yu=57.0
yl=50.5

m = Basemap(projection='lcc',
                       resolution='h',area_thresh=10.,
                       llcrnrlon=xl,
                       llcrnrlat=yl,
                       urcrnrlon=xu,
                       urcrnrlat=yu,
                       lat_0=53.0,
                       lon_0=8.0)

mxu,myu=m(xu,yu)
mxl,myl=m(xl,yl)
landresolution=200.

# get coast polygon
polys = m.coastpolygons
land=[]
for xp,yp in polys:
  land.append(zip(xp,yp))

newland=[]

dd = 3*landresolution
newland.append([(mxl-dd,myl-dd),(mxl-dd,myu+dd),(mxu+dd,myu+dd),(mxu+dd,myl-dd)])

count=0
for poly in land:
    newpoly=[]
    newpoly.append(poly.pop(0))
    x0,y0=newpoly[-1]
    check=True
    while check:
      try:
        x1,y1=poly.pop(0)
      except:
        check=False
        next
      #print("%0.2f %0.2f %0.2f %0.2f"%(x0,y0,x1,y1))
      dist=sqrt((x1-x0)**2 + (y1-y0)**2)
      if (dist>landresolution and len(poly)>0):
        newpoly.append((x1,y1))
        x0=x1;y0=y1
        count+=1
    newland.append(newpoly)

figure()
for p in newland:
  x,y=zip(*p);x=list(x);y=list(y)
  plot(x,y,'o-')
#plot(x[90:100],y[90:100],'o',color='k',ms=6.0)
show()

#dump data into .poly file:
f=open('coast.geo','w')
ip=1
iline=1
loops=[]
lines=[]

for p in newland:
  #x,y = zip(*p)
  loopstart = iline
  for ii,(x,y) in enumerate(p):
    f.write('Point(%d) = {%0.2f, %0.2f, 0, %0.2f};\n'%(ip,x,y,landresolution))
    if ii==0:
      lines.append((ip+len(p)-1,ip))
    else:
      lines.append((ip-1,ip))
    iline+=1
    ip+=1
  loops.append(range(loopstart,iline))

for iline,line in enumerate(lines):
  f.write('Line(%d) = {%d, %d};\n'%(iline+1,line[0],line[1]))

numlines=len(lines)
for iloop,loop in enumerate(loops):
  f.write('Line Loop(%d) = {'%(iloop+numlines+1))
  for iline in loop:
    if iline==loop[-1]:
      f.write('%d };\n'%iline)
    else:
      f.write('%d, '%iline)

numloops=len(loops)
f.write('Plane Surface(%d) = {'%(numloops+numlines+1))
for iloop in range(numloops):
  if iloop==numloops-1:
   f.write('%d };\n'%(iloop+1+numlines))
  else:
   f.write('%d, '%(iloop+1+numlines))


f.close()


