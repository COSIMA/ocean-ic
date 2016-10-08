#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import subprocess as sp
import netCDF4 as nc

from regridder import regrid

"""
Calculate a 'stability metric' for the IC.

Do this by just counting the parcels that want to move up the water column.
"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('ic', help="The initial condition file."
    args = parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
