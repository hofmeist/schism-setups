from pylab import *
from tappy import tappy
import pandas
import sys, os
from datetime import datetime,timedelta


df = pandas.read_csv(sys.argv[1],delim_whitespace=True, header=None, names=['secs','e1','e2','e3','e4'] )

origin = datetime(2012,1,1,0,0,0)
dates = asarray([ origin + timedelta(0,s) for s in df['secs']])
elevation = df['e2'].values

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

    x.dates = dates
    x.elevation = elevation.tolist()
    package = x.astronomic(x.dates)
    (x.zeta, x.nu, x.nup, x.nupp, x.kap_p, x.ii, x.R, x.Q, x.T, x.jd, x.s, x.h, x.N, x.p, x.p1) = package
    (x.speed_dict, x.key_list) = x.which_constituents(len(x.dates),
            package, rayleigh_comp=ray)

    x.constituents() # the analysis

    # Print the M2 amplitude and phase.
    print(x.r)
    #print('M2 phase:     {}'.format(x.phase[x.key_list.index('M2')]))
    #print('M2 amplitude: {}'.format(x.r[x.key_list.index('M2')]))
