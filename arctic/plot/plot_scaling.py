from pylab import *
from matplotlib.ticker import ScalarFormatter

cpus={36: 794., 72: 413., 144: 238., 252: 144.8, 540: 89.8, 1080: 69.0}

loglog(cpus.keys(),cpus[36]/asarray(cpus.values()),'*',ms=15.0,mfc='r',basex=2,basey=2)
loglog([36,1080],[1,30],'--',lw=2.0,color=(0.5,0.5,0.5),basex=2,basey=2)
ax=gca()
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_major_formatter(ScalarFormatter())

ylabel('speedup [comp. to 1 node]')
xlabel('number of cores')
title('strong scaling on mistral')

show()



