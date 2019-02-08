import os

import numpy as np
from pcraster.numpy_operations import pcr2numpy

from global_modules.add1lisvap import readnetcdf
from global_modules.globals import binding
from tests import reference_nc_path, atol


def test_output():
    print '\n'
    output_path = binding['PathOut']
    output_e0 = os.path.join(output_path, 'e0.nc')
    results = []
    for step in xrange(1, 10):
        e0_reference = pcr2numpy(readnetcdf(reference_nc_path, step, value='e0'), -9999)
        e0_out = pcr2numpy(readnetcdf(output_e0, step, value='e0'), -9999)
        same_size = e0_reference.size == e0_out.size
        diff_values = np.abs(e0_reference - e0_out)
        same_values = np.allclose(diff_values, np.zeros(diff_values.shape), atol=atol)
        all_ok = same_size and same_values
        if not all_ok:
            array_ok = np.isclose(diff_values, np.zeros(diff_values.shape), atol=atol)
            wrong_values_size = array_ok[array_ok is False].size
            if wrong_values_size > 0:
                max_diff = np.max(diff_values)
                large_diff = max_diff > 2 * 0.01
                perc_wrong = float(wrong_values_size * 100) / float(diff_values.size)
                print 'Step {} ---> Max Diff: {:3.9f}, % Wrong values: {:3.9f} ({})'.format(step, max_diff, perc_wrong, wrong_values_size)
                if perc_wrong >= 0.05:
                    print '[ERROR]'
                    print 'STEP {}: {:3.9f}% of values are different. max diff: {:3.4f}'.format(step, perc_wrong, max_diff)
                    results.append(False)
                elif perc_wrong >= 0.0001 and large_diff:
                    print '[WARNING]'
                    print 'STEP {}: {:3.9f}% of values have large difference. max diff: {:3.4f}'.format(step, perc_wrong, max_diff)
                    results.append(False)
                else:
                    print '[OK] Step: {}'.format(step)
                    results.append(True)
            else:
                print '[OK] Step: {}'.format(step)
                results.append(True)
        else:
            print '[OK] Step: {}'.format(step)
            results.append(True)

    assert all(results)
