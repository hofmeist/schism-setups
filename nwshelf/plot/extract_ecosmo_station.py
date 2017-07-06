import sys,os

f = open(sys.argv[1])
names = sys.argv[2].split(',')
print(names)

for line in f.readlines():
  name,lon,lat,idx = line.split()
  if name in names:
    print('  %s'%name)
    vars = ['salt','temp']
    vars.extend(['fab_%d'%n for n in range(1,14)])
    for var in vars:
      print('    %s'%var)
      print('./scripts/extract_station.sh %s %s %s'%(idx,name,var))
      os.system('~/schism/setups/nwshelf/scripts/extract_station.sh %s %s %s'%(idx,name,var))



