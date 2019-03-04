from pylab import *
import numpy as n
import os
import netCDF4
from netcdftime import utime

try:
  import pytides
  use_pytides=True
except:
  use_pytides=False

try:
  import ttide as tt
  use_ttide=True
  use_pytides=False
except:
  use_ttide=False

def get_stations(fname='stations.dat'):
  coords = {}
  name = {}
  schoutidx = {}
  f = open(fname)
  f.readline() # header
  for i,line in enumerate(f.readlines()):
    dat=line.split()
    name[dat[0]] = i
    coords[dat[0]] = (float(dat[1]),float(dat[2]))
    schoutidx[dat[0]] = int(dat[4])
  return name,coords,schoutidx

def read_staout_1(fname='staout_1'):
  a=n.loadtxt(fname)
  tnum,snum = a.shape
  time = a[:,0].squeeze()
  elev = {}
  for i in range(snum-1):
    elev[i] = a[:,i+1].squeeze()
  return time,elev

def read_schout(fname,schoutidx):
  nc = netCDF4.Dataset(fname)
  ncv = nc.variables
  elev = {}
  time = ncv['time'][:]
  for name in schoutidx:
    elev[name] = ncv['elev'][:,schoutidx[name]].squeeze()
  return time,elev

stations=['Andenes','Honningvag','NyAlesund','Vardo']

def read_ncdf(ncname,path='/work/gg0877/KST/MiMeMo/tide_gaughes',origin='2012-01-01 00:00:00'):
  nc = netCDF4.Dataset(path+'/'+ncname+'.nc')
  ncv = nc.variables
  ot = utime('seconds since '+origin)
  ut = utime(ncv['time'].units)
  time = ot.date2num(ut.num2date(ncv['time'][:]))
  #print(ncv.keys())
  scale = {'cm':100.,'m':1.0,'millimeters':1000.,'mm':1000.}

  if 'elev' in ncv:
    if 'units' in ncv['elev'].ncattrs():
      scale_factor = scale[ncv['elev'].units]
    else:
      if ncv['elev'][:].std()>100.:
        scale_factor=1000.
      elif ncv['elev'][:].std()>10.:
        scale_factor=100.
      else:
        scale_factor=1.0
    elev = ncv['elev'][:].squeeze()/scale_factor
  elif 'sea_surface_height_above_reference_level' in ncv:
    if 'units' in ncv['sea_surface_height_above_reference_level'].ncattrs():
      scale_factor = scale[ncv['sea_surface_height_above_reference_level'].units]
    else:
      scale_factor = 1000.
    elev = ncv['sea_surface_height_above_reference_level'][:].squeeze()/scale_factor
  elif 'sea_level' in ncv:
    if 'units' in ncv['sea_level'].ncattrs():
      scale_factor = scale[ncv['sea_level'].units]
    else:
      scale_factor = 1000.
    elev = ncv['sea_level'][:].squeeze()/scale_factor
  nc.close()
  return time,elev

if __name__=='__main__':
  idx,coords,schoutidx = get_stations(os.environ['HOME']+'/schism/setups/arctic/stations.dat')
  import sys
  if len(sys.argv)>1:
    staoutfile=sys.argv[1]
  else:
    staoutfile='/work/gg0877/hofmeist/nwshelf/nwshelf068/2012-01/staout_1'
    staoutfile='/work/gg0877/hofmeist/arctic/arctic007/2012-02/schout_2.nc'
  time,elevs = read_schout(staoutfile,schoutidx)

  create_tex=True

  days = time/86400.0
  hours = time/3600.
  nmodeldt = 1.0
  nhours = arange(hours[0],hours[-1]+0.5,nmodeldt)
  modeldt = time[1]-time[0]/3600.0

  for name in stations:
    nctime,ncelev = read_ncdf(name,path='/work/gg0877/KST/MiMeMo/tide_gaughes')
    ncdays = nctime/86400.
    obsdt = (ncdays[1]-ncdays[0])*24.
    
    if use_pytides:
      print('%s'%name)
      import pytides.constituent as pcon
      cons = [pcon._M2,pcon._M4,pcon._S2]
      ostart,ostop = abs(ncdays-days[0]).argmin(),abs(ncdays-days[-1]).argmin()
      obs_tide=pytides.tide.Tide.decompose(ncelev[ostart:ostop]-ncelev[ostart-ostop].mean(),list([datetime.datetime(2012,1,1,0,0,0)+datetime.timedelta(day) for day in ncdays[ostart:ostop]]),constituents=cons)
      for c in obs_tide.model:
      #  if c['constituent'].name in ['M2','M4','S2']:
          print(' obs %s: %0.2f m'%(c['constituent'].name,c[1]))
      mod_tide=pytides.tide.Tide.decompose(elevs[name]-elevs[name].mean(),list([datetime.datetime(2012,1,1,0,0,0)+datetime.timedelta(day) for day in days]),constituents=cons)
      for c in mod_tide.model:
      #  if c['constituent'].name in ['M2','M4','S2']:
          print(' model %s: %0.2f m'%(c['constituent'].name,c[1]))

    if use_ttide:
      print('%s'%name)
      ostart,ostop = abs(ncdays-days[0]).argmin(),abs(ncdays-days[-1]).argmin()
      try:
        obs_tide = tt.t_tide(ncelev[ostart:ostop],dt=obsdt,out_style=None)
        e = interp(nhours,hours,elevs[name])
        mod_tide = tt.t_tide(e,dt=nmodeldt,out_style=None)
        m2idx = list(mod_tide['nameu']).index(b'M2  ')
        m4idx = list(mod_tide['nameu']).index(b'M4  ')
        s2idx = list(mod_tide['nameu']).index(b'S2  ')
        modtext='modelled M2: %0.3f, S2: %0.3f'%(mod_tide['tidecon'][m2idx][0],mod_tide['tidecon'][s2idx][0])
        obstext='observed M2: %0.3f, S2: %0.3f'%(obs_tide['tidecon'][m2idx][0],obs_tide['tidecon'][s2idx][0])
        print(modtext)
        print(obstext)
      except:
        modtext='';obstext=''
    else:
      modtext='';obstext=''

    fig = figure(figsize=(20,6))
    fig.subplots_adjust(top=0.85)
    plot(ncdays,ncelev-ncelev.mean(),'b-')
    plot(days,elevs[name]-elevs[name].mean(),'k-')
    xlim(days.min(),days.max())
    xlabel('days')
    ylabel('ssh [m]')
    title(name+'\n%s\n%s'%(modtext,obstext))
    savefig(name+'_ssh.pdf')
    close()

  if create_tex:
    # dump tex file
    texdir='stationstex'
    if os.path.isdir(texdir):
      os.rmdir(texdir)
    if not(os.path.isfile('map.pdf')):
      os.system('cp /work/gg0877/KST/MiMeMo/tide_gaughes/tide_gaughe_locations.pdf map.pdf')
    os.mkdir(texdir)
    f = open(os.path.join(texdir,'all_stations.tex'),'w')
    f.write(r"""\documentclass{article}
\usepackage{graphicx}
\begin{document}

\hspace*{-4cm}
\includegraphics[width=18cm]{../map.pdf}
\\
\\
""")
    for station in stations:
      f.write('\hspace*{-4cm}\n\includegraphics[width=18cm]{../%s_ssh.pdf}\n'%station)

    f.write(r"""
\end{document}
""")
    f.close()

    os.system('cd %s; pdflatex all_stations.tex;cp all_stations.pdf ..'%texdir)
    try:
      os.rmdir(texdir)   
    except:
      import shutil
      shutil.rmtree(texdir)
