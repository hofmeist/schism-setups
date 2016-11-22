import sys

year,month = [int(el) for el in sys.argv[1].split('-')]

if month==1:
  prevyear = year-1
  prevmonth = 12
else:
  prevyear=year
  prevmonth=month-1

print('%04d-%02d'%(prevyear,prevmonth))
