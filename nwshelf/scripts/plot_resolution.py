from pylab import *
#from matplotlib.collections import PolyCollection
import matplotlib.tri as tri
from mpl_toolkits.basemap import Basemap
import sys,os,pickle
#from plotting import *
sys.path.append('/local/home/hofmeist/schism/setups/scripts')
from schism import *

s = schism_setup()

fig = figure()
ax=axes()


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

xx,yy = proj(s.lon,s.lat)

cmap = cm.jet
tripcolor(xx,yy,asarray(s.nv)-1,asarray(s.resolution_by_nodes.values()),shading='flat',cmap=cmap)
cb=colorbar()
cb.set_label('grid resolution [m]')

proj.drawcoastlines()
#proj.fillcontinents((0.9,0.9,0.8))
savefig('grid_resolution.png',dpi=600)
show()




    
