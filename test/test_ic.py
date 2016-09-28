
from __future__ import print_function

import pytest
import os
import subprocess as sp
import sh

data_tarball = 'test_data.tar.gz'
data_tarball_url = 'http://s3-ap-southeast-2.amazonaws.com/dp-drop/ocean-ic/test/test_data.tar.gz'

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

    def test_mom_godas(self, input_dir, output_dir):

        output = os.path.join(output_dir, 'mom_godas_ic.nc')
        if os.path.exists(output):
            os.remove(output)

        src_name = 'GODAS'
        src_hgrid = os.path.join(input_dir, 'pottmp.2016.nc')
        src_vgrid = os.path.join(input_dir, 'pottmp.2016.nc')
        src_temp_file = os.path.join(input_dir, 'pottmp.2016.nc')
        src_salt_file = os.path.join(input_dir, 'salt.2016.nc')
        dest_name = 'MOM'
        dest_hgrid = os.path.join(input_dir, 'ocean_hgrid.nc')
        dest_vgrid = os.path.join(input_dir, 'ocean_vgrid.nc')
        dest_data_file = output
        dest_mask = os.path.join(input_dir, 'ocean_mask.nc')

        args = [src_name, src_hgrid, src_vgrid, src_temp_file, src_salt_file,
                dest_name, dest_hgrid, dest_vgrid, dest_data_file,
                '--model_mask', dest_mask]

        my_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [os.path.join(my_dir, '../', 'makeic.py')] + args
        ret = sp.call(cmd)
        assert(ret == 0)

        # Check that outputs exist.
        assert(os.path.exists(output))

    def test_nemo_godas(self, input_dir, output_dir):
        pass

    def test_mom_oras4(self, input_dir, output_dir):
        pass

    def test_nemo_oras4(self, input_dir, output_dir):
        pass
