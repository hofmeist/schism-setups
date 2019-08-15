#!/bin/bash

#SBATCH --job-name=hmergeschism     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=pCluster   # Specify partition name
#SBATCH --ntasks=6 
#SBATCH --ntasks-per-node=6
#SBATCH --time=00:60:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --account=KST       # Charge resources on this project account
#SBATCH --output=log_hotstart_merge_g.o    # File name for standard output
#SBATCH --error=log_hotstart_merge_g.e     # File name for standard error output
#SBATCH --share

id=nwshelf$1
mstr=$2
resdir=/gpfs/work/$USER/schism-results/$id/$mstr/

cd $resdir/outputs

# get step number:
days=$(python ~/schism/setups/nwshelf/mistral/get_rnday.py $mstr 2012-01)
iteration=$(python -c "print('%d'%int( ($days*86400./240.) ))")

module load python
# combine hotstart
$HOME/schism/trunk/build/bin/combine_hotstart7 -i $iteration

# rename to avoid it=*
mv hotstart_it*.nc hotstart.nc

swd=/gpfs/work/$USER/nwshelf/$id/$mstr/
mkdir -p $swd
# copy hotstart files to work
cp hotstart.nc $swd
