#!/bin/bash

#SBATCH --job-name=nwschism     # Specify job name
#SBATCH --partition=pCluster    # Specify partition name
#SBATCH --ntasks=960
#SBATCH --ntasks-per-node=48
#SBATCH --time=04:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --account=KST       # Charge resources on this project account
#SBATCH --output=log.o    # File name for standard output
#SBATCH --error=log.e     # File name for standard error output

module load compilers/intel
module load intelmpi
/project/opt/intel/bin/compilervars.sh intel64

id="nwshelf$1"
currmonth=$2
initmonth='2012-01'

outpath=/gpfs/work/$USER/schism-results/$id/$currmonth
mkdir -p $outpath
rm -rf $outpath/*
mkdir -p $outpath/outputs
rm -f outputs
ln -sf $outpath/outputs outputs

# wait some time to have the files on the nodes

# set runtime and get prevyear
timestep=240
nspool=360
prevmonth=$(python ~/schism/setups/nwshelf/mistral/get_prevmonth.py $currmonth)
rnday=$(python ~/schism/setups/nwshelf/mistral/get_rnday.py $currmonth $initmonth)
#ihfskip=360 # this is for daily files
ihfskip=$(python ~/schism/setups/nwshelf/mistral/get_ihfskip.py $currmonth $timestep $initmonth)
cp param.nml.default param.nml
sed -i -- "s/MY_RNDAY/$rnday/g" param.nml
sed -i -- "s/MY_IHFSKIP/$ihfskip/g" param.nml
sed -i -- "s/MY_NSPOOL/$nspool/g" param.nml
sed -i -- "s/MY_HOTOUT_WRITE/$ihfskip/g" param.nml
sed -i -- "s/MY_DT/$timestep/g" param.nml

# run the model
# --distribution=block:cyclic bind tasks to physical cores
rm -f hotstart.nc
if [ "$currmonth" == "$initmonth" ] ; then
  ln -sf /gpfs/work/$USER/nwshelf/input/hotstart_january.nc hotstart.nc
  # use ramps here
  sed -i -- 's/MY_NRAMP_SS/1/g' param.nml
  sed -i -- 's/MY_NRAMPWIND/1/g' param.nml
  sed -i -- 's/MY_NRAMPBC/1/g' param.nml
  sed -i -- 's/MY_NRAMP_/1/g' param.nml
  sed -i -- 's/MY_ICELEV/0/g' param.nml
#  sed -i -- 's/MY_ICELEV/1/g' param.nml
#  sed -i -- 's/MY_NRAMPBC/0/g' param.nml
#  sed -i -- 's/MY_NRAMP_/0/g' param.nml
  sed -i -- 's/MY_IHOT/1/g' param.nml
else
  ln -sf /gpfs/work/$USER/schism-results/$id/$prevmonth/outputs/hotstart.nc hotstart.nc
  for i in {1..9} ; do
    cp /gpfs/work/$USER/schism-results/$id/$prevmonth/outputs/staout_${i} outputs/staout_${i}
  done
  # disable ramps here
  sed -i -- 's/MY_NRAMP_SS/0/g' param.nml
  sed -i -- 's/MY_NRAMPWIND/0/g' param.nml
  sed -i -- 's/MY_NRAMPBC/0/g' param.nml
  sed -i -- 's/MY_NRAMP_/0/g' param.nml
  sed -i -- 's/MY_ICELEV/0/g' param.nml
  sed -i -- 's/MY_IHOT/2/g' param.nml
fi

# copy parameter namelists
cp param.nml $outpath
cp bctides.in $outpath
cp vgrid.in $outpath
[[ -e fabm.nml ]] && cp fabm.nml $outpath

mpirun  ~/schism/build/bin/pschism

mv fort.* mirror.out $outpath

# wait until all nodes/file-actions are settled
wait


