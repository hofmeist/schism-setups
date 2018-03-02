#!/bin/bash

#SBATCH --job-name=plotnwshelf     # Specify job name
#SBATCH --comment="SCHISM plotting"
#SBATCH --partition=compute   # Specify partition name
#SBATCH --ntasks=10
#SBATCH --ntasks-per-node=10
#SBATCH --time=01:00:00        # Set a limit on the total run time
#SBATCH --wait-all-nodes=1     # start job, when all nodes are available
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=richard.hofmeister@hzg.de  # Set your e−mail address
#SBATCH --account=gg0877       # Charge resources on this project account
#SBATCH --output=log_plotnwshelf.o    # File name for standard output
#SBATCH --error=log_plotnwshelf.e     # File name for standard error output

module load python/2.7-ve0

id=nwshelf$1
yyyymm=$2

wpath=/work/gg0877/hofmeist/nwshelf/$id/
cd $wpath

ii="1"
ii=$(python $HOME/schism/setups/nwshelf/mistral/get_ifiles.py $yyyymm 2012-01)

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_no3 -vrange=0,20 -title nitrate -units "mmolN/m^3" -scalefactor 0.0126 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_nh4 -vrange=0,20 -title ammonium -units "mmolN/m^3" -scalefactor 0.0126 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_pho -vrange=0,2 -title phosphate -units "mmolP/m^3" -scalefactor 0.000788 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_dia -vrange=0,800 -title diatoms -units "mgC/m^3" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_fla -vrange=0,800 -title flagellates -units "mgC/m^3" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_dom -vrange=0,800 -title DOM -units "mgC/m^3" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_det -vrange=0,300 -title detritus -units "mgC/m^3" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc hzg_ecosmo_oxy -vrange=-100,250 -title oxygen -units "mmolO2/m^3" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc temp -vrange=3,18 -title temperature -units "degC" -scalefactor 1.0 &

python ~/schism/setups/nwshelf/plot/plot_schout_bott_surf.py $yyyymm/schout_$ii.nc salt -vrange=8,30 -title salinity -units "psu" -scalefactor 1.0 &

wait

