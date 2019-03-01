import os

from pyexpat import *

import numpy as np
from pcraster.numpy_operations import pcr2numpy

from global_modules.globals import binding
from global_modules.zusatz import option_binding
from global_modules.add1 import readnetcdf
from lisvap1 import lisvapexe

current_dir = os.path.dirname(__file__)
settings_path = os.path.join(current_dir, 'data/tests_settings.xml')
optionxml = os.path.join(current_dir, 'data/OptionTserieMapsLisvap.xml')
reference_nc_filenames = ['data/e0_1_15', 'data/es_1_15', 'data/et_1_15']
reference_nc_paths = {nc[5:7]: os.path.join(current_dir, nc) for nc in reference_nc_filenames}
atol = 0.01


def setup_module():
    # remove old output files
    option_binding(settings_path, optionxml)
    output_path = binding['PathOut']
    for var in reference_nc_paths:
        output_nc = os.path.join(output_path, var) + '.nc'
        os.remove(output_nc)
    # execute current version of lisvap
    lisvapexe(settings_path, optionxml)


def teardown_module():
    pass


def check_var_step(var, step):
    output_path = binding['PathOut']
    output_nc = os.path.join(output_path, var)
    reference = pcr2numpy(readnetcdf(reference_nc_paths[var], step, variable_name=var), -9999)
    current_output = pcr2numpy(readnetcdf(output_nc, step, variable_name=var), -9999)
    same_size = reference.size == current_output.size
    diff_values = np.abs(reference - current_output)
    same_values = np.allclose(diff_values, np.zeros(diff_values.shape), atol=atol)
    all_ok = same_size and same_values
    array_ok = np.isclose(diff_values, np.zeros(diff_values.shape), atol=atol)
    wrong_values_size = array_ok[~array_ok].size
    perc_wrong = float(wrong_values_size * 100) / float(diff_values.size)
    print '[+] Step: {} - Max diff: {:3.9f} % wrong values: {} ({})'.format(step, np.max(diff_values), wrong_values_size, perc_wrong)
    if not all_ok and wrong_values_size > 0:
        max_diff = np.max(diff_values)
        large_diff = max_diff > 0.02

        if perc_wrong >= 0.05:
            print '[ERROR]'
            print 'Var: {} - STEP {}: {:3.9f}% of values are different. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff)
            return False
        elif perc_wrong >= 0.005 and large_diff:
            print '[WARNING]'
            print 'Var: {} - STEP {}: {:3.9f}% of values have large difference. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff)
            return True if 9998.0 < max_diff <= 9999.09 else False
        else:
            print '[OK] {} {}'.format(var, step)
            return True
    else:
        print '[OK] {} {}'.format(var, step)
        return True
