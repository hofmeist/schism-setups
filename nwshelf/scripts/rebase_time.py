import netCDF4
import netcdftime
import sys

if len(sys.argv)>2:
  units='seconds since %s 00:00:00'%sys.argv[2]
else:
  print('rebase_time.py ncfile YYYY-MM-DD')
  sys.exit(1)

ut = netcdftime.utime(units)

nc = netCDF4.Dataset(sys.argv[1],'a')
myut = netcdftime.utime(nc.variables['time'].units)

dates = myut.num2date(nc.variables['time'][:])

nc.variables['time'][:] = ut.date2num(dates)
nc.variables['time'].units = units

nc.close()

