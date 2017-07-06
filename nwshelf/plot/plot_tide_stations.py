from pylab import *
import numpy as n
import os
import netCDF4
from netcdftime import utime

def get_stations(fname='stations.dat'):
  coords = {}
  name = {}
  f = open(fname)
  for i,line in enumerate(f.readlines()):
    dat=line.split()
    name[dat[0]] = i
    coords[dat[0]] = (float(dat[1]),float(dat[2]))
  return name,coords

def read_staout_1(fname='staout_1'):
  a=n.loadtxt(fname)
  tnum,snum = a.shape
  time = a[:,0].squeeze()
  elev = {}
  for i in range(snum-1):
    elev[i] = a[:,i+1].squeeze()
  return time,elev

def read_ncdf(name,path='/work/gg0877/KST/tide_gaughes/ncdf',origin='2012-01-01 00:00:00'):
  ncname = '_'.join(word[0].upper()+word[1:] for word in name.split('_'))
  if path[-6:]=='hawaii':
    nc = netCDF4.MFDataset(path+'/'+ncname+'*.nc')
  else:
    nc = netCDF4.Dataset(path+'/'+ncname+'.nc')
  ncv = nc.variables
  ot = utime('seconds since '+origin)
  ut = utime(ncv['time'].units)
  time = ot.date2num(ut.num2date(ncv['time'][:]))
  print(ncv.keys())
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
  nc.close()
  return time,elev

if __name__=='__main__':
  time,elevs = read_staout_1('/work/gg0877/hofmeist/nwshelf/nwshelf068/2012-01/staout_1')
  idx,coords = get_stations(os.environ['HOME']+'/schism/setups/nwshelf/stations.dat')
  days = time/86400.0

  #name = 'stMary'
  stations=['lerwick','wick','tregde','lowestoft','stMary','bergen','aberdeen','newlyn','malin_head','castletownsend','brest','cuxhaven','gothenburg','maloy','stockholm']
  for name in stations:
    try:
      nctime,ncelev = read_ncdf(name)
    except:
      nctime,ncelev = read_ncdf(name,path='/work/gg0877/KST/tide_gaughes/uhslc_hawaii')
    ncdays = nctime/86400.

    fig = figure(figsize=(20,6))
    plot(ncdays,ncelev-ncelev.mean(),'b-')
    plot(days,elevs[idx[name]],'k-')
    xlim(days.min(),days.max())
    xlabel('days')
    ylabel('ssh [m]')
    title(name)
    savefig(name+'_ssh.pdf')
    close()

  # dump tex file
  texdir='stationstex'
  if os.path.isdir(texdir):
    os.rmdir(texdir)
  if not(os.path.isfile('map.pdf')):
    os.system('cp /work/gg0877/KST/tide_gaughes/tide_gaughe_locations.pdf map.pdf')
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
  os.rmdir(texdir)   
