import commands
import sys

if len(sys.argv)<2:
  print('  Usage: start_month.py ID')
  sys.exit(1)
else:
  id = sys.argv[1]

years=[2012,2013,2014,2015]
years=[2012]

months=range(1,13)
months=[2]

rundep=''

for year in years:
  for month in months:
    yyyymm='%04d-%02d'%(year,month)

    # run the model
    out = commands.getoutput('sbatch %s mistral/run_hotstart.sh %s %s'%(rundep,id,yyyymm))
    pid = out.split()[-1]

    # merge hotstart files
    out = commands.getoutput('sbatch --dependency=afterok:%s mistral/merge_hotstart.sh %s %s'%(pid,id,yyyymm))
    hmerge_pid = out.split()[-1]
    rundep = '--dependency=afterok:%s'%hmerge_pid
    
    # merge output
    out = commands.getoutput('sbatch --dependency=afterok:%s mistral/merge_mistral.sh %s %s'%(pid,id,yyyymm))
    omerge_pid = out.split()[-1]

    # do plotting
    out = commands.getoutput('sbatch --dependency=afterok:%s plot/run_plotting.sh nwshelf/nwshelf%s/%s'%(omerge_pid,id,yyyymm))
    pid = out.split()[-1]


