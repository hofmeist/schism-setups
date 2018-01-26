import sys,os
from pylab import *

def windvel(t,tw=3*86400.,dtw=1.):
  return 3.0 + 12.0*exp(-((t/tw-abs(t/tw)-0.5)*tw/(2**(dtw/10.)))**2)

t = arange(0.0,32*86400.,3600.)

v = windvel(t)

plot(t,v,'k.-')

show()
