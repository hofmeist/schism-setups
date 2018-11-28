import sys
from datetime import datetime,timedelta

year,month = [int(el) for el in sys.argv[1].split('-')]
if len(sys.argv)>2:
  timestep = int(sys.argv[2])
else:
  timestep = 240
if len(sys.argv)>3:
  oyear,omonth = [int(el) for el in sys.argv[3].split('-')]
else:
  oyear=year
  omonth=month

if month==12:
  nyear=year+1
  nmonth=1
else:
  nyear=year
  nmonth=month+1

dt = datetime(nyear,nmonth,1,0,0,0)-datetime(oyear,omonth,1,0,0,0)
print('%d' % (int(int(dt.days)*86400/timestep)))
