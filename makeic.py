#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import netCDF4 as nc

from regridder import regrid

"""
Create ocean model IC based on reanalysis data.
"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('reanalysis_name', help="""
                        Name of src data/grid, must be GODAS or ORAS4""")
    parser.add_argument('reanalysis_hgrid', help='Reanalysis horizontal grid spec file.')
    parser.add_argument('reanalysis_vgrid', help='Reanalysis vertical grid spec file.')
    parser.add_argument('temp_reanalysis_file', help='Temp from reanalysis.')
    parser.add_argument('salt_reanalysis_file', help='Salt from reanalysis.')

    parser.add_argument('model_name', help="""
                        Name of model, must be MOM or NEMO""")
    parser.add_argument('model_hgrid', help='Model horizontal grid spec file.')
    parser.add_argument('model_vgrid', help='Model vertical grid spec file.')
    parser.add_argument('output_file', help='Name of the destination/output file.')
    parser.add_argument('--model_mask', default=None, help='Model land-sea mask file.')
    parser.add_argument('--month', default=1,
                        help="""Which month of the data to use.
                                Assumes datasets containing 12 months.""")
    parser.add_argument('--use_mpi', action='store_true', default=False,
                        help="""Use MPI to when calculating the regridding weights.
                               This will speed up the calculation considerably.""")
    args = parser.parse_args()

    assert args.model_name == 'MOM' or args.model_name == 'NEMO'
    assert args.reanalysis_name == 'GODAS' or args.reanalysis_name == 'ORAS4'

    if args.model_name == 'MOM' and args.model_mask is None:
        print("When using model MOM please provide a mask using --model_mask",
              file=sys.stderr)
        return 1

    if os.path.exists(args.output_file):
        print("Output file {} already exists, ".format(args.output_file) + \
               "please move or delete.", file=sys.stderr)
        return 1

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
        weights = regrid.do_regridding(args.reanalysis_name, args.reanalysis_hgrid,
                                       args.reanalysis_vgrid,
                                       src_file, src_var,
                                       args.model_name, args.model_hgrid,
                                       args.model_vgrid,
                                       args.output_file, dest_var,
                                       args.model_mask, args.month,
                                       weights, args.use_mpi)
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

if __name__ == '__main__':
    sys.exit(main())
