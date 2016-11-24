import sys
from datetime import datetime,timedelta

year,month = [int(el) for el in sys.argv[1].split('-')]
if len(sys.argv)>2:
  oyear,omonth = [int(el) for el in sys.argv[2].split('-')]
else:
  oyear=year
  omonth=month

if month==12:
  nyear=year+1
  nmonth=1
else:
  nyear=year
  nmonth=month+1

dtend = datetime(nyear,nmonth,1,0,0,0)-datetime(oyear,omonth,1,0,0,0)
dtstart = datetime(year,month,1,0,0,0)-datetime(oyear,omonth,1,0,0,0)
s = ''
for ifile in range(dtstart.days+1,dtend.days+1):
  s = s+' %s'%str(ifile)
print(s[1:])
