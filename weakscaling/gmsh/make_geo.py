from pylab import sqrt
import os
nums = [4,8,16,32,64,128]

res=200.

for num in nums:
  # get roughly 500 nodes per CPU
  length = sqrt(num/128. * 1300000) * res 
  f = open('scaling%d.geo'%num,'w')
  f.write('''Mesh.CharacteristicLengthFromPoints = 1;

res = 200.0;
hres = 80.0;
length = %0.1f;

Point(1) = {-0.5*length, -0.5*length, 0., res};
Point(2) = {0.5*length, -0.5*length, 0., res};
Point(3) = {0.5*length, 0.5*length, 0., res};
Point(4) = {-0.5*length, 0.5*length, 0., res};
Point(10) = {length+4000.,length+4000,0.,hres};

Line(5) = {1, 2};
Line(6) = {2, 3};
Line(7) = {3, 4};
Line(8) = {4, 1};

Line Loop(9) = {5,6,7,8};

Plane Surface(10) = {9};

Point {10} In Surface {10};

Physical Line("landbdy") = {5,6,7,8};
Physical Surface("water") = {10};
  '''%length)
  f.close()
  os.system('gmsh -2 scaling%d.geo'%num)
  os.system('python ../../scripts/msh2gr3.py scaling%d.msh'%num)
  os.system('mv hgrid.gr3 hgrid%d.gr3'%num)

