#!/bin/bash
module load nco

rundir=$1
idx=$2
name=$3


cd $rundir
mkdir -p stations/${name}
files=`ls ????-??/schout_*.nc`


for file in $files ; do
  yyyymm=${file:0:7}
  #ncks -d nSCHISM_hgrid_node,$idx,$idx -v $var,depth,node_bottom_index ${file} ${file}${name}.nc
  ncks -O -d nSCHISM_hgrid_node,$idx,$idx ${file} stations/${name}/${name}_${yyyymm}.nc
done

nfiles=`ls stations/${name}/*.nc`
ncrcat -O $nfiles stations/${name}.nc

