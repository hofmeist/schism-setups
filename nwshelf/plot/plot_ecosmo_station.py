from pylab import *
import netCDF4
import sys,os

if len(sys.argv)<2:
  print("usage: plot_ecosmo_station.py station.nc")
  sys.exit()
else:
  ncfile=sys.argv[1]

names={}
names['no3']='fab_1'
names['nh4']='fab_2'
names['pho']='fab_3'
names['sil']='fab_4'
names['oxy']='fab_5'
names['dia']='fab_6'
names['fla']='fab_7'
names['bg']='fab_8'
names['mesozoo']='fab_9'
names['microzoo']='fab_10'
names['dom']='fab_12'
names['det']='fab_11'

diag=False
label_days=True

nc = netCDF4.Dataset(ncfile)
ncv = nc.variables

days = ncv['time'][:]/86400.
years = 2003 + days/365.

no3 = ncv[names['no3']][:,-1].squeeze()
nh4 = ncv[names['nh4']][:,-1].squeeze()
pho = ncv[names['pho']][:,-1].squeeze()
sil = ncv[names['sil']][:,-1].squeeze()

 
dia = ncv[names['dia']][:,-1].squeeze()
fla = ncv[names['fla']][:,-1].squeeze()
bg = ncv[names['bg']][:,-1].squeeze()

det = ncv[names['det']][:,-1].squeeze()
dom = ncv[names['dom']][:,-1].squeeze()

microzoo = ncv[names['microzoo']][:,-1].squeeze()
mesozoo = ncv[names['mesozoo']][:,-1].squeeze()

bottom_pool=False
if bottom_pool:
  sed1 = ncv['hzg_ecosmo_sed1'][:].squeeze()
  sed2 = ncv['hzg_ecosmo_sed2'][:].squeeze()
  sed3 = ncv['hzg_ecosmo_sed3'][:].squeeze()

if diag:
  h = ncv['h'][:]
  pp = ncv['hzg_ecosmo_primprod'][:]
  sp = ncv['hzg_ecosmo_secprod'][:]
  pdays = arange(3.5,days.max(),7)
  primprod = zeros((len(pdays),))
  secprod = zeros((len(pdays),))
  # time filter:
  for i,pday in enumerate(pdays):
    idx = where(abs(days-pday)<3.5)
    inum = len(idx[0])
    primprod[i] = sum(h[idx]*pp[idx])*86400.*365./1000./inum
    secprod[i] = sum(h[idx]*sp[idx])*86400.*365./1000./inum

figure(figsize=(10,16))

if label_days:
  xlabelstr='days'
else:
  days = years
  pdays = 1958 + pdays/365.
  xlabelstr='years'

subplot(411)

plot(days,no3,'-',label='no3')
plot(days,nh4,'-',label='nh4')
plot(days,pho,'-',label='pho')
plot(days,sil,'-',label='sil')
xlabel(xlabelstr)
ylabel(u'[mgC/m\u00b3]')
legend(frameon=False)


subplot(414)
plot(days,det,'-',label='det')
plot(days,dom,'-',label='dom')
xlabel(xlabelstr)
ylabel(u'[mgC/m\u00b3]')
legend(frameon=False)


subplot(412)

plot(days,dia,'-',label='dia')
plot(days,fla,'-',label='fla')
plot(days,bg,'-',label='bg')
xlabel(xlabelstr)
ylabel(u'[mgC/m\u00b3]')
legend(frameon=False)


subplot(413)

plot(days,microzoo,'-',label='microzoo')
plot(days,mesozoo,'-',label='mesozoo')
xlabel(xlabelstr)
ylabel(u'[mgC/m\u00b3]')
legend(frameon=False)

if diag:
  subplot(514)

  lw=1.5
  plot(pdays,primprod,'-',lw=lw,label='prim. production')
  plot(pdays,secprod,'-',lw=lw,label='sec. production')
  legend(frameon=False)
  ylabel(u'[gC/m\u00b2/y]')

if bottom_pool:
  subplot(515)

  plot(days,sed1/1000.,'-',label='sed carbon')
  plot(days,sed2/1000.,'-',label='sed opal')
  plot(days,sed3/1000.,'-',label='ads. po4')
  xlabel(xlabelstr)
  ylabel(u'[gC/m\u00b2]')
  legend(frameon=False)

savefig(ncfile[:-3]+'pdf')
show()
