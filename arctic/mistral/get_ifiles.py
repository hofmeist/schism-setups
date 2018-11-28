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

# daily output:
dtend = datetime(nyear,nmonth,1,0,0,0)-datetime(oyear,omonth,1,0,0,0)
dtstart = datetime(year,month,1,0,0,0)-datetime(oyear,omonth,1,0,0,0)
istart = dtstart.days+1
iend = dtend.days+1
# monthly output:
dtstart = (year-oyear)*12 - omonth + month
istart = dtstart+1
iend = dtstart+2


s = ''
for ifile in range(istart,iend):
  s = s+' %s'%str(ifile)
print(s[1:])
