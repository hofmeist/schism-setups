# Compile SCHISM on mistral with cmake

Prepare modules and create a build directory, e.g.
```shell

module unload netcdf_c
module load intel/17.0.1
module load intelmpi/5.1.3.223
module load ncview
module load python/2.7-ve0
export FC=mpiifort
export CC=mpiicc
export NC_C_DIR=/sw/rhel6-x64/netcdf/netcdf_c-4.4.0-gcc48
export PATH=$PATH:$NC_C_DIR/bin
export PATH=$PATH:/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.3-intel14/bin

mkdir build; cd build
```

## production compilation

Then call cmake to prepare compilation, assume the SCHISM source in `../src`
```
cmake ../src -DNetCDF_FORTRAN_DIR=/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.3-intel14 -DCMAKE_Fortran_COMPILER=mpiifort -DCMAKE_CXX_COMPILER=mpiicc -DNetCDF_C_DIR=/sw/rhel6-x64/netcdf/netcdf_c-4.4.0-gcc48 -DTVD_LIM=SB -DCMAKE_Fortran_FLAGS="-xCORE-AVX2"
```

FABM is enabled with extra options `-DUSE_FABM=ON -DFABM_BASE=~/schism/fabm`
GOTM is enabled with extra options `-DUSE_GOTM=ON -DGOTM_DIR=~/schism/gotm`

## debug compilation

```
cmake ../src -DNetCDF_FORTRAN_DIR=/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.3-intel14 -DCMAKE_Fortran_COMPILER=mpiifort -DCMAKE_CXX_COMPILER=mpiicc -DNetCDF_C_DIR=/sw/rhel6-x64/netcdf/netcdf_c-4.4.0-gcc48 -DTVD_LIM=SB -DCMAKE_Fortran_FLAGS="-xCORE-AVX2 -g -O0 -traceback -check bounds -gen-interfaces -warn interfaces -fp-stack-check"
```

## use generic tracer

```
cmake ../src -DNetCDF_FORTRAN_DIR=/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.3-intel14 -DCMAKE_Fortran_COMPILER=mpiifort -DCMAKE_CXX_COMPILER=mpiicc -DNetCDF_C_DIR=/sw/rhel6-x64/netcdf/netcdf_c-4.4.0-gcc48 -DTVD_LIM=SB -DCMAKE_Fortran_FLAGS="-xCORE-AVX2 -DUSE_GEN"
```

## compile GOTM

GOTM is compiled separately, and can be used in SCHISM later with/without FABM or debug compilation (although GOTM itself is not compiled with debug flags)

```shell
mkdir -p gotm/build
cd gotm
git clone git://github.com/gotm-model/code.git gotm-code
cd build
cmake ../gotm-code/src -DCMAKE_INSTALL_PREFIX=.. -DGOTM_EMBED_VERSION=ON -DGOTM_USE_FABM=OFF
make install
```

