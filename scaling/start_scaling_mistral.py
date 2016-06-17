import os
import sys

proc_pr_node = 24
numnodes = [4,8,16,32,64,128,256]
numnodes = [4,8,16,32,64]
numnodes = [4]

for numnode in numnodes:
  os.system('sbatch --ntasks=%d --ntasks-per-node=%d --error=log%04d.e --output=log%04d.o run.sh %d'%(numnode,proc_pr_node,numnode,numnode,numnode))



