#!/bin/bash

#SBATCH --job-name=tideanalysis     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=compute2   # Specify partition name
#SBATCH --ntasks=36
#SBATCH --ntasks-per-node=36
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_ptideanalysis_2012-02.o    # File name for standard output
#SBATCH --error=log_ptideanalysis_2012-02.e     # File name for standard error output

module unload python
module load python

cd /work/gg0877/hofmeist/arctic/arctic007/2012-02

python $HOME/schism/setups/arctic/scripts/do_tideanalysis.py schout_2.nc 36

