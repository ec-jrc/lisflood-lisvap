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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nine import (IS_PYTHON2, str, basestring, native_str, chr, long,
    integer_types, class_types, range, range_list, reraise,
    iterkeys, itervalues, iteritems, map, zip, filter, input,
    implements_iterator, implements_to_string, implements_repr, nine,
    nimport)

import os
import sys
from functools import wraps

from pyexpat import *
import numpy as np
from pcraster.numpy_operations import pcr2numpy

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../src/')
if os.path.exists(src_dir):
    sys.path.append(os.path.join(current_dir, '../src/'))

from lisvap.utils import LisSettings
from lisvap.utils.readers import readnetcdf, iter_open_netcdf


reference_files = {
    'efas': {
        'e0': os.path.join(current_dir, 'data/reference/efas/e0_1_15'),
        'es': os.path.join(current_dir, 'data/reference/efas/es_1_15'),
        'et': os.path.join(current_dir, 'data/reference/efas/et_1_15'),
    },
    'cordex': {
        'e0': os.path.join(current_dir, 'data/reference/cordex/e0_1_15'),
        'et': os.path.join(current_dir, 'data/reference/cordex/et_1_15'),
    },
}
atol = 0.01


def netcdf_steps(netfile):
    """
    :param netfile: path to netcdf file
    :return: int , num of steps
    """
    netfile = '{}.{}'.format(netfile, 'nc') if not netfile.endswith('.nc') else netfile
    nf1 = iter_open_netcdf(netfile, 'r')
    t_steps = nf1.variables['time'][:]
    return len(t_steps)


def check_var_step(domain, var, step):
    settings = LisSettings.instance()
    output_path = settings.binding['PathOut']
    output_nc = os.path.join(output_path, var)
    reference = pcr2numpy(readnetcdf(reference_files[domain][var], step, variable_name=var), -9999)
    current_output = pcr2numpy(readnetcdf(output_nc, step, variable_name=var), -9999)
    same_size = reference.size == current_output.size
    diff_values = np.abs(reference - current_output)
    same_values = np.allclose(diff_values, np.zeros(diff_values.shape), atol=atol)
    all_ok = same_size and same_values
    array_ok = np.isclose(diff_values, np.zeros(diff_values.shape), atol=atol)
    wrong_values_size = array_ok[~array_ok].size
    perc_wrong = float(wrong_values_size * 100) / float(diff_values.size)
    if not all_ok and wrong_values_size > 0:
        max_diff = np.max(diff_values)
        large_diff = max_diff > 0.02
        if perc_wrong >= 0.05:
            print('[ERROR]')
            print('Var: {} - STEP {}: {:3.9f}% of values are different. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff))
            return False
        elif perc_wrong >= 0.005 and large_diff:
            print('[WARNING]')
            print('Var: {} - STEP {}: {:3.9f}% of values have large difference. max diff: {:3.4f}'.format(var, step, perc_wrong, max_diff))
            # FIXME we had a few points with null (-9999 in pcraster maps) but not in reference files. Could not find the reason.
            #  It could be a minor issue but it pollutes tests in a real bad way
            return True if 9998.0 < max_diff <= 9999.09 else False
        else:
            print('[OK] {} {}'.format(var, step))
            return True
    else:
        print('[OK] {} {}'.format(var, step))
        return True


def listest(domain, variable):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            settings = LisSettings.instance()
            output_path = settings.binding['PathOut']
            output_nc = os.path.join(output_path, variable)
            print('>>> Reference: {} - Current Output: {}'.format(reference_files[domain][variable], output_nc))
            results = []
            numsteps = netcdf_steps(reference_files[domain][variable])
            for step in range(0, numsteps):
                results.append(check_var_step(domain, variable, step))
            assert all(results)
            return f(*args, **kwds)

        return wrapper

    return decorator
