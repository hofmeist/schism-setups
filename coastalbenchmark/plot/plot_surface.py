from pylab import *
import netCDF4
import sys,os

if len(sys.argv)>2:
  varname = sys.argv[2]
else:
  print('  usage: plot_surface.py file.nc variable')
  sys.exit(1)

fname=sys.argv[1]
period=int(fname.split('/')[-1].split('_')[0])
nc = netCDF4.Dataset(fname)
ncv = nc.variables

x = ncv['SCHISM_hgrid_node_x'][:]
y = ncv['SCHISM_hgrid_node_y'][:]
sigma = ncv['sigma'][:]
nsigma = len(sigma)
bidx = ncv['node_bottom_index'][:]
nv = ncv['SCHISM_hgrid_face_nodes'][:,:3]-1
time = ncv['time'][:]/86400. # d


var = ncv[varname]
#time = array([0.0])
cmap = cm.YlGnBu_r
cmap.set_under(color='w')

def mask_triangles(masknodes,nv):
  idx = where(masknodes)[0]
  nvmask = []
  for nodes in nv:
    if any(in1d(nodes,idx)):
      nvmask.append(True)
    else:
      nvmask.append(False)
  return asarray(nvmask)

dirname=varname+'_surface'
os.system('mkdir -p %s'%dirname)

contval=29.0
ccol=(0.4,0.4,0.4)

for tidx,t in enumerate(time):
  figure()
  v = var[tidx,-1,:].squeeze()
  #mask = v == -99.
  #mask = mask_triangles(mask,nv)
  tpc=tripcolor(x,y,nv,v,cmap=cmap,rasterized=True)
  clim(0,30)
  tricontour(x,y,nv,v,levels=[contval],colors=[ccol,])
  cb=colorbar(tpc)
  cb.ax.plot([0,1],[contval/30.,contval/30.],'-',color=ccol)
  cb.ax.set_title('%s\n'%(ncv[varname].long_name),size=10.)
  savefig('%s/%s_surface_%02d-%05d.jpg'%(dirname,varname,period,tidx),dpi=100)
  #show()
  close()


