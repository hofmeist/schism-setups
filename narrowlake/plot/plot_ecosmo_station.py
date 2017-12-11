from pylab import *
import netCDF4

nc = netCDF4.Dataset(sys.argv[1])
ncv=nc.variables

idx = int(sys.argv[2])

no3 = ncv['hzg_ecosmo_no3'][:,idx,-1]
dia = ncv['hzg_ecosmo_dia'][:,idx,-1]
fla = ncv['hzg_ecosmo_fla'][:,idx,-1]
temp = ncv['temp'][:,idx,-1]
salt = ncv['salt'][:,idx,-1]
zoo = ncv['hzg_ecosmo_microzoo'][:,idx,-1]+ncv['hzg_ecosmo_mesozoo'][:,idx,-1]
days = ncv['time'][:]/86400.

figure(figsize=(8,14))
lw=2.0

subplot(311)
plot(days,no3.squeeze(),lw=lw,color='r',label='nitrate')
plot(days,dia.squeeze(),lw=lw,color=(0.0,0.5,0.0),label='diatoms')
plot(days,fla.squeeze(),lw=lw,color=(0.0,0.8,0.0),label='flagellates')
plot(days,zoo.squeeze(),lw=lw,color=(0.3,0.3,0.3),label='zooplankton')
legend(frameon=False)
xlabel('days')
ylabel(u'[mgC/m\u00b3]')
subplot(312)
plot(days,temp,lw=lw,color='r',label='temperature')
xlabel('days')
ylabel(u'temperature [\u00b0C]')

subplot(313)
plot(days,salt,lw=lw,color='orange',label='salinity')
xlabel('days')
ylabel(u'salinity [psu]')

savefig('ecosmo_station_node%04d.pdf'%idx)
show()
