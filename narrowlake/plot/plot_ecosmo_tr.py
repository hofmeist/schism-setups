from pylab import *
import numpy as np
import sys

def get_stspm(filename='total_TR.dat',ntracer=16):
   a = np.fromfile(filename,dtype=float,sep=' ').reshape(-1,ntracer)
   return a[:,0].squeeze(),a[:,1:]

if len(sys.argv)>2:
  savepdf=True
  pdfname = sys.argv[2]
else:
  savepdf=False

fig = figure(figsize=(5,8))
fig.subplots_adjust(left=0.25)

if False:
  days,tracer = get_stspm(sys.argv[1],ntracer=4)
  l = ''
  col='k'
  scol='orange'
  totC=tracer[:,2]
  semilogy(days[1:],(totC[1:]/totC[1])-1.0,'-',color=col,lw=2.0,label='generic tracer '+l)
  semilogy(days[1:],(tracer[1:,1]/tracer[0,1])-1.0,'-',color=scol,lw=2.0,label='salt '+l)

elif True:
  days,tracer = get_stspm(sys.argv[1],ntracer=16)
  l = ''
  col='k'
  scol='orange'
  totC=tracer[:,2] #no3
  totC+=tracer[:,3] #nh4
  totC+=tracer[:,7] #dia
  #totC+=tracer[:,9] #bg
  totC+=tracer[:,8] #fla
  totC+=tracer[:,10] #microzoo
  totC+=tracer[:,11] #mesozoo
  totC+=tracer[:,12] #det
  totC+=tracer[:,14] #dom
  semilogy(days[1:],(totC[1:]/totC[1])-1.0,'-',color=col,lw=2.0,label='total Nitrogen '+l)
  semilogy(days[1:],(tracer[1:,1]/tracer[0,1])-1.0,'-',color=scol,lw=2.0,label='salt '+l)
  #semilogy(days[1:],(tracer[1:,9]/tracer[0,9])-1.0,'-',color='red',lw=2.0,label='mixed, inactive tracer'+l)



legend(loc='lower left',frameon=False)
ylim(1.e-5,1.0)
ylabel('deviation from initial mass\nrelative to initial mass')
xlabel('days')
if savepdf:
  savefig(pdfname)
show()

fig = figure(figsize=(5,8))
fig.subplots_adjust(left=0.25)
plot(days[1:],tracer[1:,0]/tracer[0,0],lw=1.0)
show()

