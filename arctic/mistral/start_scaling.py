import subprocess as sub
import sys
import os

def log_directive(id,logname='log'):
  basedir='/work/gg0877/hofmeist/arctic/scaling'
  logstr='--output=%s/%s/%s.o'%(basedir,id,logname)
  logstr+=' --error=%s/%s/%s.e'%(basedir,id,logname)
  return logstr

procs=[36,72,144,252,540,1080,1620,2160]
#procs=[36,72,144,252,540,1080]
#procs=[1620,2160]
procs=[144,252,540,1080,1620,2160]
procs=[36,72]#,144,252,540,1080,1620,2160]

rundep=''
debug=False
if debug: out="99 99"

# link hotstart.nc before to some spinned-up time
cmd='rm -f hotstart.nc && ln -sf /work/gg0877/hofmeist/arctic/arctic006/2012-02/hotstart.nc hotstart.nc'
cmd='rm -f hotstart.nc && ln -sf /work/gg0877/hofmeist/arctic/arcticice002/2012-02/hotstart.nc hotstart.nc'
if debug:
  print(cmd)
else:
  os.system(cmd)

for proc in procs:
    runid='icepe%04d'%proc
    print('scaling test %d proc'%proc)
    # create output directory for log-files
    cmd='mkdir -p /work/gg0877/hofmeist/arctic/scaling/%s'%runid
    if debug:
      print(cmd)
    else:
      os.system('mkdir -p /work/gg0877/hofmeist/arctic/scaling/%s'%runid)

    logrun=log_directive(runid,logname='log')

    # run the model
    cmd = 'sbatch %s %s --ntasks=%d mistral/run_scaling.sh %s'%(rundep,logrun,proc,runid)
    if debug:
      print(cmd)
    else:
      out = sub.check_output(cmd.split(),universal_newlines=True)
    pid = out.split()[-1]
    rundep = '--dependency=afterok:%s'%pid

