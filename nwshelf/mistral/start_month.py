import commands
import sys

if len(sys.argv)<2:
  print('  Usage: start_month.py ID')
  sys.exit(1)
else:
  id = sys.argv[1]

out = commands.getoutput('sbatch run_mistral.sh %s'%id)
pid = out.split()[-1]

out = commands.getoutput('sbatch --dependency=afterok:%s merge_mistral.sh %s'%(pid,id))
pid = out.split()[-1]

out = commands.getoutput('sbatch --dependency=afterok:%s plot/run_plotting.sh nwshelf/nwshelf%s'%(pid,id))
pid = out.split()[-1]


