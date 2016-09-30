import commands
import sys

if len(sys.argv)<2:
  print('  Usage: start_pp.py ID')
  sys.exit(1)
else:
  id = sys.argv[1]

cmd = 'sbatch merge_mistral.sh %s'%(id)
out = commands.getoutput(cmd)
pid = out.split()[-1]
print(cmd)

cmd = 'sbatch --dependency=afterok:%s plot/run_plotting.sh nwshelf/nwshelf%s'%(pid,id)
out = commands.getoutput(cmd)
pid = out.split()[-1]
print(cmd)

