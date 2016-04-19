

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
      for nn in range(self.nnodes):
        dat=f.readline().split()
        n.append(int(dat[0]))
        x.append(float(dat[1]))
        y.append(float(dat[2]))
      self.inodes = n
      self.x = x
      self.y = y
      
      n=[]
      nv = []
      for nn in range(self.nelements):
        dat=f.readline().split()
        n.append(int(dat[0]))
        nvnum = int(dat[1])
        nv.append([ int(ii) for ii in dat[2:nvnum]])
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
