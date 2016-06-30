import os
import sys
from pylab import *

opath='/scratch/g/g260078/schism-results'
numnodes=[4,8,16,32,64,128]
numnodes=[4,8,16,32,64]

runtimes = []

for num in numnodes:
  f = open('%s/weakscaling%d/log%04d.o'%(opath,num,num))
  f.readline()
  f.readline()
  time = float(f.readline().split()[-1])
  f.close()
  runtimes.append(time)

runtimes = 3600./asarray(runtimes)
numnodes = asarray(numnodes)
proc = numnodes*24

ideal_runtime = runtimes[0]*ones((len(runtimes)))

semilogx(proc,ideal_runtime,'k-',lw=2.0,basex=2,label='ideal scaling')
semilogx(proc,runtimes,'r*--',lw=3.0,ms=15.0,markerfacecolor='r',basex=2,label='MISTRAL scaling')

xlim(80,5000)
ylim(150,300)

ax=gca()
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

title('weak scaling SCHISM on MISTRAL')
xlabel('number of cores')
ylabel('simulated time vs. runtime')
legend(loc='upper right',frameon=False)

savefig('weak_scaling_mistral.pdf',dpi=100)
show()
