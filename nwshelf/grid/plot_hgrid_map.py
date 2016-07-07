from pylab import *
#from matplotlib.collections import PolyCollection
import matplotlib.tri as tri
from mpl_toolkits.basemap import Basemap
import sys,os,pickle
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
  filename='../hgrid.gr3'
if len(sys.argv)>2:
  maxdepth=float(sys.argv[2])
else:
  maxdepth=200.

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

# set map boundaries

lonb=[-18., 32.]
latb=[46., 67.]

if os.path.isfile('proj.pickle'):
    (proj,)=np.load('proj.pickle')
else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="h",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

xx,yy = proj(lons,lats)

cmap = cm.ocean_r
tripcolor(xx,yy,asarray(verts.values())-1,depth.values(),shading='flat',cmap=cmap)
clim(0,maxdepth)
colorbar()

proj.drawcoastlines()
proj.fillcontinents((0.9,0.9,0.8))
savefig('%s_bathymetry.png'%(filename.split('.')[0]),dpi=600)
show()


# show the grid again

figure()

triplot(xx,yy,asarray(verts.values())-1,'k-',lw=0.1)
proj.drawcoastlines()
proj.fillcontinents((0.9,0.9,0.8))

#savefig('%s_grid.pdf'%(filename.split('.')[0]))
show()


    
