#!/bin/bash

#SBATCH --job-name=nwschism     # Specify job name
#SBATCH --comment="SCHISM compiled with intel16 and intelmpi"
#SBATCH --partition=compute2    # Specify partition name
### --ntasks=192
#SBATCH --ntasks=1080
#SBATCH --ntasks-per-node=36
#SBATCH --time=00:60:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log.o    # File name for standard output
#SBATCH --error=log.e     # File name for standard error output

# 108 cpus -> 12000 s in 60 s -> 1 month in 3.6 h
# 324 cpus -> 
# 1080 cpus -> 120000 s in 100 s -> 1 month in 36 min

# Modified Case1: Run MPI parallel program using mvapich2
#module load mvapich2/2.1-intel14
#export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
#export I_MPI_FABRICS=shm:dapl
#export I_MPI_FALLBACK=0
#export I_MPI_DAPL_UD=enable

## use Intel MPI
module load intelmpi
export I_MPI_PMI_LIBRARY=/use/lib64/libmpi.so

id="nwshelf$1"

outpath=/scratch/g/g260078/schism-results/$id
mkdir -p $outpath
rm -rf $outpath/*
mkdir -p $outpath/outputs
rm -f outputs
ln -sf $outpath/outputs outputs

# copy parameter namelists
cp param.in $outpath
cp bctides.in $outpath
cp vgrid.in $outpath

# wait some time to have the files on the nodes
#sleep 5

# run the model
# --distribution=block:cyclic bind tasks to physical cores
srun -l --cpu_bind=verbose,cores --distribution=block:cyclic ~/schism/v5.3/newbuild/bin/pschism

# move log files
mv log.e log.o fort.* $outpath

# wait until all nodes/file-actions are settled
wait
#sleep 5

