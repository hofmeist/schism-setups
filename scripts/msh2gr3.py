import pickle
from pylab import *

if False:
  # read projection:
  pf = open('coast_proj.pickle','rb')
  m, = pickle.load(f)
  pf.close()

class gr3():
  nodesxy={}
  depths={}
  lonlat={}
  elements={}
  openboundary_nodes=[]
  land_nodes=[]
  island_nodes=[]
  def set_nodes_and_elements(self,nodes={},elements=[],depth=10.0):
    self.nodesxy=nodes
    for id in self.nodesxy:
      self.depths[id] = depth
    ielement=len(self.elements)
    for element in elements:
      self.elements[ielement+1]=element
      ielement+=1
      

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
    
    # land nodes

    # island nodes

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
  labels={}
  def __init__(self,filename):
    f=open(filename)
    mode='none'
    read=True
    while read:
      line=f.readline()
      print('-%s-'%line.strip())
      if line.strip()=='$PhysicalNames':
        line=f.readline()
        num=int(line)
        for inum in range(num):
          line=f.readline()
          dat=line.split()
          self.lines[int(dat[1])] = []
          self.labels[int(dat[1])] = dat[2][1:-1] # cut off quotes
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
            for l in range(numlabels):
              self.lines[int(dat[2+l])].append([int(ii) for ii in dat[(3+numlabels):]])
        read=False

mesh=msh('coast.msh')
hgrid=gr3()
hgrid.set_nodes_and_elements(mesh.nodes,mesh.elements)
hgrid.dump('hgrid.gr3')



