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

# Opt-in performance benchmark: measures the average wall-clock time to produce
# one timestep of evapotranspiration (e0/es/et), by running the real model
# (lisvapexe) over a test domain and dividing the dynamic-loop wall time by the
# number of timesteps the model computed.
#
# This test is SKIPPED by default so it never slows down / flakes the normal
# suite. Enable it explicitly:
#
#     LISVAP_PERF=1 PYTHONPATH=src python -m pytest tests/test_perf_timestep.py -s
#
# Notes:
# - Use -s so the printed per-step report is visible.
# - It is a measurement, not a hard gate: by default it only prints and makes a
#   very loose sanity assertion (a step completes in finite, positive time).
#   Set LISVAP_PERF_MAX_STEP_SECONDS to a number to turn it into a regression
#   gate that fails if the measured wall-clock per step exceeds that budget, e.g.
#     LISVAP_PERF=1 LISVAP_PERF_MAX_STEP_SECONDS=15 PYTHONPATH=src python -m pytest tests/test_perf_timestep.py -s
# - Choose the domain with LISVAP_PERF_DOMAIN (default: efas_1arcmin, the full
#   realistic EFAS grid). Valid values: efas, efas_1arcmin.

import os
import sys
import time

import pytest

# config_flags() in lisvap.utils inspects sys.argv[0:2] for the string 'test' to
# enable test-mode flags; ensure argv satisfies that even under pytest/stdin.
if len(sys.argv) < 2 or 'test' not in ' '.join(sys.argv[:2]):
    sys.argv = ['pytest', 'tests/test_perf_timestep']

current_dir = os.path.dirname(os.path.abspath(__file__))

_DOMAINS = {
    'efas': os.path.join(current_dir, 'data/tests_efas.xml'),
    'efas_1arcmin': os.path.join(current_dir, 'data/tests_efas_1arcmin.xml'),
}

_PERF_ENABLED = os.environ.get('LISVAP_PERF') == '1'


@pytest.mark.skipif(not _PERF_ENABLED,
                    reason='performance benchmark; set LISVAP_PERF=1 to enable')
def test_timestep_throughput():
    import warnings
    warnings.filterwarnings('ignore')

    from lisvap.utils import (
        LisSettings, FileNamesManager, TimeProfiler, MaskMapMetadata, cdf_flags,
    )
    from lisvap1 import lisvapexe

    domain = os.environ.get('LISVAP_PERF_DOMAIN', 'efas_1arcmin')
    assert domain in _DOMAINS, 'LISVAP_PERF_DOMAIN must be one of {}'.format(sorted(_DOMAINS))
    xml = _DOMAINS[domain]

    settings = LisSettings(xml)
    FileNamesManager(settings.binding['PathOut'])
    # Reset per-run state so the step count / profiler reflect only this run.
    TimeProfiler().reset()
    cdf_flags['all'] = 0
    cdf_flags['steps'] = 0
    cdf_flags['end'] = 0
    assert settings.valid(), 'settings did not validate for domain {}'.format(domain)

    t0 = time.perf_counter()
    lisvapexe(settings)
    wall = time.perf_counter() - t0

    tp = TimeProfiler.instance()
    # The dynamic loop tags 'All' exactly once per timestep, so its length is the
    # number of timesteps the model actually computed.
    nsteps = len(tp.times.get('All', []))
    assert nsteps > 0, 'no timesteps were computed'

    shape = MaskMapMetadata.instance().get_maskmap().shape
    per_step = wall / nsteps

    print('\n\n================ per-timestep performance ================')
    print('domain              : {}'.format(domain))
    print('grid shape          : {} ({} cells)'.format(shape, shape[0] * shape[1]))
    print('timesteps           : {}'.format(nsteps))
    print('wall-clock total    : {:8.3f} s'.format(wall))
    print('wall-clock PER STEP : {:8.3f} s   ({:.1f} ms)'.format(per_step, 1000 * per_step))
    print('=========================================================')

    # Loose sanity check by default; strict gate only if a budget is provided.
    assert per_step > 0.0
    budget = os.environ.get('LISVAP_PERF_MAX_STEP_SECONDS')
    if budget is not None:
        budget = float(budget)
        assert per_step <= budget, (
            'per-timestep wall time {:.3f}s exceeds budget {:.3f}s for domain {}'
            .format(per_step, budget, domain))
