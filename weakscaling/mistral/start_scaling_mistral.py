import commands
import os
import sys

proc_pr_node = 24
numnodes = [4,8,16,32,64,96,128]
numnodes = [4,8,16,32,64,96]
#numnodes = [4,8]
#numnodes = [16,32,64,128]
#numnodes = [96]
#numnodes = [32,64,128,256]

depstring = ''
for numnode in numnodes:
  id = '%d'%numnode
  ntasks = numnode*proc_pr_node
  command = 'sbatch %s --ntasks=%d --ntasks-per-node=%d --error=log%04d.e --output=log%04d.o mistral/run_mistral.sh %s'%(depstring,ntasks,proc_pr_node,numnode,numnode,id)
  print(command)
  err,out = commands.getstatusoutput(command)
  depstring = ' --dependency=afterok:%s'%out.split()[-1]



