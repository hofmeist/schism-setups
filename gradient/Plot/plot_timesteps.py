from pylab import *
import netCDF4
import sys

runs = {}
if len(sys.argv)>1:
  name = sys.argv[1]
else:
  name='test'


runs[5] = name+'_5s'
runs[10] = name+'_10s'
runs[25] = name+'_25s'
runs[37] = name+'_37s'
runs[50] = name+'_50s'
runs[100] = name+'_100s'
runs[200] = name+'_200s'

lss = ['-','--',':','-.','-..']
tidx = 477

fig = figure(figsize=(8,5))
tax=axes()
vf = figure(figsize=(8,5))
vax=axes()

keys = sorted(runs)

for dt in keys:
  folder = runs[dt]
  label = '%d s'%dt

  nc = netCDF4.Dataset('%s/outputs/1_salt.nc'%folder)
  ncv=nc.variables

  t = ncv['time'][:]
  y = ncv['y'][:]
  yidx = where(y==0.0)
  s = ncv['salt'][tidx,-1][yidx]-35.
  x = ncv['x'][yidx]/1000.

  vnc = netCDF4.Dataset('%s/outputs/1_hvel.nc'%folder)
  vncv = vnc.variables
  xidx=21+11
  v = vncv['u'][-25:,-1,xidx]
  vt = vncv['time'][-25:]
  hours = (vt-vt[0])/3600.
  
  if label=='50 s':
    col = 'r'
    ls = '-'
    s0 = ncv['salt'][0,-1][yidx]-35.
    tax.plot(x,s0,'-',lw=3.0,color='orange',label='initial condition')
  else:
    col = (log(int(label[:-2]))/log(5)/3.-0.3)*ones((3))
    ls = '-'#lss.pop()
    

  tax.plot(x,s,ls=ls,color=col,lw=2.0,label=label)
  vax.plot(hours,v,ls=ls,color=col,lw=2.0,label=label)

  nc.close()
  vnc.close()

tax.set_ylim(-0.1,1.1)
tax.set_ylabel('Tracer [1/1]')
tax.set_xlabel('km')
tax.legend(loc='upper left',frameon=False)

vax.set_ylim(-0.2,0.2)
vax.set_ylabel('surface current [m/s]')
vax.set_xlabel('time [h]')
vax.legend(loc='upper left',frameon=False)

fig.savefig('transport_comparison_%s.pdf'%name)
show(fig)

vf.savefig('velocity_comparison_%s.pdf'%name)
show(vf)
