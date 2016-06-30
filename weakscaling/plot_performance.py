import os
import sys
from pylab import *

opath='/scratch/g/g260078/schism-results'
numnodes=[4,8,16,32,64,128]

runtimes = []

for num in numnodes:
  f = open('%s/weakscaling%d/log%04d.o'%(opath,num,num))
  time = float(f.readline().split()[-1])
  f.close()
  runtimes.append(time)

runtimes = 3600./asarray(runtimes)
numnodes = asarray(numnodes)
proc = numnodes*24

ideal_runtime = runtime[0]*ones((len(runtimes)))

semilogx(proc,ideal_runtime,'k-',lw=2.0,basey=2,basex=2,label='ideal speed')
semilogx(proc,runtimes,'r*--',lw=3.0,ms=15.0,markerfacecolor='r',basey=2,basex=2,label='MISTRAL runtime')

xlim(80,10000)
#ylim(0.5,50)

ax=gca()
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

title('weak scaling SCHISM on MISTRAL')
xlabel('number of cores')
ylabel('simulated time vs. runtime')
legend(loc='upper right',frameon=False)

savefig('weak_scaling_mistral.pdf',dpi=100)
show()
