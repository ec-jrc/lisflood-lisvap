import os

from global_modules.globals import binding
from tests import reference_nc_paths, check_var_step


def test_e0():
    var = 'e0'
    output_path = binding['PathOut']
    results = []
    output_nc = os.path.join(output_path, var)
    print ' ------------> Reference: {} - Current Output: {}'.format(reference_nc_paths[var], output_nc)
    for step in xrange(1, 15):
        results.append(check_var_step(var, step))

    assert all(results)


def test_es():
    var = 'es'
    output_path = binding['PathOut']
    results = []
    output_nc = os.path.join(output_path, var)
    print ' ------------> Reference: {} - Current Output: {}'.format(reference_nc_paths[var], output_nc)
    for step in xrange(1, 15):
        results.append(check_var_step(var, step))

    assert all(results)


def test_et():
    var = 'et'
    output_path = binding['PathOut']
    results = []
    output_nc = os.path.join(output_path, var)
    print ' ------------> Reference: {} - Current Output: {}'.format(reference_nc_paths[var], output_nc)
    for step in xrange(1, 15):
        results.append(check_var_step(var, step))

    assert all(results)
