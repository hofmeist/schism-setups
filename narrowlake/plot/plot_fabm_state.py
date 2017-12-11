from pylab import *
import netCDF4
from matplotlib.collections import PolyCollection

nc = netCDF4.Dataset('fabm_state_000000.nc')
ncv=nc.variables

t = ncv['time'][:]
y = ncv['node_y'][:]
x = ncv['node_x'][:]

s = ncv['hzg_ecosmo_sed2'][:]
nv = ncv['nv'][:,:3]-1

verts=[]
for nvi in nv:
  verts.append([(x[i],y[i]) for i in nvi])
verts=asarray(verts)

f=figure(figsize=(15,5))

p = PolyCollection(verts,closed=True,edgecolor='none')
p.set_array(s[0])
p.set_cmap(cm.RdYlBu_r)

pn = PolyCollection(verts,closed=True,edgecolor='none')
pn.set_array(arange(len(s[0])))
pn.set_cmap(cm.RdYlBu_r)

ax=axes([0.1,0.75,0.88,0.2])
ax.add_collection(p,autolim=True)
autoscale()
colorbar(p)

ax=axes([0.1,0.25,0.88,0.2])
ax.add_collection(pn,autolim=True)
autoscale()
colorbar(pn)

show()
