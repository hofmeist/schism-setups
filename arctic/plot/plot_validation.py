import netCDF4
import sys
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from pylab import *
import pickle,os
from netcdftime import utime
import argparse
import pandas as pd
from datetime import datetime

def replace_superscripts(s):
  r = unicode(s.replace('^3',u'\u00b3'))
  r = unicode(r.replace('^2',u'\u00b2'))
  return r

parser = argparse.ArgumentParser()
parser.add_argument('file', help='dataframe file')
#parser.add_argument('varname',help='variable name')
parser.add_argument('-year', help='year')
parser.add_argument('-vrange', help='values range [-vrange vmin,vmax]')
parser.add_argument('-title', help='title of colorbar')
parser.add_argument('-units', help='unit string')
parser.add_argument('-scalefactor', help='linear scaling factor')
args = parser.parse_args()

if args.year is not None:
  year = int(args.year)
else:
  year = 2013

if 'vrange' is not None:
  try:
    s1,s2 = args.vrange.split(',')
    vmin,vmax = float(s1),float(s2)
    uselim=True
  except:
    uselim=False
else:
  uselim=False

if args.title is not None:
  titlestr=unicode(args.title)
else:
  titlestr=''

if args.units is not None:
  unitsstr=replace_superscripts(args.units)
else:
  unitsstr=''

if args.scalefactor is not None:
  fac = float(args.scalefactor)
else:
  fac=1.0

with open(args.file,'rb') as f:
  df = pickle.load(f)

#lon = df['Londeg']
#lat = df['Latdeg']
#jd = df['jd']
#s_ices = df['salt']
#s_model = df['model_salt']
#t_ices = df['temp']
#t_model = df['model_temp']

if True:

  jdstart = date2num(datetime(year,1,1,0,0,0))
  jdend = date2num(datetime(year+1,1,1,0,0,0))
  thisyear = (df['jd']>=jdstart)&(df['jd']<jdend)

  # set map boundaries
  xl,yl = (-15.0,60.0)
  xu,yu = (100,75.0)

  if os.path.isfile('plotproj.pickle'):
    with open('plotproj.pickle','rb') as f:
      (proj,)=pickle.load(f)
  else:
    if False:
      proj = Basemap(projection='npstere',boundinglat=55.,lon_0=0.0,resolution='i')
    else:
      proj = Basemap(projection='lcc',
                       resolution='i',area_thresh=10.0,
                        llcrnrlon=xl,
                        llcrnrlat=yl,
                        urcrnrlon=xu,
                        urcrnrlat=yu,
                        lat_0=70.0,
                        lon_0=20.0)

    f=open('plotproj.pickle','wb')
    pickle.dump((proj,),f)
    f.close()

  x,y = proj(asarray(df['Longdeg'][thisyear]),asarray(df['Latdeg'][thisyear]))

  os.system('mkdir -p jpgs/ices_validation')
  for var in ['salt','temp']:
    cmap = cm.RdYlGn

    fig=figure()
    fig.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)

    # plot salt differences
    v = asarray(-df[var][thisyear]+df['model_%s'%var][thisyear])
    proj.scatter(x, y, s=8.0, c=v, edgecolors='none', cmap=cmap)

    if uselim:
      clim(vmin,vmax)
    else:
      if var=='salt':
        clim(-1.0,1.0)
      elif var=='temp':
        clim(-2.0,2.0)

    if titlestr=='':
      cbtitle = '%s (model-obs)'%var
    else:
      cbtitle = titlestr

    proj.drawcoastlines()
    proj.fillcontinents((0.9,0.9,0.8))

    cax = axes([0.03,0.2,0.25,0.03])
    cb=colorbar(cax=cax,orientation='horizontal')
    for ll in cax.get_xmajorticklabels():
      ll.set_rotation(60.)
    cb.set_label(u'%s %s'%(cbtitle,unitsstr))

    savefig('jpgs/ices_validation/%s_%d.jpg'%(var,year),dpi=300)
    close()



