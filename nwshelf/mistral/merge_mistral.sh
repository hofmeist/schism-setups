#!/bin/bash

#SBATCH --job-name=mergeschism     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=8
#SBATCH --time=02:30:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_newmerge.o    # File name for standard output
#SBATCH --error=log_newmerge.e     # File name for standard error output

id=nwshelf$1
yyyymm=$2
module load python/2.7-ve0

outpath=/scratch/g/g260078/schism-results/$id/$yyyymm
cd $outpath/outputs

iis=$(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01)
files="elev.61 srad.61 radu.61 radd.61 salt.63 temp.63 zcor.63 tdff.63"

for file in $files ; do
  for ii in $iis ; do
    $HOME/schism/schism5.3/build/bin/combine_output9 -b $ii -e $ii -n 1 -f $file &
  done
done
wait

# move results
echo "  move results..."
$HOME/schism/setups/nwshelf/mistral/results_to_work.scr $id/$yyyymm


