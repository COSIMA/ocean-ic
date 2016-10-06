#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import netCDF4 as nc

from regridder import regrid

"""
Create ocean model IC based on reanalysis data.
"""

grid_defs_error = \
"""
Grid definitions directory {} not found.
please download it with:
wget http://s3-ap-southeast-2.amazonaws.com/dp-drop/ocean-ic/grid_defs.tar.gz
and unzip into the same directory as this executable.
"""

def grid_defs_dir():
    """
    Get path to directory where MOM, NEMO, GODAS and ORAS4 grid definitions are
    found.
    """

    if getattr(sys, 'frozen', False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(basedir, 'grid_defs')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('reanalysis_name', help="""
                        Name of src data/grid, must be GODAS or ORAS4""")
    parser.add_argument('temp_reanalysis_file', help='Temp from reanalysis.')
    parser.add_argument('salt_reanalysis_file', help='Salt from reanalysis.')

    parser.add_argument('model_name', help="""
                        Name of model, must be MOM or NEMO""")
    parser.add_argument('output_file', help='Name of the destination/output file.')
    parser.add_argument('--month', default=1, type=int,
                        help="""Which month of the data to use.
                                Assumes datasets containing 12 months.""")
    parser.add_argument('--use_mpi', action='store_true', default=False,
                        help="""Use MPI to when calculating the regridding weights.
                               This will speed up the calculation considerably.""")
    args = parser.parse_args()

    assert args.model_name == 'MOM' or args.model_name == 'NEMO'
    assert args.reanalysis_name == 'GODAS' or args.reanalysis_name == 'ORAS4'

    if os.path.exists(args.output_file):
        print("Output file {} already exists, ".format(args.output_file) + \
               "please move or delete.", file=sys.stderr)
        return 1

    # Set up the reanalysis model and grid definitions.
    grid_defs = grid_defs_dir()
    if not os.path.exists(grid_defs):
        print(grid_defs_error.format(grid_defs), file=sys.stderr)
        return 1

    if args.reanalysis_name == 'GODAS':
        reanalysis_hgrids = (os.path.join(grid_defs, 'pottmp.2016.nc'),)
        reanalysis_vgrid = os.path.join(grid_defs, 'pottmp.2016.nc')
    else:
        reanalysis_hgrids = (os.path.join(grid_defs, 'coordinates_grid_T.nc'),
                             os.path.join(grid_defs, 'coordinates_grid_U.nc'),
                             os.path.join(grid_defs, 'coordinates_grid_V.nc'))
        reanalysis_vgrid = os.path.join(grid_defs, 'coordinates_grid_T.nc')

    if args.model_name == 'MOM':
        model_hgrid = os.path.join(grid_defs, 'ocean_hgrid.nc')
        model_vgrid = os.path.join(grid_defs, 'ocean_vgrid.nc')
        model_mask = os.path.join(grid_defs, 'ocean_mask.nc')
    else:
        model_hgrid = os.path.join(grid_defs, 'coordinates.nc')
        model_vgrid = os.path.join(grid_defs, 'data_1m_potential_temperature_nomask.nc')
        model_mask = None

    # Read in temperature and salinity data.
    if args.reanalysis_name == 'ORAS4':
        temp_src_var = 'thetao'
        salt_src_var = 'so'
    else:
        temp_src_var = 'pottmp'
        salt_src_var = 'salt'

    if args.model_name == 'MOM':
        temp_dest_var = 'temp'
        salt_dest_var = 'salt'
    else:
        temp_dest_var = 'votemper'
        salt_dest_var = 'vosaline'

    # Regrid temp and salt, write out to the same file.
    weights = None
    vars_to_regrid = [(args.temp_reanalysis_file, temp_src_var, temp_dest_var),
                      (args.salt_reanalysis_file, salt_src_var, salt_dest_var)]
    for src_file, src_var, dest_var in vars_to_regrid:
        weights = regrid.do_regridding(args.reanalysis_name, reanalysis_hgrids,
                                       reanalysis_vgrid,
                                       src_file, src_var,
                                       args.model_name, model_hgrid,
                                       model_vgrid,
                                       args.output_file, dest_var, dest_mask=model_mask,
                                       month=args.month, regrid_weights=weights,
                                       use_mpi=args.use_mpi, write_ic=True)
        if weights is None:
            return 1

    # May need to scale the salt.
    with nc.Dataset(args.output_file, 'r+') as f:
        for salt_name in ['vosaline', 'salt']:
            try:
                salt_var = f.variables[salt_name]
                if salt_var.units == 'kg/kg':
                    salt_var.units = 'psu'
                    salt_var[:] *= 1000
            except KeyError:
                pass
        for temp_name in ['votemper', 'temp']:
            try:
                temp_var = f.variables[temp_name]
                if temp_var.units == 'K':
                    temp_var.units = 'C'
                    temp_var[:] -= 273.15
            except KeyError:
                pass

if __name__ == '__main__':
    sys.exit(main())
