#!/bin/bash

#SBATCH --job-name=plotschism     # Specify job name
#SBATCH --comment="ECOSMO plotting"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_plotecosmo$1.o    # File name for standard output
#SBATCH --error=log_plotecosmo$1.e     # File name for standard error output

module load python/2.7-ve0
id=$1
yyyymm=$2
ifiles=($(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01))

outpath=/work/gg0877/hofmeist/$1
cd $outpath

i=0
for ifile in ${ifiles[@]} ; do
  # plot surface elevation
  #python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 29_elev.nc elev
  #python $HOME/schism/setups/nwshelf/plot/plot_surface_mistral.py 30_elev.nc elev
  #python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_elev.nc elev &
#  ((i++))
  # plot first timestep each day for salt & temp
  #python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_salt.nc salt -tidx 0 &
#  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_salt.nc salt &
#  ((i++))
#  python $HOME/schism/setups/nwshelf/plot/plot_bott_baltic.py $yyyymm/${ifile}_salt.nc salt &
  python $HOME/schism/setups/nwshelf/plot/plot_phytoplankton.py $yyyymm/${ifile} -vrange 0,800 &
  ((i++))
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_fab_1.nc fab_1 -vrange 0,2000 -title nitrate -units "mgC/m^3" &
  ((i++))
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_fab_11.nc fab_11 -vrange 0,800 -title detritus -units "mgC/m^3" &
  ((i++))
  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_fab_3.nc fab_3 -vrange 0,2000 -title phosphate -units "mgC/m^3" &
  ((i++))
#  python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifile}_temp.nc temp &
#  ((i++))
  if [ "$i" == "36" ] ; then
    wait
    i=0
  fi
done

# plot initial S,T
#python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifiles[0]}_salt.nc salt -tidx 0 &
#python $HOME/schism/setups/nwshelf/plot/plot_bott_surf.py $yyyymm/${ifiles[0]}_temp.nc temp -tidx 0 &

# plot German Bight salinity for last day in month
#python $HOME/schism/setups/nwshelf/plot/plot_german_bight.py $yyyymm/${ifile}_salt.nc salt &

wait

