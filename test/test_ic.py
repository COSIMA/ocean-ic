
from __future__ import print_function

import pytest
import os
import subprocess as sp
import sh
import netCDF4 as nc
import numpy as np

data_tarball = 'test_data.tar.gz'
data_tarball_url = 'http://s3-ap-southeast-2.amazonaws.com/dp-drop/ocean-ic/test/test_data.tar.gz'

def check_output_grid(model_name, output):

    with nc.Dataset(output) as f:
        if model_name == 'MOM':
            lats = f.variables['GRID_Y_T'][:]
        else:
            assert model_name == 'NEMO'
            lats = f.variables['nav_lat'][:]

    assert np.min(lats) < -78.0
    assert np.max(lats) > 80.0

def check_output_fields(model_name, output):

    with nc.Dataset(output) as f:
        if model_name == 'MOM':
            assert f.variables['temp'].units == 'C' or \
                'celsius' in f.variables['temp'].units.lower()
            assert f.variables['salt'].units == 'psu'

            temp = f.variables['temp'][:]
            salt = f.variables['salt'][:]
        else:
            assert model_name == 'NEMO'
            temp = f.variables['votemper'][:]
            salt = f.variables['vosaline'][:]

    assert np.max(temp) < 40.0
    assert np.min(temp) > -10.0

    assert np.max(salt) < 50.0
    assert np.min(salt) > 0.0

class TestRegrid():

    @pytest.fixture
    def input_dir(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        test_data_dir = os.path.join(test_dir, 'test_data')
        test_data_tarball = os.path.join(test_dir, data_tarball)

        if not os.path.exists(test_data_dir):
            if not os.path.exists(test_data_tarball):
                sh.wget('-P', test_dir, data_tarball_url)
            sh.tar('zxvf', test_data_tarball, '-C', test_dir)

        return os.path.join(test_data_dir, 'input')

    @pytest.fixture
    def output_dir(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        test_data_dir = os.path.join(test_dir, 'test_data')

        return os.path.join(test_data_dir, 'output')


    @pytest.mark.godas
    def test_mom_godas(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'mom_godas_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'GODAS'
        src_temp_file = os.path.join(input_dir, 'pottmp.2016.nc')
        src_salt_file = os.path.join(input_dir, 'salt.2016.nc')
        dest_name = 'MOM'
        dest_data_file = output

        args = [src_name, src_temp_file, src_salt_file,
                dest_name, dest_data_file]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic_simple.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

        check_output_fields('MOM', output)
        check_output_grid('MOM', output)

    @pytest.mark.nemo
    def test_nemo_godas(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'nemo_godas_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'GODAS'
        src_temp_file = os.path.join(input_dir, 'pottmp.2016.nc')
        src_salt_file = os.path.join(input_dir, 'salt.2016.nc')
        dest_name = 'NEMO'
        dest_data_file = output

        args = [src_name, src_temp_file, src_salt_file,
                dest_name, dest_data_file]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic_simple.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

        check_output_fields('NEMO', output)
        check_output_grid('NEMO', output)

    @pytest.mark.pentad
    def test_nemo_godas_pentad(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'nemo_godas_pentad_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'GODAS'
        src_temp_file = os.path.join(input_dir, 'godas.P.20031231.pentad.nc')
        src_salt_file = os.path.join(input_dir, 'godas.P.20031231.pentad.nc')
        dest_name = 'NEMO'
        dest_data_file = output

        args = [src_name, src_temp_file, src_salt_file,
                dest_name, dest_data_file]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic_simple.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

        check_output_fields('NEMO', output)
        check_output_grid('NEMO', output)


    @pytest.mark.oras4
    def test_mom_oras4(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'mom_oras4_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'ORAS4'
        src_temp_file = os.path.join(input_dir, 'thetao_oras4_1m_2014_grid_T.nc')
        src_salt_file = os.path.join(input_dir, 'so_oras4_1m_2014_grid_T.nc')
        dest_name = 'MOM'
        dest_data_file = output

        args = [src_name, src_temp_file, src_salt_file,
                dest_name, dest_data_file]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic_simple.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

        check_output_fields('MOM', output)
        check_output_grid('MOM', output)

    @pytest.mark.nemo
    def test_nemo_oras4(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'nemo_oras4_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'ORAS4'
        src_temp_file = os.path.join(input_dir, 'thetao_oras4_1m_2014_grid_T.nc')
        src_salt_file = os.path.join(input_dir, 'so_oras4_1m_2014_grid_T.nc')
        dest_name = 'NEMO'
        dest_data_file = output

        args = [src_name, src_temp_file, src_salt_file,
                dest_name, dest_data_file]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic_simple.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

        check_output_fields('NEMO', output)
        check_output_grid('NEMO', output)
