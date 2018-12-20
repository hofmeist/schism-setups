from pylab import *
from matplotlib.ticker import ScalarFormatter

proc=[36,72,144,252,540,1080,1620]
#proc=[36,72,144,252,540,1080]
basedir='/work/gg0877/hofmeist/arctic/scaling'

cpus = {}
for p in proc:
  with open('%s/pe%04d/mirror.out'%(basedir,p)) as f:
    cpus[p]=float(f.readlines()[-3].split()[1])

#cpus={36: 794., 72: 413., 144: 238., 252: 144.8, 540: 89.8, 1080: 69.0}

speedup = 86400./asarray(cpus.values())

loglog(cpus.keys(),speedup,'*',ms=15.0,mfc='r',basex=2,basey=2)
loglog([36,max(proc)],[speedup[0],max(proc)/36*speedup[0]],'--',lw=2.0,color=(0.5,0.5,0.5),basex=2,basey=2)
ax=gca()
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_major_formatter(ScalarFormatter())

ylabel('sim. days per cpu day')
xlabel('number of cores')
title('strong scaling on mistral')

show()



