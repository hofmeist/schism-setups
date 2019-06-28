import os
import sys
from pylab import *

opath='/gpfs/work/%s/schism-results'%os.environ['USER']
label="schism 11 layers, 1000k nodes"
cpus_pr_node=[24,48]
cpus_pr_node=[24,48]

scale=1.0

figure()

for cpu in cpus_pr_node:
  runtimes = []
  if cpu==48:
    numnodes=[2,4,8,16,20]
    color='r'
  if cpu==24:
    numnodes=[4,8,16,20]
    numnodes=[4,8,16,20]
    color='b'
  label='1000k nodes, %d tasks/node'%cpu
  for num in numnodes:
    f = open('%s/scaling_%dp/scaling_%04d/mirror.out'%(opath,cpu,num))
    for line in f.readlines():
      if line[:13]==' pure_runtime':
        time = float(line.split()[-1])
    f.close()
    runtimes.append(time)

  runtimes = asarray(runtimes)
  numnodes = asarray(numnodes)
  proc = numnodes*cpu

  if cpu==24:
    scale = runtimes[0]

  speedup = scale/runtimes
  loglog(proc,speedup,'*--',color=color,lw=3.0,ms=15.0,markerfacecolor=color,basey=2,basex=2,label=label)


ideal_proc=asarray([96,1000])
ideal_speedup = ideal_proc/96
loglog(ideal_proc,ideal_speedup,'k-',lw=2.0,basey=2,basex=2,label='ideal speedup')

xlim(80,1050)
ylim(0.5,12)
grid()

ax=gca()
for axis in [ax.xaxis, ax.yaxis]:
    axis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

title('strong scaling SCHISM on strand')
xlabel('number of cores')
ylabel('speedup normalized to 96 cores on 4 nodes')
legend(loc='upper left',frameon=False)

savefig('strong_scaling_strand.png',dpi=100)
show()
