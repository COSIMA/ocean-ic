# ocean-ic

Create ocean initial conditions by regridding GODAS or ORAS4 reanalysis to MOM or NEMO grids.

# Dependencies

This tool is written in Python and depends a few different Python packages. See section 'Install' below for instructions on how to download all of the Python dependencies. It also depends on
 [ESMF_RegridWeightGen](https://www.earthsystemcog.org/projects/regridweightgen/) program to perform regridding between non-rectilinear grids.

# Install

1. Download and install [Anaconda](https://www.continuum.io/downloads) for your platform.
2. Install ESMF_RegridWeightGen. ESMF releases can be found [here](http://www.earthsystemmodeling.org/download/data/releases.shtml).
3. Install the [git](https://git-scm.com/) revision control system if you don't already have it.
4. Download ocean-ic:
```{bash}
$ git clone --recursive https://github.com/nicjhan/ocean-ic.git
$ cd ocean-ic
```
5. Setup the Anaconda environment. This will download all the necessary Python packages.
```{bash}
$ conda env create -f ocean.yml
$ source activate ocean
```

# Use

Download ORAS4 or GODAS reanalysis dataset, data can be found here:

- GODAS: http://www.esrl.noaa.gov/psd/data/gridded/data.godas.html
- ORAS4: ftp://ftp.icdc.zmaw.de/EASYInit/ORA-S4/monthly_orca1/

For ORAS4 it is also necessary to download the grid definition file at:

- ftp://ftp.icdc.zmaw.de/EASYInit/ORA-S4/orca1_coordinates/

In addition the horizontal and vertical model grid definitions and land-sea mask are also needed. These should be a part of your model installation.

Example command regridding GODAS reanalysis to MOM:
```
$ makeic.py GODAS pottmp.2016.nc pottmp.2016.nc pottmp.2016.nc salt.2016.nc \
    MOM ocean_hgrid.nc ocean_vgrid.nc mom_godas_ic.nc --model_mask ocean_mask.nc
```

Notice that since GODAS does not have horizontal and vertical grid definition files we just use the pottmp.nc file.

Creating NEMO initial condition from GODAS:
```
$ makeic.py GODAS pottmp.2016.nc pottmp.2016.nc pottmp.2016.nc salt.2016.nc  \
    NEMO coordinates.nc data_1m_potential_temperature_nomask.nc nemo_godas_ic.nc
```

Creating MOM initial conditions from ORAS4:
```
$ ./makeic.py ORAS4 coordinates_grid_T.nc coordinates_grid_T.nc thetao_oras4_1m_2014_grid_T.nc so_oras4_1m_2014_grid_T.nc \
    MOM ocean_hgrid.nc ocean_vgrid.nc mom_oras4_ic.nc --model_mask ocean_mask.nc
```

Creating NEMO initial conditions from ORAS4:
```
$ ./makeic.py ORAS4 coordinates_grid_T.nc coordinates_grid_T.nc thetao_oras4_1m_2014_grid_T.nc so_oras4_1m_2014_grid_T.nc \
    NEMO coordinates.nc data_1m_potential_temperature_nomask.nc nemo_oras4_ic.nc
```

Above we're using a NEMO data file, data_1m_potential_temperature_nomask to specify the vertical grid. The levels variable in the NEMO coordinates.nc is incomplete.

# How to use the output

## MOM

Overwrite the output from the tool to the MOM initial condition file in the INPUT directory:

```{bash}
$ cp mom_oras4_ic.nc INPUT/ocean_temp_salt.res.nc
```

## NEMO

Overwrite the output from the tool to the NEMO initial condition file in the model run directory:

```{bash}
$ cp nemo_oras4_ic.nc data_1m_potential_temperature_nomask.nc
$ cp nemo_oras4_ic.nc data_1m_salinity_nomask.nc
```

Then check the following namelist options:

```{fortran}
&namrun        !   parameters of the run
!-----------------------------------------------------------------------
    ln_rstart   = .false.   !  start from rest (F) or from a restart file (T)

&namtsd    !   data : Temperature  & Salinity
!-----------------------------------------------------------------------
!-----------------------------------------------------------------------
!          !  file name                            ! frequency (hours) ! variable  ! time interp. !  clim  ! 'yearly'/ ! weights  ! rotation ! land/sea mask !
!          !                                       !  (if <0  months)  !   name    !   (logical)  !  (T/F) ! 'monthly' ! filename ! pairing  ! filename      !
    sn_tem  = 'data_1m_potential_temperature_nomask',         -1        ,'votemper' ,    .false.    , .true. , 'yearly'   , ''       ,   ''    ,    ''
    sn_sal  = 'data_1m_salinity_nomask'             ,         -1        ,'vosaline' ,    .false.    , .true. , 'yearly'   , ''       ,   ''    ,    ''
    ln_tsd_init   = .true.    !  Initialisation of ocean T & S with T &S input data (T) or not (F)
    ln_tsd_tradmp = .false.   !  damping of ocean T & S toward T &S input data (T) or not (F)

!-----------------------------------------------------------------------
&namtra_dmp    !   tracer: T & S newtonian damping
!-----------------------------------------------------------------------
    ln_tradmp   =  .false.   !  add a damping termn (T) or not (F)
```

Note that nudging / Newtownian damping (ln_tsd_tradmp and ln_tradmp) has been turned off and there is no time interpolation done on the input. The model output should then contain something like:

```
dta_tsd: deallocte T & S arrays as they are only use to initialize the run
```

If you do wish to do nudging / Newtownian damping then the initial condition must contain a time-series. One way to create this is using the [ocean-nudge](https://github.com/nicjhan/ocean-nudge.git) tool.

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

