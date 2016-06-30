from pylab import *
#from matplotlib.collections import PolyCollection
import matplotlib.tri as tri
import os,pickle
#from plotting import *

def read_gr3(filename='hgrid.gr3'):
  f = open(filename)
  fname = f.readline()
  numelements,numnodes = f.readline().split()
  numnodes=int(numnodes)
  numelements=int(numelements)  

  el={}
  depth={}
  verts={}

  for num in range(1,numnodes+1):
    data = f.readline().split()
    num=int(data[0])
    lon=float(data[1])
    lat=float(data[2])
    d=float(data[3])
    el[num]=(lon,lat)
    depth[num] = d

  for line in f.readlines()[:numelements]:
    data = line.split()
    num = int(data[0])
    numverts = int(data[1])
    if numverts!=3:
      print(data)
    v = [ int(dd) for dd in data[2:2+numverts]]
    verts[num]=v

  return el,verts,depth

if len(sys.argv)>1:
  filename=sys.argv[1]
else:
  filename='hgrid.gr3'

el,verts,depth = read_gr3(filename=filename)

fig = figure()
ax=axes()

lons=[]
lats=[]
v = []
d = []

for num,coords in el.iteritems():
  lons.append(coords[0])
  lats.append(coords[1])

for num,ijk in verts.iteritems():
  i,j,k = verts[num]
  xs = (el[i][0],el[j][0],el[k][0])
  ys = (el[i][1],el[j][1],el[k][1])
  v.append(zip(xs,ys))
  d.append(depth[i])
  #plot(xs,ys,'k-',lw=0.2)
  #if num%10000==0:
  #  print(num)

d = asarray(d)

#print len(verts),verts[1]
#print depth[1],depth[2],depth[3],depth[4]
#print d[:4]
#print(cm.jet(d[:4]/200.))


#triplot(lons,lats,asarray(verts.values())-1,'k-',linewidth=0.1)
# set map boundaries

lonb=[-10., 10.]
latb=[48., 58]

xx,yy = lons,lats
#triang = tri.Triangulation(xx,yy)

#cmap = cm.ocean_r
#tripcolor(xx,yy,asarray(verts.values())-1,depth.values(),shading='flat',cmap=cmap)
#clim(0,60)
#colorbar()

#tripcolor(lons,lats,asarray(verts.values())-1,facecolors=cm.jet(d/200.),edgecolors='none')

if False:
  coll = PolyCollection(v,array=d,cmap=cm.jet,edgecolors='none')
  ax.add_collection(coll)
  ax.autoscale_view()
  colorbar(coll)

#plot(lons,lats,'k.')

#savefig('%s_bathymetry.png'%(filename.split('.')[0]),dpi=600)
#show()

figure()

triplot(xx,yy,'k-',lw=0.3)
#xlim(0,10000)
#ylim(0,10000)

savefig('%s_grid.pdf'%(filename.split('.')[0]))
show()


    
