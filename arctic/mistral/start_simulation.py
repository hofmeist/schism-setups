import subprocess as sub
import sys
import os

if len(sys.argv)<2:
  print('  Usage: start_month.py ID')
  sys.exit(1)
else:
  id = sys.argv[1]
  if len(sys.argv)>=4:
    # expect first and last month
    start_year,start_month = [int(nn) for nn in sys.argv[2].split('-')]
    end_year,end_month = [int(nn) for nn in sys.argv[3].split('-')]
    if len(sys.argv)==5:
      startafter=sys.argv[4]
      rundep = '--dependency=afterok:%s'%startafter
    else:
      rundep = ''
  else:
    start_year=2012
    start_month=1
    end_year=2012
    end_month=12

def create_workdir(path,origpath='/pf/g/%s/schism/setups/arctic'%os.environ['USER']):
  """
  create working directory and link necessary forcing
  """
  import shutil
  import os
  if os.path.exists(path) and os.path.isdir(path):
    shutil.rmtree(path)
  os.makedirs(path)
  os.makedirs(os.path.join(path,'outputs'))
  linklist=['sflux','elev.ic','tvd.prop','hgrid.gr3','hgrid.ll','watertype.gr3','diffmin.gr3','diffmax.gr3','windrot_geo2proj.gr3','elev2D.th.nc','SAL_3D.th.nc','TEM_3D.th.nc','vgrid.in']
  for f in linklist:
    try:
      os.symlink(os.path.join(origpath,f),os.path.join(path,f))
    except:
      print('  cannot link %s'%f)
  copylist=['param.default','ice.nml','gotmturb.nml','fabm.nml','albedo.gr3','rough.gr3','bctides.in','station.in']
  for f in copylist:
    try:
      os.system('cp %s %s 2> /dev/null'%(os.path.join(origpath,f),os.path.join(path,f)))
    except:
      print('  cannot copy %s'%f)


def log_directive(workdir,yyyymm,logname='log'):
  logstr='--output=%s/%s_%s.o'%(workdir,logname,yyyymm)
  logstr+=' --error=%s/%s_%s.e'%(workdir,logname,yyyymm)
  return logstr

years=[2012,2013,2014,2015]
years=range(start_year,end_year+1)

months=range(1,13)
yearmonths={}
for year in years:
  if year == start_year:
    sm = start_month
  else:
    sm = 1
  if year == end_year:
    em = end_month
  else:
    em = 12
  yearmonths[year] = range(sm,em+1)

debug=False
runid='arctic'+id
if debug: out="1 1"
workdir='/scratch/g/%s/schism-results/%s'%(os.environ['USER'],runid)
os.system('mkdir -p %s'%workdir)

for year in years:
  for month in yearmonths[year]:
    yyyymm='%04d-%02d'%(year,month)
    print('hotstart period %s'%yyyymm)

    logrun=log_directive(workdir,yyyymm,logname='log')
    loghot=log_directive(workdir,yyyymm,logname='log_hmerge')
    logmerge=log_directive(workdir,yyyymm,logname='log_merge')
    logecomerge=log_directive(workdir,yyyymm,logname='log_ecomerge')

    currdir = os.path.join(workdir,yyyymm)
    create_workdir(currdir)

    # run the model
    cmd = 'sbatch %s %s mistral/run_hotstart.sh %s %s'%(rundep,logrun,workdir,yyyymm)
    if debug:
      print(cmd.split())
    else:
      #out = commands.getoutput(cmd)
      out = sub.check_output(cmd.split(),universal_newlines=True)
    pid = out.split()[-1]

    # merge hotstart files
    cmd = 'sbatch --dependency=afterok:%s %s mistral/merge_hotstart.sh %s %s'%(pid,loghot,runid,yyyymm)
    if debug:
      print(cmd.split())
    else:
      #out = commands.getoutput(cmd)
      out = sub.check_output(cmd.split(),universal_newlines=True)
    hmerge_pid = out.split()[-1]
    rundep = '--dependency=afterok:%s'%hmerge_pid
    
    # merge output
    cmd = 'sbatch --dependency=afterok:%s %s mistral/merge_output.sh %s %s'%(pid,logmerge,runid,yyyymm)
    if debug:
      print(cmd.split())
    else:
      #out = commands.getoutput(cmd)
      out = sub.check_output(cmd.split(),universal_newlines=True)
    omerge_pid = out.split()[-1]


