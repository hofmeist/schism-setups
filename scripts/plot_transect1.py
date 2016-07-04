from pylab import *
import numpy as np

a = np.loadtxt('transect1.out')
z_m = np.loadtxt('vgrid_master.out')
z_idx=z_m[:,0].copy()
z_m = z_m[:,3:]

d = a[:,4]
x = a[:,2]
y = a[:,3]
bidx= a[:,1].astype('int')

z_m = ma.masked_equal(z_m, -100000.)

z = a[:,7:]

dnum,znum = z.shape

levels = arange(znum)

d2d,l2d =np.meshgrid(d,levels)

plot(d2d.T,z,'k.-',lw=0.6)
plot(d2d,z.T,'k.-',lw=0.6)

z_master = 9000*ones(z.shape)
for i,bi in enumerate(bidx):
  n_z = bi-21
  if n_z > 0:
    z_master[i,:bi]=z_m[n_z,:bi]

z_master = ma.masked_equal(z_master,9000)
mcol=(0.4,0.4,1.0)
plot(d2d.T,z_master,'.-',color=mcol,lw=0.4,alpha=0.8)


show()


