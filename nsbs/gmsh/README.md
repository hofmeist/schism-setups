python nsbs2polygon.py
python ~/SCHISM/setups/scripts/bathymetry_to_xyd.py small_nsbs_bathymetry.nc
gmsh -2 coast.geo # to create coast.msh
python ~/SCHISM/setups/scripts/msh2gr3.py
python ~/SCHISM/setups/scripts/xyd_and_hgrid_to_backgroundfile.py

# now change coast.geo such, that the background field is used
# and call gmsh again

gmsh -2 coast.geo
python ~/SCHISM/setups/scripts/msh2gr3.py
python ~/SCHISM/setups/scripts/xyd_to_hgrid.py

# ready to run?
