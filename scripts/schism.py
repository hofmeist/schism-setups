

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
      self.depthsdict={}
      self.xdict={}
      self.ydict={}
      for nn in range(self.nnodes):
        dat=f.readline().split()
        n.append(int(dat[0]))
        x.append(float(dat[1]))
        y.append(float(dat[2]))
        d.append(float(dat[3]))
        self.depthsdict[n[-1]] = d[-1]
        self.ydict[n[-1]] = y[-1]
        self.xdict[n[-1]] = x[-1]
      self.inodes = n
      self.x = x
      self.y = y
      self.depths = d
      
      n=[]
      nv = []
      nvdict = {}
      for nn in range(self.nelements):
        dat=f.readline().split()
        n.append(int(dat[0]))
        nvnum = int(dat[1])
        nv.append([ int(ii) for ii in dat[2:2+nvnum]])
        nvdict[n[-1]] = nv[-1]
      self.ielement = n
      self.nv = nv
      self.nvdict = nvdict


      # get resolution of elements
      res = {}
      import numpy as np
      for el in self.nvdict:
        inodes = self.nvdict[el]
        x = [self.xdict[ii] for ii in inodes]
        y = [self.ydict[ii] for ii in inodes]
        res[el] = (np.sqrt((x[1]-x[0])**2 + (y[1]-y[0])**2) + np.sqrt((x[2]-x[1])**2 + (y[2]-y[1])**2) + np.sqrt((x[0]-x[2])**2 + (y[0]-y[2])**2))/3.0
      self.resolution_by_element = dict(res)

      # compute sides
      # first get sequence array
      self.nx = {}
      self.nx[3] = [[1,2],[2,0],[0,1]]
      self.nx[4] = [[1,2],[2,3],[3,0],[0,1]]

      # get inverse nv - neighbouring elements
      self.node_neighbour_elements = { i:[] for i in self.inodes }
      self.n_node_neighbours = { i:0 for i in self.inodes }
      for i,nv in zip(self.ielement,self.nv):
        for nnode in nv:
          self.n_node_neighbours[nnode] += 1
          self.node_neighbour_elements[nnode].append(i)
      # find neighbouring elements around element (ic3)
      self.element_sides={}
      self.side_nodes={}
      for i,nv in zip(self.ielement,self.nv):
        isides = []
        # loop around element for existing sides
        for iloop,(ind1,ind2) in enumerate(self.nx[len(nv)]):
          iside = 0
          nd1,nd2 = nv[ind1],nv[ind2]
          for checkelement in self.node_neighbour_elements[nd1]:
            if (checkelement != i) and (nd2 in self.nvdict[checkelement]):
              iside = checkelement
              break
          isides.append(iside)
        self.element_sides[i] = isides
      # count sides
      self.nsides = 0
      element_ids = self.element_sides.keys()
      element_ids.sort()
      for i in element_ids:
        for ii,iside in enumerate(self.element_sides[i]):
          if iside==0 or i<iside:
            self.nsides += 1
            iinds = self.nx[len(self.element_sides[i])][ii]
            self.side_nodes[self.nsides] = [self.nvdict[i][iinds[0]],self.nvdict[i][iinds[1]]]

      # average resolution_by_element on nodes
      self.resolution_by_nodes = {}
      for inode in self.node_neighbour_elements:
        elids = self.node_neighbour_elements[inode]
        self.resolution_by_nodes[inode] = np.asarray([self.resolution_by_element[ii] for ii in self.node_neighbour_elements[inode]]).mean()

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
        self.londict={}
        self.latdict={}
        for nn in range(self.nnodes):
          dat=f.readline().split()
          nll.append(int(dat[0]))
          lon.append(float(dat[1]))
          lat.append(float(dat[2]))
          self.londict[nll[-1]]=lon[-1]
          self.latdict[nll[-1]]=lat[-1]
        self.ill = nll
        self.lon = lon
        self.lat = lat
        f.close()
      except:
        print('  no hgrid.ll available')

      try:
        self.parse_vgrid()
      except:
        print('  no vgrid.in available')

      self.node_tree_xy=None
      self.node_tree_latlon=None
      self.element_tree_xy=None
      self.element_tree_latlon=None
      
  def parse_vgrid(self):
    import numpy as np
    f = open('vgrid.in')
    first = int(f.readline())
    znum = int(f.readline())
    self.znum = znum
    a = {}
    self.bidx = {}
    for line in f.readlines():
      sigma1d = -9999.*np.ones((znum,))
      data = line.split()
      self.bidx[int(data[0])] = int(data[1])
      sigma1d[int(data[1])-1:] = np.asarray([float(ii) for ii in data[2:]])
      a[int(data[0])] = np.ma.masked_equal(sigma1d,-9999.)
    f.close()
    self.vgrid = a

  def dump_hgridll(self,filename='hgrid_new.ll'):
    f = open(filename,'w')
    f.write('%s\n'%filename)
    f.write('%d %d\n'%(self.nelements,self.nnodes))
    # write nodes
    for n,x,y,d in zip(self.inodes,self.lon,self.lat,self.depths):
      f.write('%d %0.6f %0.6f %0.2f\n'%(n,x,y,d))

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

  def signed_area(self,nodelist):
      x1,y1 = (self.xdict[nodelist[0]],self.ydict[nodelist[0]])
      x2,y2 = (self.xdict[nodelist[1]],self.ydict[nodelist[1]])
      x3,y3 = (self.xdict[nodelist[2]],self.ydict[nodelist[2]])
      return ((x1-x3)*(y2-y3)-(x2-x3)*(y1-y3))/2.0

  def dump_gr3(self,filename,const=0.0,comment='gr3 by create_ic.py'):
      f = open(filename,'w')
      f.write('%s\n'%comment)
      f.write('%d %d\n'%(self.nelements,self.nnodes))
      for i,x,y in zip(self.inodes,self.x,self.y):
        f.write('%d %0.2f %0.2f %0.5f\n'%(i,x,y,const))
      f.close()

  def dump_tvd_prop(self):
      f = open('tvd.prop','w')
      for i in self.ielement:
        f.write('%d 1\n'%i)
      f.close()

  def bdy_array(self,fname,num=0):
      """
      read boundary *.th files into a numpy array
      """
      import numpy as np

      if num == 0:
        num = self.num_bdy_nodes
      if fname == 'elev2D.th':
        f = open(fname,'rb')
        times = []
        data = []
        while f.read(1):
          f.seek(-1,1)
          times.append(np.fromfile(f,dtype='float32',count=1))
          data.append(np.fromfile(f,dtype='float32',count=num))
        times = np.asarray(times)
        data = np.asarray(data)
        return times,data
      else:
        print('  no support for file type %s'%fname)

  def init_node_tree(self,latlon=True):
    print('  build node tree')
    if latlon:
      self.node_tree_latlon = ckDTree(zip(self.lon,self.lat))
    else:
      self.node_tree_xy = cKDTree(zip(self.x,self.y))

  def init_element_tree(self,latlon=True):
    print('  build node tree')
    if latlon:
      self.element_lon={}
      self.element_lat={}
      for el in self.nvdict:
        self.element_lon[el]=sum([self.londict[idx] for idx in self.nvdict[el]])/len(self.nvdict[el])
        self.element_lat[el]=sum([self.londict[idx] for idx in self.nvdict[el]])/len(self.nvdict[el])

      self.element_tree_latlon = ckDTree(zip(self.element_lon.values(),self.element_lat.values))
      self.element_tree_ids = self.element_lon.keys()

  def find_nearest_node(self,x,y,latlon=True):
    """
    find nearest node for given coordinate
    """
    ridx=-1
    if latlon:
      if self.node_tree_latlon==None:
        self.init_node_tree(latlon=True)
      idx,d = self.node_tree_latlon.query((x,y),k=1)
      ridx = self.ill[idx]
    else:
       if self.node_tree_latlon==None:
        self.init_node_tree(latlon=False)
      idx,d = self.node_tree_latlon.query((x,y),k=1)
      ridx = self.inodes[idx]

    return ridx

  def find_nearest_element(self,x,y,latlon=True):
    """
    give coordinates and find nearest element
    """
    ridx=-1
    if latlon:
      if self.element_tree_latlon==None:
        self.init_element_tree(latlon=True)
      idx,d = self.element_tree_latlon.query((x,y),k=1)
      ridx = self.element_tree_ids[idx]
    return ridx
        
if __name__ == '__main__':

    from pylab import *
    setup = schism_setup('hgrid.gr3')
    # plot domain
    setup.plot_domain_boundaries()

    # read elevation boundaries
    t,e = setup.bdy_array('elev2D.th')
    figure()
    plot(t[:],e[:,50])
    show()
