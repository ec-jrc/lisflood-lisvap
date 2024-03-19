"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

from nine import range

import os
import sys

from pyexpat import *
import numpy as np
from pcraster.numpy_operations import pcr2numpy

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../src/')
if os.path.exists(src_dir):
    sys.path.append(src_dir)

from lisvap.utils import LisSettings, FileNamesManager, cdf_flags
from lisvap1 import lisvapexe
from lisvap.utils.readers import readnetcdf, iter_open_netcdf


class TestLis(object):
    reference_files = {
        'efas': {
            'e0': os.path.join(current_dir, 'data/reference/efas/e0_1_15'),
            'es': os.path.join(current_dir, 'data/reference/efas/es_1_15'),
            'et': os.path.join(current_dir, 'data/reference/efas/et_1_15'),
        },
        'efas_1arcmin': {
            'e0': os.path.join(current_dir, 'data/reference/efas_1arcmin/e0_1_15'),
            'es': os.path.join(current_dir, 'data/reference/efas_1arcmin/es_1_15'),
            'et': os.path.join(current_dir, 'data/reference/efas_1arcmin/et_1_15'),
        },
        'efas_1arcmin_6hourly': {
            'e0_202112': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/e0_202112'),
            'es_202112': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/es_202112'),
            'et_202112': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/et_202112'),
            'e0_202201': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/e0_202201'),
            'es_202201': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/es_202201'),
            'et_202201': os.path.join(current_dir, 'data/reference/efas_1arcmin_6hourly/et_202201'),
        },
        'efas_1arcmin_hourly': {
            'e0': os.path.join(current_dir, 'data/reference/efas_1arcmin_hourly/e0'),
            'es': os.path.join(current_dir, 'data/reference/efas_1arcmin_hourly/es'),
            'et': os.path.join(current_dir, 'data/reference/efas_1arcmin_hourly/et'),
        },
        'efas_1arcmin_yearly': {
            'e0': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly/e0'),
            'es': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly/es'),
            'et': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly/et'),
        },
        'efas_1arcmin_yearly_output': {
            'e0_2015': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/e0_2015'),
            'es_2015': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/es_2015'),
            'et_2015': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/et_2015'),
            'e0_2016': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/e0_2016'),
            'es_2016': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/es_2016'),
            'et_2016': os.path.join(current_dir, 'data/reference/efas_1arcmin_yearly_output/et_2016'),
        },
        'efas_1arcmin_360days_calendar': {
            'e0': os.path.join(current_dir, 'data/reference/efas_1arcmin_360days_calendar/e0_1_15'),
            'es': os.path.join(current_dir, 'data/reference/efas_1arcmin_360days_calendar/es_1_15'),
            'et': os.path.join(current_dir, 'data/reference/efas_1arcmin_360days_calendar/et_1_15'),
        },
        'cordex': {
            'e0': os.path.join(current_dir, 'data/reference/cordex/e0_1_15'),
            'et': os.path.join(current_dir, 'data/reference/cordex/et_1_15'),
        },
        'glofas': {
            'e0': os.path.join(current_dir, 'data/reference/glofas/e0'),
        },
    }
    domain = None
    settings_path = None
    atol = 0.01
    max_perc_wrong_large_diff = 0.01
    max_perc_wrong = 0.05
    large_diff_th = atol * 100

    @classmethod
    def setup_class(cls):
        print('\n\n================ Running {} tests ================\n\n'.format(cls.domain.upper()))
        settings = LisSettings(cls.settings_path)
        output_path = settings.binding['PathOut']
        fileManager = FileNamesManager(output_path)
        for var in cls.reference_files:
            output_nc = os.path.join(output_path, var) + '.nc'
            if os.path.exists(output_nc):
                os.remove(output_nc)
        lisvapexe(settings)

    @classmethod
    def teardown_class(cls):
        cdf_flags['all'] = 0
        cdf_flags['steps'] = 0
        cdf_flags['end'] = 0

    @classmethod
    def check_var_step(cls, var, step, variable_file_sufix=''):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        output_nc = os.path.join(output_path, var + variable_file_sufix)
        reference = pcr2numpy(readnetcdf(cls.reference_files[cls.domain][var + variable_file_sufix], step, variable_name=var), -9999)
        current_output = pcr2numpy(readnetcdf(output_nc, step, variable_name=var), -9999)
        same_size = reference.size == current_output.size
        diff_values = np.abs(reference - current_output)

        same_values = np.allclose(diff_values, np.zeros(diff_values.shape), atol=cls.atol)
        all_ok = same_size and same_values

        array_ok = np.isclose(diff_values, np.zeros(diff_values.shape), atol=cls.atol)
        wrong_values_size = array_ok[~array_ok].size

        if not all_ok and wrong_values_size > 0:
            max_diff = np.max(diff_values)
            large_diff = max_diff > cls.large_diff_th
            perc_wrong = float(wrong_values_size * 100) / float(diff_values.size)
            if perc_wrong >= cls.max_perc_wrong or perc_wrong >= cls.max_perc_wrong_large_diff and large_diff:
                print('[ERROR]')
                print('Var: {} - STEP {}: {:3.9f}% of values are different. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff))
                return False
            else:
                print('[OK] {} {}'.format(var, step))
                return True
        else:
            print('[OK] {} {}'.format(var, step))
            return True

    @classmethod
    def netcdf_steps(cls, netfile):
        """
        :param netfile: path to netcdf file
        :return: int , num of steps
        """
        netfile = '{}.{}'.format(netfile, 'nc') if not netfile.endswith('.nc') else netfile
        nf1 = iter_open_netcdf(netfile, 'r')
        t_steps = nf1.variables['time'][:]
        return len(t_steps)

    @classmethod
    def listest(cls, variable, variable_file_sufix=''):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        output_nc = os.path.join(output_path, variable + variable_file_sufix)
        print('\n\n>>> Reference: {} - Current Output: {}'.format(cls.reference_files[cls.domain][variable + variable_file_sufix], output_nc))
        results = []
        numsteps = cls.netcdf_steps(cls.reference_files[cls.domain][variable + variable_file_sufix])
        for step in range(0, numsteps):
            results.append(cls.check_var_step(variable, step, variable_file_sufix))
        assert all(results)
