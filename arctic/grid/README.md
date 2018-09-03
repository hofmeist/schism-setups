python arctic2polygon.py
python xyd_to_structured.py
#gimp map.png, add resolution_grey.png -> save resolution layer
#python png2structured.py
# then add 
# Field[3] = Structured;
# Field[3].FileName = "structured_size.dat";
# Field[3].TextFormat = 1;
# Background Field = 3;

gmsh -2 coast.geo
python ../../scripts/new_msh2gr3.py coast.msh
python ibcao_to_pickle.py # creates xyd_bathymetry.pickle
python ../../scripts/xyd_to_hgrid.py
python ../../scripts/calculate_rotation.py
cp hgrid_new.ll hgrid_new.gr3
num=$((`wc -l < hgrid_new.ll`+1))
tail -n+$num hgrid.gr3 >> hgrid_new.gr3

