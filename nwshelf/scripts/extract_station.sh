#!/bin/bash
module load nco

idx=$1
name=$2
var=$3

cd /work/gg0877/hofmeist/nwshelf/nwshelf069
files=`ls ????-??/*_${var}.nc`
#rm ${name}_????-??.nc


for file in $files ; do
  yyyymm=${file:0:7}
  #ncks -d nSCHISM_hgrid_node,$idx,$idx -v $var,depth,node_bottom_index ${file} ${file}${name}.nc
  ncks -A -d nSCHISM_hgrid_node,$idx,$idx -v $var,depth,node_bottom_index ${file} ${name}_${yyyymm}.nc
done

#nfiles=`ls ${name}_????-??.nc`
#ncrcat -O $nfiles ${name}.nc

