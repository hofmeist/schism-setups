SCHISM scaling setup
====================

Here, we use a rectangular domain, with a horizontal grid resolution of 200m and three refinement areas with 50m resolution.
This setup can run for a few timesteps to get an idea about parallel scaling.

The initial elevation has an east-west-gradient in elev.ic
The density is set up as north-south log-exchange through salt.ic

bottom roughness and mixing length-scale are horizontally constant in rough.gr3 and xlsc.gr3
