import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime

if len(sys.argv)>2:
  varname = sys.argv[2]
else:
  print('  usage: plot_bott_surf.py file.nc variable')
  sys.exit(1)

if len(sys.argv)>3:
  tidx=int(sys.argv[3])
else:
  tidx=-1

if len(sys.argv)>4:
  try:
    s1,s2 = sys.argv[4].split(',')
    vmin,vmax = float(s1),float(s2)
    uselim=True
  except:
    uselim=False
else:
  uselim=False
  

nc = netCDF4.Dataset(sys.argv[1])
ncv = nc.variables

lon = ncv['SCHISM_hgrid_node_x'][:]
lat = ncv['SCHISM_hgrid_node_y'][:]
#sigma = ncv['sigma'][:]
#nsigma = len(sigma)
#bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:] # s
ut = utime(ncv['time'].units)
dates = ut.num2date(time)

lonb=[0., 10.]
latb=[49., 55.]

if os.path.isfile('proj_issue.pickle'):
    (proj,)=np.load('proj_issue.pickle')
else:
    proj=Basemap(projection="merc", lat_ts=0.5*(latb[1]+latb[0]), resolution="i",llcrnrlon=lonb[0], urcrnrlon=lonb[1], llcrnrlat=latb[0], urcrnrlat=latb[1])
    f=open('proj_issue.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

x,y = proj(lon,lat)

if varname=='dz':
  ncvarname='zcor'
elif varname=='nlayers':
  ncvarname='depth'
else:
  ncvarname=varname

var = ncv[ncvarname]
#time = array([0.0])
cmap = cm.YlGnBu
#cmap.set_under(color='w')

def mask_triangles(masknodes,nv):
  idx = where(masknodes)[0]
  nvmask = []
  for nodes in nv:
    if any(in1d(nodes,idx)):
      nvmask.append(True)
    else:
      nvmask.append(False)
  return asarray(nvmask)

bidx = ncv['node_bottom_index'][:]
nbidx = len(bidx)
nvrt = len(nc.dimensions['nSCHISM_vgrid_layers'])

if tidx >= 0:
  dates = [dates[tidx],]
  tidx_offset=tidx
else:
  tidx_offset=0

os.system('mkdir -p jpgs/%s'%varname)
for tidx,t in enumerate(dates):
  if varname=='depth':
    vs=var[:].squeeze()
    plot_bottom=False
    plot_surface=True
  elif varname=='dz':
    v = var[tidx+tidx_offset,:].squeeze()
    vs=v[-1,:].squeeze()-v[-2,:].squeeze()
    vb=v[bidx+1,arange(nbidx)].squeeze()-v[bidx,arange(nbidx)].squeeze()
    plot_surface=True
    plot_bottom=True
  elif varname=='nlayers':
    vs = nvrt-bidx
    plot_bottom=False
    plot_surface=True
  else:
    v = var[tidx+tidx_offset,:].squeeze()
    if varname=='elev':
      vs = v
      plot_surface=True
      plot_bottom=False
    else:
      vs = v[:,-1].squeeze()
      print(bidx.max(),bidx.min())
      print(v.shape)
      vb = v[arange(nbidx),bidx]
      plot_surface=True
      plot_bottom=True
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  if plot_surface:
    figure()
    if varname=='elev':
      cmap=cm.RdYlGn
      cmap.set_under('gray')

    if varname=='nlayers':
      tricontour(x,y,nv,vs,levels=arange(nvrt),linewidths=0.3)
    else:
      tripcolor(x,y,nv,vs,cmap=cmap,rasterized=False)
    if varname=='salt':
      if ~uselim:
        clim(5,35)
      cbtitle='surface salinity'
    elif varname=='temp':
      clim(1,vs.max())
      cbtitle=u'surface temperature\n[\u00b0C]'
    elif varname=='elev':
      if uselim:
        clim(vmin,vmax)
      cbtitle='ssh [m]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vs.max())
      cbtitle=varname
    if uselim:
      clim(vmin,vmax)
    #proj.drawcoastlines()
    #proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title(u'%s\n'%(cbtitle),size=10.)
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_issue_surface_%s.jpg'%(varname,varname,tstring),dpi=1200)
    if varname=='nlayers':
      savefig('jpgs/%s/%s_issue_%s.pdf'%(varname,varname,tstring),dpi=1200)
    close()

  if plot_bottom:
    figure()
    tripcolor(x,y,nv,vb,cmap=cmap,rasterized=False)
    if varname=='salt':
      clim(5,35)
      cbtitle='bottom salinity'
    elif varname=='temp':
      clim(1,vb.max())
      cbtitle=u'bottom temperature\n[\u00b0C]'
    else:
      if uselim:
        clim(vmin,vmax)
      else:
        clim(0,vb.max())
      cbtitle=varname
    if uselim:
      clim(vmin,vmax)
    #proj.drawcoastlines()
    #proj.fillcontinents((0.9,0.9,0.8))
    cb=colorbar()
    cb.ax.set_title(u'%s\n'%(cbtitle),size=10.)
    tstring = t.strftime('%Y%m%d-%H%M')
    savefig('jpgs/%s/%s_issue_bottom_%s.jpg'%(varname,varname,tstring),dpi=1200)

    #show()
    close()


