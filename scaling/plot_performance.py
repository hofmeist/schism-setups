import os
import sys
from pylab import *

opath='/scratch/g/g260078/schism-results'
numnodes=[4,8,16,32,64,128]

runtimes = []

for num in numnodes:
  f = open('%s/scaling%04d/log%04d.o'%(opath,num,num))
  time = float(f.readline().split()[-1])
  f.close()
  runtimes.append(time)

runtimes = asarray(runtimes)
numnodes = asarray(numnodes)
proc = numnodes*24

speedup = runtimes[0]/runtimes
ideal_speedup = numnodes/numnodes[0]

loglog(proc,ideal_speedup,'k-',lw=2.0,basey=2,basex=2,label='ideal speedup')
loglog(proc,speedup,'r*--',lw=3.0,ms=15.0,markerfacecolor='r',basey=2,basex=2,label='MISTRAL speedup')

xlim(80,10000)
ylim(0.5,50)

ax=gca()
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

title('strong scaling SCHISM on MISTRAL')
xlabel('number of cores')
ylabel('speedup normalized to 96 cores')
legend(loc='lower right',frameon=False)

savefig('strong_scaling_mistral.pdf',dpi=100)
show()
