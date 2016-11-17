#!/bin/bash

#SBATCH --job-name=mergeschism     # Specify job name
#SBATCH --comment="SCHISM plotting"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_plotall.o    # File name for standard output
#SBATCH --error=log_plotall.e     # File name for standard error output

module load python/2.7-ve0
id=$1

outpath=/work/gg0877/hofmeist/cb/$1
cd $outpath
plotdir=$HOME/schism/setups/coastalbenchmark/plot

# plot surface salinity
python $plotdir/plot_surface.py 30_salt.nc salt

# plot transects
python $plotdir/plot_transect.py 30_salt.nc salt 0.0
python $plotdir/plot_transect.py 30_temp.nc temp 0.0
python $plotdir/plot_transect.py 30_hvel.nc hvel_v 0.0
python $plotdir/plot_transect.py 30_tdff.nc tdff 0.0

python $plotdir/plot_transect.py 30_salt.nc salt 10000.0 27.0,30.0
python $plotdir/plot_transect.py 30_salt.nc salt 30000.0 27.0,30.0

wait

