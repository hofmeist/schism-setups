import netCDF4
import sys

const = {'q2':0.000005,'xl':0.1,'dfv':0.0001,'dfh':0.0001,'dfq1':0.0001,'dfq2':0.0001}

nc = netCDF4.Dataset(sys.argv[1],'a')

for vname in const:
  try:
    v = nc.variables[vname]
    v[:] = const[vname]
    nc.sync()
  except:
    pass

nc.close()
