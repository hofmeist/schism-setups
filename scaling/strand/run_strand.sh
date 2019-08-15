#!/bin/bash

#SBATCH --job-name=scalingschism     # Specify job name
#SBATCH --ntasks=96
#SBATCH --ntasks-per-node=48
#SBATCH --account=KST
#SBATCH --partition=pCluster
#SBATCH --time=00:32:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your email address
#SBATCH --output=run_parallel.o%j    # File name for standard output
#SBATCH --error=run_parallel.e%j     # File name for standard error output


## use Intel MPI
module load compilers/intel
module load intelmpi

#module load compilers/intel/2019.3.199
#module load intelmpi/2019.3.199

#module load compilers/intel/2018.1.163
#module load intelmpi/2018.1.163

/project/opt/intel/bin/compilervars.sh intel64


id="$1"

outpath=/gpfs/work/hofmeist/schism-results/$id
mkdir -p $outpath
rm -rf $outpath/*
mkdir -p $outpath/outputs
ln -sf $outpath/outputs outputs

# copy parameter namelists
cp param.nml $outpath
cp bctides.in $outpath
cp vgrid.in $outpath

# wait some time to have the files on the nodes
#sleep 5

# run the model
#mpirun ~/schism/build/bin/pschism

srun --mpi=pmi2 --export=LD_LIBRARY_PATH  ~/schism/build/bin/pschism
#srun --mpi=pmi2 --export=LD_LIBRARY_PATH  ~/schism/build2018/bin/pschism
mpirun  ~/schism/build/bin/pschism


# move log files
mv log*.e log*.o fort.* mirror.out $outpath
rm outputs

# wait until all nodes/file-actions are settled
wait
#sleep 5

