from pylab import *

def read_msource(nsources):
  f = open('msource.th')
  conc = []
  time = []
  for line in f.readlines():
    dat = line.split()
    time.append(float(dat[0]))
    conc.append(asarray([float(item) for item in dat[1:]]).reshape(-1,nsources))
  f.close()
  return asarray(time),asarray(conc)


f=open('source_sink.in')
nsources=float(f.readline().split()[0])
f.close()

time,conc=read_msource(nsources)

