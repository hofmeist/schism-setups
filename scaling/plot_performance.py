import os
import sys
from pylab import *

opath='/scratch/g/g260078/schism-results'
label="schism 11 layers, 1000k nodes"
#opath='/work/gg0877/hofmeist/scaling/dt036s/'
#opath='/work/gg0877/hofmeist/scaling/'
numnodes=[4,8,16,32,64,128,256]
#numnodes=[4,8,16,32,64,128]

runtimes = []
figure()

for num in numnodes:
    f = open('%s/scaling_11layers_%04d/log%04d.o'%(opath,num,num))
    time = float(f.readline().split()[-1])
    f.close()
    runtimes.append(time)

runtimes = asarray(runtimes)
numnodes = asarray(numnodes)
proc = numnodes*24

speedup = runtimes[0]/runtimes
loglog(proc,speedup,'r*--',lw=3.0,ms=15.0,markerfacecolor='r',basey=2,basex=2,label=label)


ideal_speedup = numnodes/numnodes[0]
loglog(proc,ideal_speedup,'k-',lw=2.0,basey=2,basex=2,label='ideal speedup')

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
