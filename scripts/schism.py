

class schism_setup(object):
  
  def __init__(self,hgrid_file='hgrid.gr3',ll_file='hgrid.ll',vgrid_file='vgrid.gr3'):
      self.hgrid_file=hgrid_file
      
      # parse hgrid file
      f = open(hgrid_file)
      self.description = f.readline().rstrip()
      dat = f.readline().split()
      self.nelements = int(dat[0])
      self.nnodes = int(dat[1])
      
      n=[]
      x=[]
      y=[]
      d=[]
      for nn in range(self.nnodes):
        dat=f.readline().split()
        n.append(int(dat[0]))
        x.append(float(dat[1]))
        y.append(float(dat[2]))
        d.append(float(dat[3]))
      self.inodes = n
      self.x = x
      self.y = y
      self.depths = d
      
      n=[]
      nv = []
      for nn in range(self.nelements):
        dat=f.readline().split()
        n.append(int(dat[0]))
        nvnum = int(dat[1])
        nv.append([ int(ii) for ii in dat[2:2+nvnum]])
      self.ielement = n
      self.nv = nv
      
      self.num_bdy_segments = int(f.readline().split()[0])
      if self.num_bdy_segments > 0:
        self.num_bdy_nodes = int(f.readline().split()[0])
      self.bdy_segments=[]
      self.bdy_nodes=[]
      for iseg in range(self.num_bdy_segments):
        nlines = int(f.readline().split()[0])
        self.bdy_segments.append( [int(f.readline()) for nn in range(nlines)] )
        self.bdy_nodes.extend(self.bdy_segments[-1])

      self.num_land_segments = int(f.readline().split()[0])
      if self.num_land_segments > 0:
        self.num_land_nodes = int(f.readline().split()[0])
      self.land_nodes=[]
      self.island_segments=[]
      self.land_segments=[]
      for iseg in range(self.num_land_segments):
        dat = f.readline().split()
        nlines = int(dat[0])
        if int(dat[1])==0:
          self.land_segments.append( [int(f.readline()) for nn in range(nlines)] )
          self.land_nodes.extend(self.land_segments[-1])
        elif int(dat[1])==1:
          self.island_segments.append( [int(f.readline()) for nn in range(nlines)] )
          self.land_nodes.extend(self.island_segments[-1])
     
      f.close()

      # parse hgrid.ll file
      try:
        f = open(ll_file)
        line = f.readline().rstrip()
        dat = f.readline().split()
        ll_nelements = int(dat[0])
        ll_nnodes = int(dat[1])
      
        nll = []
        lon=[]
        lat=[]
        for nn in range(self.nnodes):
          dat=f.readline().split()
          nll.append(int(dat[0]))
          lon.append(float(dat[1]))
          lat.append(float(dat[2]))
        self.ill = n
        self.lon = lon
        self.lat = lat
        f.close()
      except:
        print('  no hgrid.ll available')

  def dump_hgridll(self,filename='hgrid_new.ll'):
    f = open(filename,'w')
    f.write('%s\n'%filename)
    f.write('%d %d\n'%(self.nelements,self.nnodes))
    # write nodes
    for n,x,y,d in zip(self.inodes,self.lon,self.lat,self.depths):
      f.write('%d %0.2f %0.2f %0.2f\n'%(n,x,y,d))

    # write elements
    for n,nv in zip(self.ielement,self.nv):
      f.write('%d %d '%(n,len(nv)))
      for nvi in nv:
        f.write('%d '%nvi)
      f.write('\n')
    # write boundaries
    f.close()

  def get_bdy_latlon(self):
      bdylon = [ self.lon[ii-1] for ii in self.bdy_nodes ]
      bdylat = [ self.lat[ii-1] for ii in self.bdy_nodes ]
      return (bdylon,bdylat)

  def plot_domain_boundaries(self):
      from pylab import figure,plot,show,legend,xlabel,ylabel
      f = figure()
      
      label='open boundary'
      for seg in self.bdy_segments:
        lon = [ self.lon[ii-1] for ii in seg ]
        lat = [ self.lat[ii-1] for ii in seg ]
        plot( lon,lat, 'ro-', ms=0.5, label=label, markeredgecolor='r')
        label=''

      label='land boundary'
      for seg in self.land_segments:
        lon = [ self.lon[ii-1] for ii in seg ]
        lat = [ self.lat[ii-1] for ii in seg ]
        lcol = (0.6,0.6,0.6)
        plot( lon,lat, 'o-',color=lcol, ms=0.1, label=label, markeredgecolor=lcol)
        label=''
 
      label='island boundary'
      for seg in self.island_segments:
        lon = [ self.lon[ii-1] for ii in seg ]
        lat = [ self.lat[ii-1] for ii in seg ]
        lcol = (0.3,0.3,0.3)
        plot( lon,lat, 'o-',color=lcol, ms=0.1, label=label, markeredgecolor=lcol)
        label=''

      legend(loc='lower right',frameon=False)
      xlabel('longitude [degE]')
      ylabel('latitude [degN]')
      show()

  def bdy_array(self,fname):
      """
      read boundary *.th files into a numpy array
      """
      import numpy as np

      if fname == 'elev2D.th':
        f = open(fname,'rb')
        times = []
        data = []
        while f.read(1):
          f.seek(-1,1)
          times.append(np.fromfile(f,dtype='float32',count=1))
          data.append(np.fromfile(f,dtype='float32',count=self.num_bdy_nodes))
        times = np.asarray(times)
        data = np.asarray(data)
        return times,data
      else:
        print('  no support for file type %s'%fname)

        
if __name__ == '__main__':

    from pylab import *
    setup = schism_setup('hgrid.gr3')
    # plot domain
    setup.plot_domain_boundaries()

    # read elevation boundaries
    t,e = setup.bdy_array('elev2D.th')
    plot(t[:],e[:,0])
    show()
