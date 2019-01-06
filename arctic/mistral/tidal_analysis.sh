#!/bin/bash

#SBATCH --job-name=tideanalysis     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=compute2   # Specify partition name
#SBATCH --ntasks=30
#SBATCH --ntasks-per-node=30
#SBATCH --time=00:60:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_ptideanalysis_2012-02.o    # File name for standard output
#SBATCH --error=log_ptideanalysis_2012-02.e     # File name for standard error output

module unload python
module load python

opath=$1
cd $opath

python $HOME/schism/setups/arctic/scripts/do_tideanalysis.py schout_2.nc 30

