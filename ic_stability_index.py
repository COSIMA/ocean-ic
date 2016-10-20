#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import subprocess as sp
import netCDF4 as nc
import numpy as np
from seawater import eos80

from regridder import regrid

"""
Calculate a 'stability metric' for the IC.

This counts the fraction of cells in a column which need to move to make it
completely stable.
"""

def level_of_first_masked(array):

    assert len(array.shape) == 1

    i = 0
    for i in xrange(len(array)):
        if array.mask[i]:
            break
    return i

def calc_density(temp, salt, levels):

    assert len(temp.shape) == 3
    assert len(salt.shape) == 3
    assert len(levels.shape) == 1

    num_levs = levels.shape[0]
    lats = salt.shape[1]
    lons = salt.shape[2]
    depth = np.vstack(([levels]*lats*lons)).T.reshape(num_levs, lats, lons)

    # Pressure in dbar
    pressure = depth*0.1
    density = eos80.dens(salt, temp, pressure)

    return density


def calc_stability_index(temp, salt, levels):

    density = calc_density(temp, salt, levels)

    lats = salt.shape[1]
    lons = salt.shape[2]
    si_ret = np.zeros((lats, lons))

    # The score for each column is the sum of the difference between the
    # current and sorted column.
    for lat in range(lats):
        for lon in range(lons):
            if hasattr(density, 'mask'):
                lev = level_of_first_masked(density[:, lat, lon])
                if lev == 0:
                    continue
            else:
                lev = density.shape[0]

            si = np.count_nonzero(np.sort(density[:lev, lat, lon]) - density[:lev, lat, lon])
            si = si / float(lev)
            si_ret[lat, lon] = si

    return si_ret

def create_more_stable_ic(temp, salt, levels):
    """
    Sort temp and salt based on density to create a more stable IC.
    """

    density = calc_density(temp, salt, levels)
    lats = salt.shape[1]
    lons = salt.shape[2]

    new_temp = np.copy(temp)
    new_salt = np.copy(salt)

    for lat in range(lats):
        for lon in range(lons):
            if hasattr(density, 'mask'):
                lev = level_of_first_masked(density[:, lat, lon])
                if lev == 0:
                    continue
            else:
                lev = density.shape[0]

            t_col = temp[:lev, lat, lon]
            s_col = salt[:lev, lat, lon]
            d_col = density[:lev, lat, lon]

            new_temp[:lev, lat, lon] = [t for _,t in sorted(zip(d_col,t_col),
                                                            key=lambda x : x[0])]
            new_salt[:lev, lat, lon] = [s for _,s in sorted(zip(d_col,s_col),
                                                            key=lambda x : x[0])]

            si = np.count_nonzero(np.sort(density[:lev, lat, lon]) - density[:lev, lat, lon])

    return new_temp, new_salt


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('temp_ic', help="The initial condition file containing temp")
    parser.add_argument('salt_ic', help="The initial condition file containing salt")
    parser.add_argument('--output_stable', action='store_true',
                        default=False, help="Output a more stable version of the IC.")
    args = parser.parse_args()

    salt_var_names = ['vosaline', 'salt', 'SALT']
    temp_var_names = ['votemper', 'temp', 'TEMP', 'pottmp']
    depth_var_names = ['depth', 'zt', 'ZT', 'AZ_50', 'level']

    with nc.Dataset(args.salt_ic) as f:
        for salt_var in salt_var_names:
            if f.variables.has_key(salt_var):
                salt = f.variables[salt_var][0, :, :, :]
                try:
                    if f.variables[salt_var].units == "kg/kg":
                        salt *= 1000
                except AttributeError, e:
                    pass
                break
        else:
             raise KeyError(salt_var)

    with nc.Dataset(args.temp_ic) as f:
        for temp_var in temp_var_names:
            if f.variables.has_key(temp_var):
                temp = f.variables[temp_var][0, :, :, :]
                try:
                    if f.variables[temp_var].units == "K":
                        temp -= 273.15
                except AttributeError, e:
                    pass
                break
        else:
            raise KeyError(temp_var)

        for d in depth_var_names:
            if f.variables.has_key(d):
                depth = f.variables[d][:]
                break
        else:
            raise KeyError(d)

    si = calc_stability_index(temp, salt, depth)
    lats = salt.shape[1]
    lons = salt.shape[2]

    if args.output_stable:
        new_temp, new_salt = create_more_stable_ic(temp, salt, depth)

        ret = sp.call(['nccopy', '-v', temp_var, args.temp_ic, './more_stable_ic.nc'])
        assert ret == 0
        ret = sp.call(['nccopy', '-v', salt_var, args.salt_ic, './more_stable_ic.nc'])
        assert ret == 0

        with nc.Dataset('./more_stable_ic.nc', 'r+') as f:
            f.variables[temp_var][0, :] = new_temp[:]
            f.variables[salt_var][0, :] = new_salt[:]

    with nc.Dataset('./stability_index.nc', 'w') as f:
        f.createDimension('x', lons)
        f.createDimension('y', lats)
        si_nc = f.createVariable('stability', 'f8', ('y', 'x'))

        si_nc[:] = si[:]


    # Total score is sum of all columns divided by total columns
    print('Average stability metric (high is bad) {}'.format(np.sum(si) / (lats*lons)))

    return 0

if __name__ == '__main__':
    sys.exit(main())
