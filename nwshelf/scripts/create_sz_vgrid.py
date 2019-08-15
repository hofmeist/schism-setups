from pylab import *

nsigma=6

z=[-5000,-4000] # all depths above -4500., so this value is not needed 

z.extend(range(-3750,-500,250))

z.extend(range(-500,-300,100))

z.extend(range(-300,-250,50))

z.extend(range(-250,-150,25))

z.extend(range(-150,-100,10))

z.extend(range(-100,-55,5))

z.extend(range(-55,-10,3))

z.extend([-10.])

nvrt = len(z)-1+nsigma

f = open('vgrid_sz.in','w')
f.write('''2 ! 1-LSC2 2-SZ
%d %d 10.
Z levels
'''%(nvrt,len(z)))

for i,zz in enumerate(z):
  print(zz)
  f.write('%d %0.0f\n'%(i+1,float(zz)))

f.write('S levels\n')
f.write('9. 0.001 0.001\n')

ioff = len(z)
for i in range(nsigma):
  sigma = -1.+i/(nsigma-1.0)
  f.write('%d %0.2f\n'%(ioff+i,sigma))

f.close()



