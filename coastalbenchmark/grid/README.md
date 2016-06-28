#!/bin/bash

python create_gmsh_input.py
gmsh -2 grid.geo
python ../../scripts/msh2gr3.py grid.msh
python ../../scripts/xyd_to_hgrid.py hgrid.gr3
cp hgrid_new.gr3 ../hgrid.gr3
num=$((`wc -l < hgrid_new.gr3`+1))
tail -n+$num hgrid.gr3 >> ../hgrid.gr3
cd ..
cp hgrid.gr3 hgrid.ll
python scripts/create_ic.py

