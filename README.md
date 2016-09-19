# ocean-ic

Create ocean initial conditions by regridding GODAS or ORAS4 reanalysis to MOM or NEMO grids.

# Dependencies

This tool is written in Python and depends on many different Python packages. See section 'Install' below for instructions on how to download all of the Python dependencies. It also depends on
 [ESMF_RegridWeightGen](https://www.earthsystemcog.org/projects/regridweightgen/) program to perform regridding between non-rectilinear grids.

# Install

ESMF releases can be found here: http://www.earthsystemmodeling.org/download/data/releases.shtml

# Use

Download ORAS4 or GODAS reanalysis dataset, links can be found here:

https://reanalyses.org/ocean/overview-current-reanalyses

The horizontal and vertical model grid definitions as well as the land-sea mask are also needed, in the case or ORAS4 this is a separate file, for GODAS it is contained within the data file.

Example command regridding GODAS reanalysis to MOM:
```
$ makeic.py GODAS pottmp.2016.nc pottmp.2016.nc pottmp.2016.nc salt.2016.nc \
    MOM ocean_hgrid.nc ocean_vgrid.nc mom_godas_ic.nc --model_mask ocean_mask.nc
```

Notice that since GODAS does not have separate horizontal and vertical grid definition files we just use the pottmp.nc file.

Creating NEMO initial condition from GODAS:
```
$ makeic.py GODAS pottmp.2016.nc pottmp.2016.nc pottmp.2016.nc salt.2016.nc  \
    NEMO coordinates.nc data_1m_potential_temperature_nomask.nc nemo_godas_ic.nc
```

Creating MOM initial conditions from ORAS4:
```
$ ./makeic.py ORAS4 coords_T.nc coords_T.nc thetao_oras4_1m_2014_grid_T.nc so_oras4_1m_2014_grid_T.nc \
    MOM ocean_hgrid.nc ocean_vgrid.nc mom_oras4_ic.nc --model_mask ocean_mask.nc
```

Creating NEMO initial conditions from ORAS4:
```
$ ./makeic.py ORAS4 coords_T.nc coords_T.nc thetao_oras4_1m_2014_grid_T.nc so_oras4_1m_2014_grid_T.nc \
    NEMO coordinates.nc data_1m_potential_temperature_nomask.nc nemo_oras4_ic.nc
```

# How it works

1. The reanalysis/obs dataset is regridded in the vertical to have the same depth and levels as the model grid. Linear interpolation is used for this. If the model is deeper than the obs then the deepest value is extended.

2. In the case of GODAS since the obs dataset is limited latitudinally it is extended to cover the whole globe. This is done based on nearest neighbours.

3. The obs dataset is then regridded onto the model grid using weights calculated with ESMF_RegridWeightGen. Various regridding schemes are supported includeing distance weighted nearest neighbour, bilinear and conservative.

4. The model land sea mask is applied and initial condition written out.

# Limitations

* When using GODAS reanalysis the values at high latitudes are unphysical due to limited observations.
* Only 'cold-start' initial conditions are created consisting of temperature and salt fields. This means that the model will need to be spun up.

# Example output

## MOM IC temperature field based on ORAS4 reanalysis
![Temp from MOM IC based on ORAS4 reanalysis](https://raw.github.com/nicjhan/ocean-ic/master/test_data/MOM_IC_TEMP_ORAS4.png)

## MOM IC salt field based on GODAS reanalysis
![Salt from MOM IC based on GODAS reanalysis](https://raw.github.com/nicjhan/ocean-ic/master/test_data/MOM_IC_SALT_GODAS.png)

Note that because GODAS has a limited domain the salt in the Arctic has been filled with a 'representational value', in this case taken from the Bering Strait.

