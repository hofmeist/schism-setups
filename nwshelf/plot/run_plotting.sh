#!/bin/bash

#SBATCH --job-name=plotschism     # Specify job name
#SBATCH --comment="SCHISM plotting"
#SBATCH --partition=compute2   # Specify partition name
#SBATCH --ntasks=36
#SBATCH --ntasks-per-node=36
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_plotall.o    # File name for standard output
#SBATCH --error=log_plotall.e     # File name for standard error output

module load python/2.7-ve0
id=$1
yyyymm=$2
ifiles=($(python mistral/get_ifiles.py $yyyymm 2012-01))

outpath=/work/gg0877/hofmeist/$1
cd $outpath

i=0
for ifile in ${ifiles[@]} ; do
  # plot surface elevation
  #python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 29_elev.nc elev
  #python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 30_elev.nc elev
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_elev.nc elev &
  ((i++))
  # plot first timestep each day for salt & temp
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_salt.nc salt 0 &
  ((i++))
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_temp.nc temp 0 &
  ((i++))
  if [ "$i" == "36" ] ; then
    wait
    i=0
  fi
done

# plot initial S,T
#python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifiles[0]}_salt.nc salt 0 &
#python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifiles[0]}_temp.nc temp 0 &

# plot German Bight salinity for last day in month
python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py $yyyymm/${ifile}_salt.nc salt &

wait

