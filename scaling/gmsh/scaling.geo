Mesh.CharacteristicLengthFromPoints = 1;

res = 200.0;
hres = 30.0;
length = 100000.0;

Point(1) = {0., 0., 0., res};
Point(2) = {length, 0., 0., res};
Point(3) = {length, length, 0., res};
Point(4) = {0.0, length, 0., res};
Point(10) = {length*0.2,length*0.2,0.,hres};
Point(11) = {length*0.6,length*0.5,0.,hres};
Point(12) = {length*0.7,length*0.8,0.,hres};

Line(5) = {1, 2};
Line(6) = {2, 3};
Line(7) = {3, 4};
Line(8) = {4, 1};

Line Loop(9) = {5,6,7,8};

Plane Surface(10) = {9};

Point {10} In Surface {10};
Point {11} In Surface {10};
Point {12} In Surface {10};

Physical Line("landbdy") = {5,7};
Physical Line("openbdy") = {6,8};
Physical Surface("water") = {10};

