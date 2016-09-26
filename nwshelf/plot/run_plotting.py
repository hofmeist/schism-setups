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

outpath=/work/gg0877/hofmeist/$1
cd $outpath

# plot surface elevation
#python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 29_elev.nc elev
python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 30_elev.nc elev
python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py 29_elev.nc elev

# plot initial S,T
python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py 1_salt.nc salt 0
python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py 1_temp.nc temp 0

# plot German Bight salinity
python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py 30_salt.nc

wait

