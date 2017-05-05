f = open('stations.dat')
o = open('station.in','w')
o.write('1 0 0 0 0 0 0 0 0 !on (1)|off(0) flags for elev, air pressure, windx, windy, T, S, u, v, w\n')

num = 0
ostring = ''
for line in f.readlines():
  data = line.split()
  name = data[0]
  lon = data[1]
  lat = data[2]
  num = num+1
  ostring+='   %d  %s  %s  -1.0\n'%(num,lon,lat)

o.write('%d\n'%num)
o.write(ostring)
o.close()
f.close() 
