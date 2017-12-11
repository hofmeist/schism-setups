#from pylab import *

o = open('hgrid_helgoland.ll','w')
i = open('hgrid.gr3')

line = i.readline()
o.write('%s'%line)

numel,numnd = [int(ii) for ii in i.readline().split()]
o.write('%d %d\n'%(numel,numnd))

for nd in range(numnd):
  line = i.readline()
  data = line.split()
  o.write('%s %0.2f %0.2f %s\n'%(data[0],7.9,54.2,data[3]))

for el in range(numel):
  line = i.readline()
  o.write('%s'%line)

i.close()
o.close()
