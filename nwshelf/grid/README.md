python nwshelf2polygon.py
gimp map.png -> save resolution layer
python png2structured.py
gmsh -2 coast.geo
python ../../scripts/msh2gr3.py coast.msh
python ../../scripts/bathymetry_to_hgrid.py # creates xyd_bathymetry.pickle
python ../../scripts/xyd_to_hgrid.py
python ../../scripts/calculate_rotation.py
cp hgrid_new.ll ../hgrid.gr3
num=$((`wc -l < hgrid_new.ll`+1))
tail -n+$num hgrid.gr3 >> ../hgrid.gr3
cp hgrid_new.ll ../hgrid.ll
