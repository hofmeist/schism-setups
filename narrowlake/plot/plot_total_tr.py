from pylab import *
import numpy as np
import sys

def get_stspm(filename='total_TR.dat',ntracer=4):
   a = np.fromfile(filename,dtype=float,sep=' ').reshape(-1,ntracer)
   return a[:,0],a[:,1],a[:,2],a[:,3]

if len(sys.argv)>1:
  savepdf=True
  pdfname = sys.argv[1]
else:
  savepdf=False

files  = ['total_TR.dat']
files  = ['results/total_TR_lsc2.dat','results/total_TR_diff1e-5.dat','total_TR.dat']#'total_TR_diff1e-3.dat']
labels = ['diff 1.e-4','diff 1.e-5','diff=1.e-1, dt=200s']
cfacs = [0.0,0.4,0.8]

fig = figure(figsize=(5,8))
fig.subplots_adjust(left=0.25)

for cfac,l,filen in zip(cfacs,labels,files):
  days,t,s,spm = get_stspm(filen)
  col = cfac*ones((3,))
  if cfac==cfacs[-1]:
   scol='orange'
  else:
   scol='r'
  plot(days[1:],spm[1:]/spm[1],'-',color=col,label='SPM '+l)
  plot(days[1:],s[1:]/s[1],'-',color=scol,label='salt '+l)

legend(loc='lower left',frameon=False)
#ylim(0.9,1.1)
ylabel('total salt,SPM (relative to initial mass)')
xlabel('days')
if savepdf:
  savefig(pdfname)
show()

