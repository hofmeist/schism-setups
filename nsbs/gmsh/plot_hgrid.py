from pylab import *
import os,pickle

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

d = asarray(d)
xx,yy = lons,lats

figure()

triplot(xx,yy,asarray(verts.values())-1,'k-',lw=0.1)

savefig('%s_grid.pdf'%(filename.split('.')[0]))
show()


    
