#!/bin/bash

#SBATCH --job-name=extractecosmo     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=6
#SBATCH --ntasks-per-node=6
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_schoutextract.o    # File name for standard output
#SBATCH --error=log_schoutextract.e     # File name for standard error output
module load nco

rundir=$1
stationlist=$2

cd $rundir

while read name lon lat idx
do

  echo "  process station $name"
  mkdir -p stations/${name}
  files=`ls ????-??/schout_*.nc`

  i=0
  for file in $files ; do
    yyyymm=${file:0:7}
  #ncks -d nSCHISM_hgrid_node,$idx,$idx -v $var,depth,node_bottom_index ${file} ${file}${name}.nc
    ncks -O -d nSCHISM_hgrid_node,$idx,$idx ${file} stations/${name}/${name}_${yyyymm}.nc &
    ((i++))
    if [ $i -eq 6 ] ; then
      wait
      i=0
    fi
  done
  wait
  nfiles=`ls stations/${name}/*.nc`
  ncrcat -O $nfiles stations/${name}.nc
done < $stationlist


