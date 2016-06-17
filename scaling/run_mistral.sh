#!/bin/bash

#SBATCH --job-name=hschism     # Specify job name
#SBATCH --comment="SCHISM compiled with intel16 and intelmpi"
#SBATCH --partition=compute    # Specify partition name
#SBATCH --ntasks=96
#SBATCH --ntasks-per-node=24
#SBATCH --time=00:10:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=run_parallel.o%j    # File name for standard output
#SBATCH --error=run_parallel.e%j     # File name for standard error output


# Modified Case1: Run MPI parallel program using mvapich2
#module load mvapich2/2.1-intel14
#export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
#export I_MPI_FABRICS=shm:dapl
#export I_MPI_FALLBACK=0
#export I_MPI_DAPL_UD=enable

## use Intel MPI
module load intelmpi
export I_MPI_PMI_LIBRARY=/use/lib64/libmpi.so

id="$1"

outpath=/scratch/g/g260078/schism-results/$id
mkdir -p $outpath
rm -rf $outpath/*

# copy parameter namelists
cp param.in bctides.in vgrid.in $outdir

# wait some time to have the files on the nodes
#sleep 5

# run the model
# --distribution=block:cyclic bind tasks to physical cores
srun -l --cpu_bind=verbose,cores --distribution=block:cyclic ~/schism/v5.3/build/bin/pschism

# move log files
mv outputs/* log*.e log*.o $outpath

# wait until all nodes/file-actions are settled
wait
#sleep 5

