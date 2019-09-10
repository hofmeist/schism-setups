#!/bin/bash

#SBATCH --job-name=mergeschism     # Specify job name
#SBATCH --comment="SCHISM postprocessing"
#SBATCH --partition=shared   # Specify partition name
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=8
#SBATCH --time=06:30:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_merge.o    # File name for standard output
#SBATCH --error=log_merge.e     # File name for standard error output

id=$1
yyyymm=$2
module load python/2.7-ve0

outpath=/scratch/g/g260078/schism-results/$id/$yyyymm
cd $outpath/outputs

iis=$(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01)

for ii in $iis ; do
    $HOME/schism/svn-code/trunk/build/bin/combine_output11 -b $ii -e $ii &
    #$HOME/schism/svn-code/trunk/build/bin/combine_output11 -b $ii -e 31 &
done
wait

# move results
echo "  move results..."
sname=$id/$yyyymm
swd=/work/gg0877/$USER/arctic/$sname
scratchdir=/scratch/g/$USER/schism-results/$sname
mkdir -p $swd

cp $scratchdir/outputs/staout* $swd &
cp -L  $scratchdir/{param.in,fabm.nml,ice.nml,gotmturb.nml} $swd &
for ii in $iis ; do
  cp $scratchdir/outputs/schout_${iis}.nc $swd &
done
wait


