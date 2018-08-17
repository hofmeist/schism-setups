import pickle
#from pylab import *

class gr3():
  nodesxy={}
  depths={}
  lonlat={}
  elements={}
  openboundary_nodes=[]
  num_openboundary_nodes=0
  land_nodes=[]
  num_land_nodes=0
  island_nodes=[]
  num_island_nodes=0
  def set_nodes_and_elements(self,nodes={},elements=[],depth=10.0):
    self.nodesxy=nodes
    for id in self.nodesxy:
      self.depths[id] = depth
    for ielement,element in enumerate(elements):
      self.elements[ielement+1]=element

  def signed_area(self,nodelist):
    x1,y1 = self.nodesxy[nodelist[0]]
    x2,y2 = self.nodesxy[nodelist[1]]
    x3,y3 = self.nodesxy[nodelist[2]]
    return ((x1-x3)*(y2-y3)-(x2-x3)*(y1-y3))/2.0

  def import_mesh(self,mesh,depth=10.,remove_hanging_nodes=False):
    self.nodesxy=mesh.nodes
    for id in self.nodesxy:
      self.depths[id] = depth
    for ielement,element in enumerate(mesh.elements):
      self.elements[ielement+1]=element

    id = mesh.labelids['landbdy']
    self.num_land_nodes=mesh.linelengths['landbdy']
    self.land_nodes=mesh.lines['landbdy']

    if 'openbdy' in mesh.hgridids:
      id = mesh.labelids['openbdy']
      self.num_openboundary_nodes=mesh.linelengths['openbdy']
      self.openboundary_nodes=mesh.lines['openbdy']
    else:
      self.num_openboundary_nodes=0
      self.openboundary_nodes=[]

    if 'islandbdy' in mesh.hgridids:
      id = mesh.labelids['islandbdy']
      self.num_island_nodes=mesh.linelengths['islandbdy']
      self.island_nodes=mesh.lines['islandbdy']
    else:
      self.num_island_nodes = 0
      self.island_nodes=[]

    if False:
      # remove island boundaries with length=2
      island_nodes = self.island_nodes
      self.island_nodes=[]
      self.num_island_nodes=0
      for nlist in island_nodes:
        if len(nlist)>2:
          self.island_nodes.append(nlist)
          self.num_island_nodes+=len(nlist)
        else:
          # do not remove hanging nodes here
          if False:
            for nidx in nlist:
              try:
                del self.nodesxy[nidx]
                del self.depths[nidx]
                print "remove hanging node %d"%nidx
              except:
                print "could not find node %d"%nidx

          
    # remove hanging nodes
    if remove_hanging_nodes:
      nodesxy=dict(self.nodesxy)
      for idx in nodesxy:
        found=False
        for elidx in self.elements:
          if idx in self.elements[elidx]:
            found=True
            break
        if not(found):
          print "remove hanging node %d"%idx
          try:
            del self.nodesxy[idx]
            del self.depths[idx]
          except:
            pass

  def renumber_nodes(self):
    newids = {}
    for newid,oldid in enumerate(self.nodesxy):
      newids[oldid]=newid+1
    self.newids=newids
    self.oldxy=dict(self.nodesxy)
    
    oldxy=dict(self.nodesxy)
    self.nodesxy={}
    for elid in oldxy:
      self.nodesxy[newids[elid]] = oldxy[elid]

    olddepths=dict(self.depths)
    self.depths={}
    for elid in olddepths:
      self.depths[newids[elid]] = olddepths[elid]

    for elid in self.elements:
      self.elements[elid] = [newids[oldid] for oldid in self.elements[elid][::-1]]
      # check for counter-clockwise sequence:
      area = self.signed_area(self.elements[elid]) 
      if area < 0.0:
        #print('  negative area for element %d: %0.2f, reversing nodes'%(elid,area))
        self.elements[elid] = [ nid for nid in self.elements[elid][::-1]]
      else:
        print(' area for element %d: %0.2f'%(elid,area))
    for elid in range(len(self.land_nodes)):
      self.land_nodes[elid] = [newids[oldid] for oldid in self.land_nodes[elid]]
    for elid in range(len(self.openboundary_nodes)):
      self.openboundary_nodes[elid] = [newids[oldid] for oldid in self.openboundary_nodes[elid]]
    for elid in range(len(self.island_nodes)):
      self.island_nodes[elid] = [newids[oldid] for oldid in self.island_nodes[elid]]


  def dump(self,filename='hgrid.gr3'):
    f = open(filename,'w')
    f.write('%s\n'%filename)
    f.write('%d %d\n'%(len(self.elements),len(self.nodesxy)))
    #f.write('%d\n'%len(self.nodesxy))
    for node in self.nodesxy:
      f.write('%d %0.2f %0.2f %0.2f\n'%(node,self.nodesxy[node][0],self.nodesxy[node][1],self.depths[node]))
    #f.write('%d\n'%len(self.elements))
    for el in self.elements:
      i,j,k = self.elements[el]
      f.write('%d 3 %d %d %d\n'%(el,i,j,k))
    # open boundary nodes
    f.write('%d = Number of open boundaries\n'%(len(self.openboundary_nodes)))
    f.write('%d = Total number of open boundary nodes\n'%self.num_openboundary_nodes)
    for sublist in self.openboundary_nodes:
      f.write('%d\n'%len(sublist))
      for node in sublist:
        f.write('%d\n'%node)
    
    # land nodes
    f.write('%d = Number of land boundaries\n'%(len(self.land_nodes) + len(self.island_nodes)))
    f.write('%d = Total number of land boundary nodes\n'%(self.num_land_nodes+self.num_island_nodes))
    for i,sublist in enumerate(self.land_nodes):
      f.write('%d 0 = Number of nodes for land boundary %d\n'%(len(sublist),i+1))
      for node in sublist:
        f.write('%d\n'%node)

    # island nodes
    for i,sublist in enumerate(self.island_nodes):
      f.write('%d 1 = Number of nodes for island boundary %d\n'%(len(sublist),i+1))
      for node in sublist:
        f.write('%d\n'%node)

    f.close()

  def nodes_in_elements(self):
    nodes=[]
    for (i,j,k) in self.elements:
      nodes.append(i)
      nodes.append(j)
      nodes.append(k)
    return list(set(nodes))

    
class msh():
  nodes={}
  elements=[]
  lines={}
  linelengths={}
  tmplines={}
  linelabels={}
  labelids={}
  sublist={}
  sublabels={}
  linesbyid={}
  subidbyid={}
  def __init__(self,filename):
    f=open(filename)
    mode='none'
    read=True
    while read:
      line=f.readline()
      #print('-%s-'%line.strip())
      if line.strip()=='$PhysicalNames':
        line=f.readline()
        num=int(line)
        for inum in range(num):
          line=f.readline()
          dat=line.split()
          self.lines[int(dat[1])] = []
          self.linelabels[int(dat[1])] = dat[2][1:-1] # cut off quotes
          self.labelids[dat[2][1:-1]]=int(dat[1])
      if line.strip()=='$Nodes':
        num=int(f.readline())
        for inum in range(num):
          line=f.readline()
          dat=line.split()
          self.nodes[int(dat[0])] = (float(dat[1]),float(dat[2]))
      if line.strip()=='$Elements':
        num=int(f.readline())
        for inum in range(num):
          line=f.readline()
          dat=line.split()
          id = int(dat[0])
          if dat[1] == '2': # assume area element
            numlabels=int(dat[2])
            self.elements.append([int(ii) for ii in dat[(3+numlabels):]])
          elif dat[1] == '1': # assume line element
            numlabels=int(dat[2])
            labelid=tuple([int(ii) for ii in dat[3:3+numlabels]])
            if not(self.tmplines.has_key(labelid)):
              self.tmplines[labelid]=[]
            self.tmplines[labelid].append([int(ii) for ii in dat[(3+numlabels):]])
            # append lines, sorted by element
            if not(self.linesbyid.has_key(int(dat[3]))):
              self.linesbyid[int(dat[3])]=[]
              self.subidbyid[int(dat[3])]=[]
            self.linesbyid[int(dat[3])].append([int(ii) for ii in dat[(3+numlabels):]])
            self.subidbyid[int(dat[3])].append(int(dat[4]))

        read=False

    # now go through list and identify common land and island polygons
    # using the subid does work for splines (openbdys), but not
    # for lists of lines, since each line got a unique subid
    self.sublabels = {'openbdy':[self.labelids['openbdy'],],'landbdy':[],'islandbdy':[]}
    self.sublabeltypes = {}
    for label in self.labelids:
      for check in self.sublabels:
        if (check == label[:len(check)]) and (check != label):
          self.sublabels[check].append(self.labelids[label])
          self.sublabeltypes[self.labelids[label]] = check
        elif (check == label):
          self.sublabeltypes[self.labelids[label]] = 'none'

    if True:
      self.subkeys={'openbdy':[],'landbdy':[],'islandbdy':[]}

      # treat openbdys:
      ob_id = self.labelids['openbdy']
      for subid,(p1,p2) in zip(self.subidbyid[ob_id],self.linesbyid[ob_id]):
        subkey = (ob_id,subid)
        if subkey not in self.subkeys['openbdy']:
          self.subkeys['openbdy'].append(subkey)
        if self.sublist.has_key(subkey):
          self.sublist[subkey].append(p2)
        else:
          self.sublist[subkey] = [p1,p2]
      print('sublist[3]',self.sublist[(ob_id,3)][0],self.sublist[(ob_id,3)][-1])

      # treat linelists:
      for label in ['landbdy','islandbdy']:
        for labelid in self.sublabels[label]:
          self.subkeys[self.sublabeltypes[labelid]].append(labelid)
          for p1,p2 in self.linesbyid[labelid]:
            if self.sublist.has_key(labelid):
              self.sublist[labelid].append(p2)
            else:
              self.sublist[labelid] = [p1,p2]

    else:
      # this is the old part of the code, where all bdy lines were splines
      # 
      # reduce lines to lists of points
      self.subkeys={}
      # go through whole list and get number of subkeys
      for key in self.tmplines:
        labelid=key[0]
        subid=key[1]
        if not(subkeys.has_key(labelid)):
          self.subkeys[labelid]=[]
        self.subkeys[labelid].append(subid)
        for subline in self.tmplines[key]:
          p1=subline[0]
          p2=subline[1]
          if self.sublist.has_key(subid):
            if p1 not in self.sublist[subid]:
              self.sublist[subid].append(p1)
            if p2 not in self.sublist[subid]:
              self.sublist[subid].append(p2)
          else:
            self.sublist[subid] = [p1,p2]

      # from here on: expect that labelids still contain only
      # [landbdy, openbdy, islandbdy, water], but sublines are ordered into subkeys
      for labelid in self.subkeys:
        self.linelengths[labelid] = 0
        self.subkeys[labelid] = list(set(self.subkeys[labelid]))
        for subkey in self.subkeys[labelid]:
          if not(self.lines.has_key(labelid)):
            self.lines[labelid]=[]
          self.lines[labelid].append(self.sublist[subkey])
          self.linelengths[labelid] += len(self.sublist[subkey])

    # continue with the new strategy:
    self.hgridids={'openbdy':[],'landbdy':[],'islandbdy':[]}
    self.lines={'openbdy':[],'landbdy':[],'islandbdy':[]}
    self.linelengths={'openbdy':0,'landbdy':0,'islandbdy':0}
    for label in self.hgridids:
      if label=='openbdy':
        print('label: %s, len = %d'%(label,len(list(set(self.subkeys[label])))))
        self.hgridids[label].extend(list(set(self.subkeys[label])))
      else:
        print('label: %s, len = %d'%(label,len(self.sublabels[label])))
        self.hgridids[label].extend(self.sublabels[label])
    
    for label in self.hgridids:
      for subkey in self.hgridids[label]:
        self.lines[label].append(self.sublist[subkey])
        self.linelengths[label] += len(self.sublist[subkey])

      
if __name__ == '__main__':
  import sys
  if False:
    # read projection:
    pf = open('coast_proj.pickle','rb')
    m, = pickle.load(f)
    pf.close()

  if len(sys.argv)>1:
    filename=sys.argv[1]
  else:
    filename='coast.msh'
  mesh=msh(filename)
  hgrid=gr3()
  hgrid.import_mesh(mesh)
  print '  renumber nodes'
  hgrid.renumber_nodes()
  hgrid.dump('hgrid.gr3')



