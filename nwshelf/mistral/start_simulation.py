import commands
import sys
import os

if len(sys.argv)<2:
  print('  Usage: start_month.py ID')
  sys.exit(1)
else:
  id = sys.argv[1]

def log_directive(id,yyyymm,logname='log'):
  logstr='--output=/scratch/g/g260078/schism-results/nwshelf%s/%s_%s.o'%(id,logname,yyyymm)
  logstr+=' --error=/scratch/g/g260078/schism-results/nwshelf%s/%s_%s.e'%(id,logname,yyyymm)
  return logstr

years=[2012,2013,2014,2015]
years=[2012]

months=range(1,13)
#months=[1,2,3]
#months=range(11,13)

rundep=''
debug=False
if debug: out="1 1"
# create output directory for log-files
os.system('mkdir -p /scratch/g/g260078/schism-results/nwshelf%s'%id)

for year in years:
  for month in months:
    yyyymm='%04d-%02d'%(year,month)
    print('hotstart period %s'%yyyymm)

    logrun=log_directive(id,yyyymm,logname='log')
    loghot=log_directive(id,yyyymm,logname='log_hmerge')
    logmerge=log_directive(id,yyyymm,logname='log_merge')

    # run the model
    cmd = 'sbatch %s %s mistral/run_hotstart.sh %s %s'%(rundep,logrun,id,yyyymm)
    if debug:
      print(cmd)
    else:
      out = commands.getoutput(cmd)
    pid = out.split()[-1]

    # merge hotstart files
    cmd = 'sbatch --dependency=afterok:%s %s mistral/merge_hotstart.sh %s %s'%(pid,loghot,id,yyyymm)
    if debug:
      print(cmd)
    else:
      out = commands.getoutput(cmd)
    hmerge_pid = out.split()[-1]
    rundep = '--dependency=afterok:%s'%hmerge_pid
    
    # merge output
    cmd = 'sbatch --dependency=afterok:%s %s mistral/merge_mistral.sh %s %s'%(pid,logmerge,id,yyyymm)
    if debug:
      print(cmd)
    else:
      out = commands.getoutput(cmd)
    omerge_pid = out.split()[-1]

    # do plotting
    #out = commands.getoutput('sbatch --dependency=afterok:%s plot/run_plotting.sh nwshelf/nwshelf%s/%s'%(omerge_pid,id,yyyymm))
    #pid = out.split()[-1]


