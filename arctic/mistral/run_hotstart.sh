#!/bin/bash

#SBATCH --job-name=arcticschism     # Specify job name
#SBATCH --comment="SCHISM compiled with intel16 and intelmpi"
#SBATCH --partition=compute2    # Specify partition name
### --ntasks=192
#SBATCH --ntasks=36
#SBATCH --ntasks-per-node=36
#SBATCH --time=01:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log.o    # File name for standard output
#SBATCH --error=log.e     # File name for standard error output


## use Intel MPI
module load intel/17.0.1
module load intelmpi/5.1.3.223
export I_MPI_PMI_LIBRARY=/use/lib64/libmpi.so
module load python/2.7-ve0

id="arctic$1"
currmonth=$2
initmonth='2012-01'

outpath=/scratch/g/g260078/schism-results/$id/$currmonth
mkdir -p $outpath
rm -rf $outpath/*
mkdir -p $outpath/outputs
rm -f outputs
ln -sf $outpath/outputs outputs

# wait some time to have the files on the nodes

# set runtime and get prevyear
timestep=240.
nspool=15
prevmonth=$(python ~/schism/setups/nwshelf/mistral/get_prevmonth.py $currmonth)
rnday=$(python ~/schism/setups/nwshelf/mistral/get_rnday.py $currmonth $initmonth)
#ihfskip=360 # this is for daily files
ihfskip=$(python ~/schism/setups/nwshelf/mistral/get_ihfskip.py $currmonth $timestep $initmonth)

# run for 1 day only
rnday=1
ihfskip=360

cp param.default param.in
sed -i -- "s/MY_RNDAY/$rnday/g" param.in
sed -i -- "s/MY_IHFSKIP/$ihfskip/g" param.in
sed -i -- "s/MY_NSPOOL/$nspool/g" param.in
sed -i -- "s/MY_HOTOUT_WRITE/$ihfskip/g" param.in
sed -i -- "s/MY_DT/$timestep/g" param.in

# run the model
# --distribution=block:cyclic bind tasks to physical cores
rm -f hotstart.nc
if [ "$currmonth" == "$initmonth" ] ; then
  ln -sf /work/gg0877/hofmeist/arctic/input/hotstart_january_woa_tweak.nc hotstart.nc
  # use ramps here
  sed -i -- 's/MY_NRAMP_SS/1/g' param.in
  sed -i -- 's/MY_NRAMPWIND/1/g' param.in
  sed -i -- 's/MY_NRAMPBC/1/g' param.in
  sed -i -- 's/MY_NRAMP_/1/g' param.in
  sed -i -- 's/MY_ICELEV/0/g' param.in
#  sed -i -- 's/MY_ICELEV/1/g' param.in
#  sed -i -- 's/MY_NRAMPBC/0/g' param.in
#  sed -i -- 's/MY_NRAMP_/0/g' param.in
  sed -i -- 's/MY_IHOT/0/g' param.in
else
  ln -sf /scratch/g/g260078/schism-results/$id/$prevmonth/outputs/hotstart.nc hotstart.nc
  for i in {1..9} ; do
    touch outputs/staout_${i}
  done
  # disable ramps here
  sed -i -- 's/MY_NRAMP_SS/0/g' param.in
  sed -i -- 's/MY_NRAMPWIND/0/g' param.in
  sed -i -- 's/MY_NRAMPBC/0/g' param.in
  sed -i -- 's/MY_NRAMP_/0/g' param.in
  sed -i -- 's/MY_ICELEV/0/g' param.in
  sed -i -- 's/MY_IHOT/2/g' param.in
fi

# copy parameter namelists
cp param.in $outpath
cp bctides.in $outpath
cp vgrid.in $outpath
cp fabm.nml $outpath

srun -l --propagate=STACK --cpu_bind=verbose,cores --distribution=block:cyclic ~/schism/svn-code/trunk/build/bin/pschism

# move log files
mv fort.* mirror.out $outpath

# wait until all nodes/file-actions are settled
wait


