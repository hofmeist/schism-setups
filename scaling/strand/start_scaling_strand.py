import commands
import os
import sys

proc_pr_node = 48 
numnodes = [2,16,20]
numnodes = [4,8,16,20]
numnodes = [6,10,16,20,60,80,120]

depstring = ''
for numnode in numnodes:
  id = 'scaling_%04d'%numnode
  ntasks = numnode*proc_pr_node
  command = 'sbatch %s --ntasks=%d --ntasks-per-node=%d --partition=pAll --error=log%04d.e --output=log%04d.o strand/run_strand.sh %s'%(depstring,ntasks,proc_pr_node,numnode,numnode,id)
  print(command)
  err,out = commands.getstatusoutput(command)
  depstring = ' --dependency=afterok:%s'%out.split()[-1]



