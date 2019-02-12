import os

import numpy as np
from pcraster.numpy_operations import pcr2numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

from global_modules.add1 import readnetcdf
from global_modules.globals import binding
from tests import reference_nc_paths, atol


def test_output():
    print '\n'
    output_path = binding['PathOut']
    results = []
    for var in reference_nc_paths:
        output_nc = os.path.join(output_path, var)
        for step in xrange(1, 10):
            reference = pcr2numpy(readnetcdf(reference_nc_paths[var], step, variable_name=var), -9999)
            current_output = pcr2numpy(readnetcdf(output_nc, step, variable_name=var), -9999)
            same_size = reference.size == current_output.size

            diff_values = np.abs(reference - current_output)

            same_values = np.allclose(diff_values, np.zeros(diff_values.shape), atol=atol)
            print(reference_nc_paths[var], '-', output_nc, ' max diff:', np.max(diff_values))
            all_ok = same_size and same_values
            if not all_ok:
                array_ok = np.isclose(diff_values, np.zeros(diff_values.shape), atol=atol)
                wrong_values_size = array_ok[~array_ok].size
                if wrong_values_size > 0:
                    max_diff = np.max(diff_values)
                    large_diff = max_diff > 0.02
                    perc_wrong = float(wrong_values_size * 100) / float(diff_values.size)
                    print 'Var: {} - Step {} ---> Max Diff: {:3.9f}, % Wrong values: {:3.9f} ({})'.format(var, step, max_diff, perc_wrong, wrong_values_size)
                    if perc_wrong >= 0.05:
                        print '[ERROR]'
                        print 'Var: {} - STEP {}: {:3.9f}% of values are different. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff)
                        results.append(False)
                    elif perc_wrong >= 0.0001 and large_diff:
                        print '[WARNING]'
                        print 'Var: {} - STEP {}: {:3.9f}% of values have large difference. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff)
                        results.append(False)
                    else:
                        print 'Var: {} - [OK] Step: {}'.format(var, step)
                        results.append(True)
                else:
                    print 'Var: {} - [OK] Step: {}'.format(var, step)
                    results.append(True)
            else:
                print 'Var: {} - [OK] Step: {}'.format(var, step)
                results.append(True)

    assert all(results)
