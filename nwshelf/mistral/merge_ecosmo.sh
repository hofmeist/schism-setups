#!/bin/bash

#SBATCH --job-name=mergeecosmo     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=13
#SBATCH --ntasks-per-node=13
#SBATCH --time=00:60:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_ecomerge.o    # File name for standard output
#SBATCH --error=log_ecomerge.e     # File name for standard error output

id=nwshelf$1
yyyymm=$2

outpath=/scratch/g/g260078/schism-results/$id/$yyyymm
cd $outpath/outputs

iis="1"
iis=$(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01)
files="elev.61 salt.63 temp.63 zcor.63"
files="fab_1.63 fab_2.63 fab_3.63 fab_4.63 fab_5.63 fab_6.63 fab_7.63 fab_8.63 fab_9.63 fab_10.63 fab_11.63 fab_12.63 fab_13.63"

for ii in $iis ; do
  for file in $files ; do
    $HOME/schism/schism5.3/build/bin/combine_output9 -b $ii -e $ii -n 1 -f $file &
  done
  wait
done

# move results
echo "  move results..."
mkdir -p /work/gg0877/hofmeist/nwshelf/$id/$yyyymm
cp -ua $outpath/outputs/*_fab_*.nc /work/gg0877/hofmeist/nwshelf/$id/$yyyymm
#$HOME/schism/setups/nwshelf/mistral/results_to_work.scr $id/$yyyymm

wait

