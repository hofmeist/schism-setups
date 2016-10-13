from pylab import *
from tappy import tappy
import pandas
import sys, os
from datetime import datetime,timedelta


df = pandas.read_csv(sys.argv[1],delim_whitespace=True, header=None, names=['secs','A','B','C','D'] )

origin = datetime(2012,1,1,0,0,0)
dates = asarray([ origin + timedelta(0,s) for s in df['secs']])

if True:
    # Load a time series to analyse
    #dates = ... # a datetime.datetime list of dates
    #elevation = ... # a list of surface elevation values

    # Set up the bits needed for TAPPY. This is mostly lifted from
    # tappy.py in the baker function "analysis" (around line 1721).
    quiet = True
    debug = False
    outputts = False
    outputxml = False
    ephemeris = False
    rayleigh = 1.0
    print_vau_table = False
    missing_data = 'ignore'
    linear_trend = False
    remove_extreme = False
    zero_ts = None
    filter = None
    pad_filters = None
    include_inferred = True
    if rayleigh:
        ray = float(rayleigh)

    x = tappy.tappy(
        outputts = outputts,
        outputxml = outputxml,
        quiet=quiet,
        debug=debug,
        ephemeris=ephemeris,
        rayleigh=rayleigh,
        print_vau_table=print_vau_table,
        missing_data=missing_data,
        linear_trend=linear_trend,
        remove_extreme=remove_extreme,
        zero_ts=zero_ts,
        filter=filter,
        pad_filters=pad_filters,
        include_inferred=include_inferred,
        )

xpos = {'A':-30.0,'B':0.0,'C':20.0,'D':90.0}
t_amp = {}
constis = ['S2','S4','S6']
stations = ['A','B','C','D']

for station in stations:

    x.dates = dates
    x.elevation = df[station].values.tolist()
    package = x.astronomic(x.dates)
    (x.zeta, x.nu, x.nup, x.nupp, x.kap_p, x.ii, x.R, x.Q, x.T, x.jd, x.s, x.h, x.N, x.p, x.p1) = package
    (x.speed_dict, x.key_list) = x.which_constituents(len(x.dates),
            package, rayleigh_comp=ray)

    x.constituents() # the analysis

    t_amp[station] = {}
    for cc in constis:
      t_amp[station][cc] = float(x.r[cc])

f = figure(figsize=(12,3))
f.subplots_adjust(left=0.08,right=0.98,wspace=0.35)

for ii,station in enumerate(stations):

  ax = subplot(100+10*len(stations)+ii+1)

  xpos = [0.5,1.5,2.5]
  values = [t_amp[station]['S2']/10.,t_amp[station]['S4'],t_amp[station]['S6']]
  ax.bar(xpos,values, width=0.5,color=[(0.2,0.25,0.4),(0.3,0.5,0.8),(0.6,0.7,0.8)],align='center',edgecolor='none')
  ax.set_xticks(xpos)
  ax.set_xticklabels(['S2/10','S4','S6'])
  ax.set_xlim(0,3)
  ax.set_ylim(0,0.2)
  text(2.5,0.17,station,size=25.)
  if ii==0:
    ax.set_ylabel('amplitude [m]')


savefig(sys.argv[1]+'_constituents.pdf',dpi=300)
