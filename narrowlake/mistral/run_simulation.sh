#!/bin/bash

#SBATCH --job-name=narrowlake     # Specify job name
#SBATCH --comment="SCHISM compiled with intel16 and intelmpi"
#SBATCH --partition=compute    # Specify partition name
### --ntasks=192
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=03:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log.o    # File name for standard output
#SBATCH --error=log.e     # File name for standard error output

# Modified Case1: Run MPI parallel program using mvapich2
#module load mvapich2/2.1-intel14
#export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
#export I_MPI_FABRICS=shm:dapl
#export I_MPI_FALLBACK=0
#export I_MPI_DAPL_UD=enable

## use Intel MPI
module load intel/17.0.1
module load intelmpi/5.1.3.223
export I_MPI_PMI_LIBRARY=/use/lib64/libmpi.so
module load python/2.7-ve0

id="nl$1"

outpath=/work/gg0877/hofmeist/narrowlake/$id
mkdir -p $outpath
rm -rf $outpath/*
mkdir -p $outpath/outputs
rm -f outputs
ln -sf $outpath/outputs outputs

# wait some time to have the files on the nodes

# set runtime and get prevyear

# copy parameter namelists
cp param.in $outpath
cp bctides.in $outpath
cp vgrid.in $outpath
cp fabm.nml $outpath

srun -l --propagate=STACK --cpu_bind=verbose,cores --distribution=block:cyclic ~/schism/svn-code/trunk/build/bin/pschism

# move log files
#cp log.e log.o $outpath
mv fort.* mirror.out total_TR.dat $outpath

# wait until all nodes/file-actions are settled
wait

# merge output
cd outputs
~/schism/svn-code/trunk/build/bin/combine_output10 -b 1 -e 1
