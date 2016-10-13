import sys
sys.path.append('/local/home/hofmeist/schism/setups/scripts')
from schism import *

if len(sys.argv) > 1:
  hgridfile=sys.argv[1]
else:
  hgridfile='hgrid.gr3'

s = schism_setup(hgrid_file=hgridfile)

for nvid in s.nvdict:
  area = s.signed_area(s.nvdict[nvid])
  if area < 0.0:
    print('  area of element %d: %0.2f'%(nvid,area))
    sys.exit()

