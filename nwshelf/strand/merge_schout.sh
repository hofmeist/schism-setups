#!/bin/bash

#SBATCH --job-name=mergeschism     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=pAll   # Specify partition name
#SBATCH --ntasks=12
#SBATCH --ntasks-per-node=12
#SBATCH --time=07:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --account=KST       # Charge resources on this project account
#SBATCH --output=log_schoutmerge.o    # File name for standard output
#SBATCH --error=log_schoutmerge.e     # File name for standard error output

module load compilers/intel
module load intelmpi
/project/opt/intel/bin/compilervars.sh intel64

id=nwshelf$1
yyyymm=$2

outpath=/gpfs/work/$USER/schism-results/$id/$yyyymm
cd $outpath/outputs

iis="1"
iis=$(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01)

$HOME/schism/build/bin/combine_output11 -b $iis -e $iis 

# move results
echo "  move results..."
workdir=/gpfs/work/$USER/nwshelf/$id/$yyyymm
mkdir -p $workdir
cp -ua $outpath/outputs/schout_${iis}.nc $workdir

wait

