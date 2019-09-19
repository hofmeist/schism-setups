## station Barents Sea:
#lon=45.0
#lat=73.0

python scripts/find_station_in_output.py /work/gg0877/hofmeist/arctic/arcticice04/2016-01/schout_49.nc 45.0,73.0
 Index for lon=45.00,lat=73.00 is 32967
python scripts/extract_station_schout.sh /work/gg0877/hofmeist/arctic/arcticice04 32967 BarentsSea
