#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import netCDF4 as nc
from regridder import regrid

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('reanalysis_name', help="""
                        Name of src data/grid, must be GODAS, ORAS4 or WOA""",
                        choices=['GODAS','ORAS4','WOA'])
    parser.add_argument('reanalysis_hgrid', help='Reanalysis horizontal grid spec file.')
    parser.add_argument('reanalysis_vgrid', help='Reanalysis vertical grid spec file.')
    parser.add_argument('temp_reanalysis_file', help='Temperature file from reanalysis.')
    parser.add_argument('salt_reanalysis_file', help='Salt file from reanalysis.')

    parser.add_argument('model_name', help="""
                        Name of model, must be MOM, MOM1 or NEMO""",
                        choices=['MOM','MOM1','NEMO'])
    parser.add_argument('model_hgrid', help='Model horizontal grid spec file.')
    parser.add_argument('model_vgrid', help='Model vertical grid spec file.')
    parser.add_argument('output_file', help='Name of the destination/output file.')
    parser.add_argument('--model_mask', default=None, help='Model land-sea mask file.')
    parser.add_argument('--month', default=1, type=int,
                        help="""Which month of the data to use.
                                Assumes datasets containing 12 months.""")
    parser.add_argument('--use_mpi', action='store_true', default=False,
                        help="""Use MPI to when calculating the regridding weights.
                               This will speed up the calculation considerably.""")

    parser.add_argument('--mom_version', type=str, default='MOM5',
                    help="""MOM version (e.g., MOM5, MOM6). Only used if model_name is MOM or MOM1. 
                    Defaults to MOM5.""")

    args = parser.parse_args()

    if os.path.exists(args.output_file):
        print("Output file {} already exists, ".format(args.output_file) + \
               "please move or delete.", file=sys.stderr)
        return 1

    temp_vars = {
        "pottemp": {"src": None, "dest": None},
        "contemp": {"src": None, "dest": None}
    }
    salt_vars = {
        "pracsalt": {"src": None, "dest": None},
        "abssalt": {"src": None, "dest": None}
    }
    # Read in temperature and salinity data.
    if args.reanalysis_name == 'ORAS4':
        temp_vars["pottemp"]["src"] = 'thetao'
        salt_vars["pracsalt"]["src"] = 'so'
    elif args.reanalysis_name == 'GODAS':
        temp_vars["pottemp"]["src"] = 'pottmp'
        salt_vars["pracsalt"]["src"] = 'salt'
    elif args.reanalysis_name == 'WOA':
        temp_vars["pottemp"]["src"] = 'potential_temperature'
        temp_vars["contemp"]["src"] = 'conservative_temperature'
        salt_vars["pracsalt"]["src"] = 'practical_salinity'
        salt_vars["abssalt"]["src"] = 'absolute_salinity'

    if 'MOM' in args.model_name:
        # OM2 expects variables conservative temp and practical salt in variables called
        # "temp" and "salt"
        # OM3 expects potential temp and practical salt in variables called "ptemp" and "salt"
        # (by default)
        temp_vars["pottemp"]["dest"] = 'ptemp'
        temp_vars["contemp"]["dest"] = 'temp'
        salt_vars["pracsalt"]["dest"] = 'salt'
        salt_vars["abssalt"]["dest"] = 'asalt'
    else:
        temp_vars["pottemp"]["dest"] = 'votemper'
        salt_vars["pracsalt"]["dest"] = 'vosaline'

    temp_var_to_regrid = [
        (args.temp_reanalysis_file, var["src"], var["dest"]) for _, var in temp_vars.items() if var["src"] is not None
    ]
    salt_var_to_regrid = [
        (args.salt_reanalysis_file, var["src"], var["dest"]) for _, var in salt_vars.items() if var["src"] is not None
    ]
    vars_to_regrid = temp_var_to_regrid + salt_var_to_regrid

    # Regrid temp and salt, write out to the same file.
    weights = None
    for src_file, src_var, dest_var in vars_to_regrid:
        weights = regrid.do_regridding(args.reanalysis_name, (args.reanalysis_hgrid,),
                                       args.reanalysis_vgrid,
                                       src_file, src_var,
                                       args.model_name, args.model_hgrid,
                                       args.model_vgrid,
                                       args.output_file, dest_var, dest_mask=args.model_mask,
                                       month=args.month, regrid_weights=weights,
                                       use_mpi=args.use_mpi, write_ic=True, mom_version=args.mom_version)
        if weights is None:
            return 1
    try:
        os.remove(weights)
    except OSError:
        pass

    # May need to scale the salt.
    with nc.Dataset(args.output_file, 'r+') as f:
        for salt_name in ['vosaline', 'salt', 'asalt']:
            try:
                salt_var = f.variables[salt_name]
                if salt_var.units == 'kg/kg':
                    salt_var.units = 'psu'
                    salt_var[:] *= 1000
            except KeyError:
                pass
        for temp_name in ['votemper', 'temp', 'ptemp']:
            try:
                temp_var = f.variables[temp_name]
                if temp_var.units == 'K':
                    temp_var.units = 'C'
                    temp_var[:] -= 273.15
            except KeyError:
                pass

if __name__ == '__main__':
    sys.exit(main())
