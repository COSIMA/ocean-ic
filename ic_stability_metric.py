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

Counting the tendency for parcels to move up (or down) the water column.
"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('temp_ic', help="The initial condition file containing temp")
    parser.add_argument('salt_ic', help="The initial condition file containing salt")
    args = parser.parse_args()

    with nc.Dataset(args.salt_ic) as f:
        salt = f.variables['vosaline'][0, :, :, :]

    with nc.Dataset(args.temp_ic) as f:
        temp = f.variables['votemper'][0, :, :, :]
        tmp = f.variables['depth'][:]

        levels = tmp.shape[0]
        lats = salt.shape[1]
        lons = salt.shape[2]
        depth = np.vstack(([tmp]*lats*lons)).T.reshape(levels, lats, lons)

    f = nc.Dataset('./stability_index.nc', 'w')
    f.createDimension('x', lons)
    f.createDimension('y', lats)
    si_nc = f.createVariable('stability', 'f8', ('y', 'x'))

    # Pressure in dbar
    pressure = depth*0.1
    density = eos80.dens(salt, temp, pressure)

    # The score for each column is the sum of the difference between the
    # current and sorted column.
    accum = 0
    for lat in range(lats):
        for lon in range(lons):
            si = np.sum(abs(np.sort(density[:, lat, lon]) - \
                                density[:, lat, lon]))
            si = si / float(density.shape[0])
            si_nc[lat, lon] = si
            accum += si

    f.close()

    # Total score is sum of all columns divided by total columns
    print('Average stability metric (high is bad) {}'.format(accum / (lats*lons)))

    return 0

if __name__ == '__main__':
    sys.exit(main())
