import commands
import os
import sys

proc_pr_node = 24
numnodes = [4,8,16,32,64,128,256]
numnodes = [4,8,16,32,64]
numnodes = [4]

depstring = ''
for numnode in numnodes:
  id = 'scaling%04d'%numnode
  command = 'sbatch %s --ntasks=%d --ntasks-per-node=%d --error=log%04d.e --output=log%04d.o run_mistral.sh %s'%(depstring,numnode,proc_pr_node,numnode,numnode,id)
  err,out = commands.getstatusoutput(command)
  depstring = ' --dependency=afterok:%s'%out.split()[-1]



