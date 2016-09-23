#!/bin/bash

#SBATCH --job-name=plotschism     # Specify job name
#SBATCH --comment="SCHISM plotting"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:60:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_plotgb.o    # File name for standard output
#SBATCH --error=log_plotgb.e     # File name for standard error output

module load python/2.7-ve0
id=$1

outpath=/work/gg0877/hofmeist/$1
cd $outpath

#python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py 29_salt.nc
#python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py 30_salt.nc
python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py 29_elev.nc elev
#python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py 30_elev.nc elev

wait

