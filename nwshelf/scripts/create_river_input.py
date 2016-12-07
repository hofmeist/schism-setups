import netCDF4
import sys,os
sys.path.append(os.environ['HOME']+'/schism/setups/scripts')
from schism import schism_setup
import matplotlib
#matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime

plot_it=False
if plot_it:
  lonb=[-18., 32.]
  latb=[46., 67.]

  if os.path.isfile('proj.pickle'):
    (proj,)=np.load('proj.pickle')
  else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="i",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

s = schism_setup()

# read rivers:
nc = netCDF4.Dataset('/work/gg0877/rivers/river_loads_and_discharge_NSBS_orig.nc')
ncv=nc.variables
rlon = ncv['lon'][:]
rlat = ncv['lat'][:]
rdis = ncv['discharge'][:] # in m^3/s
jds = ncv['time'][:]

slist=''
idxs=[]
elids=[]
rlons=[]
rlats=[]
for idx,(rrlon,rrlat,rrdis) in enumerate(zip(rlon,rlat,rdis)):
  if isnan(rrlon) or isnan(rrlat):
    continue
  el_id = s.find_nearest_element(rrlon,rrlat,latlon=True,mindepth=5.0)
  slist+='%d\n'%(el_id)
  elids.append(el_id)
  idxs.append(idx)
  rlons.append(rrlon)
  rlats.append(rrlat)

f = open('source_sink.in','w')
f.write('%d   ! number of elements with sources\n'%len(elids))
f.write(slist)
f.write('0   ! number of elements with sinks\n')
f.close()

vf = open('vsource.th','w')
mf = open('msource.th','w')
ut = utime('seconds since 2012-01-01 00:00:00')
for tidx,jd in enumerate(jds):
  secs = ut.date2num(num2date(jd-366))
  if secs<0.0: continue
  vline='%12.1f'%secs
  tline=''
  sline=''
  for rrdis in rdis[tidx]:
    if isnan(rrdis): continue
    vline+=' %0.2f'%rrdis
    tline+=' -9999'
    sline+=' 0.0'
  vf.write(vline+'\n')
  mf.write('%12.1f %s %s\n'%(secs,tline,sline))
vf.close()
mf.close()

if plot_it:
  x,y = proj(s.londict.values(),s.latdict.values())
  nv = s.nvdict.values()
  depths = s.depthsdict.values()

  cmap=cm.jet
  tripcolor(x,y,asarray(nv)-1,depths,shading='flat',cmap=cmap)
  clim(0,10)
  colorbar()

  proj.drawcoastlines()
  #proj.fillcontinents((0.9,0.9,0.8))

  rx,ry = proj(rlon,rlat)
  plot(rx,ry,'+',markeredgecolor='magenta',mew=2.0,ms=12.)

  for rrlon,rrlat,idx in zip(rlons,rlats,elids):
    nodeids = s.nvdict[idx]
    nlons = [s.londict[i] for i in nodeids]
    nlats = [s.latdict[i] for i in nodeids]
    nxs,nys = proj(nlons,nlats)
    plot(nxs,nys,'o-',ms=3.0,lw=2.0,color='magenta',mec='magenta')

  savefig('river_map.png',dpi=600)
  show()
