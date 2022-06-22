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

from future.utils import with_metaclass
from nine import (IS_PYTHON2, str, range, map, nine)

import inspect
import os
import copy
import pprint
import sys
import getopt
import time
import glob
import xml.dom.minidom
from collections import Counter, defaultdict

import numpy as np
from netCDF4 import Dataset
from pcraster import pcraster
from decimal import *

from .. import __version__, __date__, __status__, __authors__, __maintainers__
from .defaults_options import defaults
from .decorators import cached


__DECIMAL_CASES = 20

getcontext().prec = __DECIMAL_CASES

project_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))


if not IS_PYTHON2:
    # time.clock is deprecated and will be removed in python 3.8
    process_time = time.process_time
else:
    process_time = time.clock


class LisfloodError(Exception):
    """
    the error handling class
    prints out an error
    """

    def __init__(self, msg):

        self._msg = msg

    def __str__(self):
        return '\n\n ========================== LISFLOOD ERROR ============================= \n{}'.format(self._msg)


class Singleton(type):
    """
    Singleton metaclass to keep single instances by init arguments
    """
    _instances = {}
    _init = {}
    _current = {}

    def __init__(cls, name, bases, dct):
        cls._init[cls] = dct.get('__init__', None)
        super(Singleton, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs):
        init = cls._init[cls]
        if init is not None:
            key = (cls, frozenset(inspect.getcallargs(init, None, *args, **kwargs).items()))
        else:
            key = cls

        if key not in cls._instances:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
        cls._current[cls] = cls._instances[key]
        return cls._instances[key]

    def instance(cls):
        return cls._current[cls]


@nine
class LisSettings(with_metaclass(Singleton)):
    printer = pprint.PrettyPrinter(indent=4, width=120)

    def __init__(self, settings_file):
        dom = xml.dom.minidom.parse(settings_file)

        self.settings_path = os.path.normpath(os.path.dirname((os.path.abspath(settings_file))))
        self.flags = self.config_flags()

        user_settings, bindings = self.get_binding(dom)

        self.binding = bindings
        self.options = self.get_options(dom)
        self.report_steps = self._report_steps(user_settings, bindings)
        self.report_timeseries = self._report_tss()
        self.report_maps_steps, self.report_maps_all, self.report_maps_end = self._reported_maps()

    def get_option(self, option_key=''):
        return self.options[option_key.lower()]

    def get_binding(self, dom):
        binding = {}

        #  built-in user variables
        user = {
            'ProjectDir': project_dir, 'ProjectPath': project_dir,
            'SettingsDir': self.settings_path, 'SettingsPath': self.settings_path,
        }
        lfuse = dom.getElementsByTagName("lfuser")[0]
        for userset in lfuse.getElementsByTagName("textvar"):
            user[userset.attributes['name'].value] = str(userset.attributes['value'].value)
            binding[userset.attributes['name'].value] = str(userset.attributes['value'].value)

        # get all the binding in the last part of the settingsfile  = lfbinding
        bind_elem = dom.getElementsByTagName("lfbinding")[0]
        for textvar_elem in bind_elem.getElementsByTagName("textvar"):
            binding[textvar_elem.attributes['name'].value] = str(textvar_elem.attributes['value'].value)

        # replace/add the information from lfuser to lfbinding
        for i in binding:
            expr = binding[i]
            while expr.find('$(') > -1:
                a1 = expr.find('$(')
                a2 = expr.find(')')
                try:
                    s2 = user[expr[a1 + 2:a2]]
                except KeyError:
                    print('no ', expr[a1 + 2:a2], ' in lfuser defined')
                else:
                    expr = expr.replace(expr[a1:a2 + 1], s2)
            binding[i] = expr
        return user, binding

    def __str__(self):
        res = """
Binding: {binding}
Options: {options}
report_steps: {report_steps}
report_timeseries: {report_timeseries}
report_maps_steps: {report_maps_steps}
report_maps_all: {report_maps_all}
report_maps_end: {report_maps_end}
""".format(binding=self.printer.pformat(self.binding), options=self.printer.pformat(self.options),
           report_steps=self.printer.pformat(self.report_steps), report_timeseries=self.printer.pformat(self.report_timeseries),
           report_maps_steps=self.printer.pformat(self.report_maps_steps), report_maps_all=self.printer.pformat(self.report_maps_all),
           report_maps_end=self.printer.pformat(self.report_maps_end))
        return res

    def _set_active_options(self, obj, reported, report_options, restricted_options):
        key = obj.name
        for rep in report_options:
            if self.get_option(rep):
                # option is set so temporarily allow = True
                allow = True
                # checking that restricted_options are not set
                for ro in restricted_options:
                    if ro.lower() in self.options and not self.options[ro.lower()]:
                        allow = False
                        break
                if allow:
                    reported[key] = obj

    @staticmethod
    def _report_steps(user_settings, bindings):

        res = {}
        repsteps = user_settings['ReportSteps'].split(',')
        if repsteps[-1] == 'endtime':
            repsteps[-1] = bindings['StepEnd']
        jjj = []
        for i in repsteps:
            if '..' in i:
                j = list(map(int, i.split('..')))
                for jj in range(j[0], j[1] + 1):
                    jjj.append(jj)
            else:
                jjj.append(i)
        res['rep'] = list(map(int, jjj))
        return res

    def _report_tss(self):
        report_time_series_act = {}
        # running through all times series
        timeseries = self.get_option('timeseries')
        for ts in timeseries:
            rep_opt = ts.repoption.split(',') if ts.repoption else []
            rest_opt = ts.restrictoption.split(',') if ts.restrictoption else []
            self._set_active_options(ts, report_time_series_act, rep_opt, rest_opt)

        return report_time_series_act

    def _reported_maps(self):

        report_maps_steps = {}
        report_maps_all = {}
        report_maps_end = {}

        # running through all maps
        reportedmaps = self.get_option('reportedmaps')
        for rm in reportedmaps:
            rep_opt_all = rm.all.split(',') if rm.all else []
            rep_opt_steps = rm.steps.split(',') if rm.steps else []
            rep_opt_end = rm.end.split(',') if rm.end else []
            restricted_options = rm.restrictoption.split(',') if rm.restrictoption else []

            self._set_active_options(rm, report_maps_all, rep_opt_all, restricted_options)
            self._set_active_options(rm, report_maps_steps, rep_opt_steps, restricted_options)
            self._set_active_options(rm, report_maps_end, rep_opt_end, restricted_options)

        return report_maps_steps, report_maps_all, report_maps_end

    @staticmethod
    def config_flags():
        """ read flags - according to the flags the output is adjusted
            quiet, veryquiet, loud, checkfiles, noheader, printtime
        """
        flags = {'quiet': False, 'veryquiet': False, 'loud': False,
                 'checkfiles': False, 'noheader': False, 'printtime': False}

        @cached
        def _flags(argz):

            try:
                opts, arguments = getopt.getopt(argz, 'qvlcht', list(flags.keys()))
            except getopt.GetoptError:
                usage()
                sys.exit(1)
            else:
                for o, a in opts:
                    for opt in (('-q', '--quiet'), ('-v', '--veryquiet'),
                                ('-l', '--loud'), ('-c', '--checkfiles'),
                                ('-h', '--noheader'), ('-t', '--printtime')):
                        if o in opt:
                            flags[opt[1].lstrip('--')] = True
                            break
            return flags

        if 'test' in sys.argv[0] or 'test' in sys.argv[1]:
            return flags
        args = sys.argv[2:]
        return _flags(args)

    @staticmethod
    def get_options(dom):
        options = copy.deepcopy(defaults)
        # getting option set in the specific settings file
        # and resetting them to their choice value
        lfoptions_elem = dom.getElementsByTagName("lfoptions")[0]
        option_setting = {}
        for optset in lfoptions_elem.getElementsByTagName("setoption"):
            option_setting[str(optset.attributes['name'].value).lower()] = bool(int(optset.attributes['choice'].value))

        options.update(option_setting)
        return options


@nine
class NetcdfMetadata(with_metaclass(Singleton)):

    @classmethod
    def register(cls, netcdf_file):
        return cls(netcdf_file)

    def __setitem__(self, k, v):
        self._metadata[k] = v

    def __delitem__(self, k):
        del self._metadata[k]

    def __getitem__(self, k):
        return self._metadata.get(k)

    def __iter__(self):
        return iter(self._metadata)

    def __len__(self):
        return len(self._metadata)

    def __contains__(self, k):
        return k in self._metadata

    def __init__(self, netcdf_file):
        self.path = netcdf_file
        self._metadata = self._read_metadata(netcdf_file)

    @staticmethod
    def _read_metadata(nc):
        res = {}
        filename = '{}.{}'.format(os.path.splitext(nc)[0], 'nc')
        if not (os.path.isfile(filename)):
            msg = 'NetCDF file {} does not exist'.format(filename)
            raise LisfloodError(msg)
        nf1 = Dataset(filename, 'r')
        for var in nf1.variables:
            res[var] = nf1.variables[var].__dict__
        nf1.close()
        return res


class MaskMapMetadata(with_metaclass(Singleton)):

    @classmethod
    def register(cls, maskmap):
        return cls(maskmap)

    def __init__(self, maskmap):
        self.maskmap = maskmap
        self._metadata = self._pcr_clone_metadata()

    @staticmethod
    def _pcr_clone_metadata():
        decimal_format = '{:.20f}'
        # Definition of cellsize, coordinates of the meteomaps and maskmap
        # need some love for error handling
        return {'x': Decimal(decimal_format.format(pcraster.clone().west())), 'y': Decimal(decimal_format.format(pcraster.clone().north())),
                'col': pcraster.clone().nrCols(),
                'row': pcraster.clone().nrRows(),
                'cell': Decimal(decimal_format.format(pcraster.clone().cellSize()))}

    def __setitem__(self, k, v):
        self._metadata[k] = v

    def __delitem__(self, k):
        del self._metadata[k]

    def __getitem__(self, k):
        return self._metadata.get(k)

    def __iter__(self):
        return iter(self._metadata)

    def __len__(self):
        return len(self._metadata)

    def __contains__(self, k):
        return k in self._metadata

    def __str__(self):
        res = """
        x - west: {west}
        y - north: {north}
        cell size: {cell_size}
        num_rows: {num_rows}
        num_cols: {num_cols}
        """.format(west=self._metadata['x'], north=self._metadata['y'],
                   cell_size=self._metadata['cell'], num_rows=self._metadata['row'],
                   num_cols=self._metadata['col'])
        return res


class CutMap(tuple, with_metaclass(Singleton)):

    @classmethod
    def register(cls, in_file):
        return cls(in_file)

    def __init__(self, in_file):
        self.path = in_file
        self.cuts = self.get_cuts(in_file)

    @staticmethod
    def get_cuts(in_file):
        decimal_format = '{:.20f}'
        settings = LisSettings.instance()
        filename = '{}.{}'.format(os.path.splitext(in_file)[0], 'nc')
        nf1 = Dataset(filename, 'r')

        maskmap_attrs = MaskMapMetadata.instance()
        cellSize = Decimal(decimal_format.format(maskmap_attrs['cell']))
        mask_x = Decimal(decimal_format.format(maskmap_attrs['x']))
        mask_y = Decimal(decimal_format.format(maskmap_attrs['y']))

        if 'lon' in nf1.variables.keys():
            x1 = Decimal(decimal_format.format(nf1.variables['lon'][0]))
            x2 = Decimal(decimal_format.format(nf1.variables['lon'][1]))
            # Detect if the x axis is inverted
            if int(mask_x + cellSize) != int(x1):
                x1 = Decimal(decimal_format.format(nf1.variables['lon'][-1]))
                x2 = Decimal(decimal_format.format(nf1.variables['lon'][-2]))
            y1 = Decimal(decimal_format.format(nf1.variables['lat'][0]))
            y2 = Decimal(decimal_format.format(nf1.variables['lat'][1]))
            # Detect if the y axis is inverted
            if int(mask_y - cellSize) != int(y1):
                y1 = Decimal(decimal_format.format(nf1.variables['lat'][-1]))
                y2 = Decimal(decimal_format.format(nf1.variables['lat'][-2]))
        else:
            x1 = Decimal(decimal_format.format(nf1.variables['x'][0]))
            x2 = Decimal(decimal_format.format(nf1.variables['x'][1]))
            y1 = Decimal(decimal_format.format(nf1.variables['y'][0]))
            y2 = Decimal(decimal_format.format(nf1.variables['y'][1]))
        nf1.close()

        round_x = round(Decimal(decimal_format.format(abs(x2 - x1))), 13)
        round_y = round(Decimal(decimal_format.format(abs(y2 - y1))), 13)
        round_cellSize = round(cellSize, 13)

        if round_cellSize != round_x or round_cellSize != round_y:
            raise LisfloodError('Cell size different in maskmap {} ({}) and {} (xinc {}, yinc {})'.format(
                settings.binding['MaskMap'], round_cellSize, filename, round_x, round_y)
            )

        half_cell = cellSize * Decimal(0.5)
        x = x1 - half_cell  # |
        y = y1 + half_cell  # | coordinates of the upper left corner of the input file upper left pixel
        cut0 = int(Decimal(decimal_format.format(abs(mask_x - x))) / cellSize)
        cut1 = cut0 + maskmap_attrs['col']
        cut2 = int(Decimal(decimal_format.format(abs(mask_y - y))) / cellSize)
        cut3 = cut2 + maskmap_attrs['row']
        return cut0, cut1, cut2, cut3  # input data will be sliced using [cut2:cut3, cut0:cut1]

    @property
    def slices(self):
        return slice(self.cuts[2], self.cuts[3]), slice(self.cuts[0], self.cuts[1])


class TimeProfiler(with_metaclass(Singleton)):

    def __init__(self):
        self.start = process_time()
        self.times = defaultdict(list)
        self.times_sum = {}

    def reset(self):
        self.__init__()

    def timemeasure(self, name):
        if self.times[name]:
            t = process_time() - self.times[name][-1]
        else:
            t = process_time() - self.start
        self.times[name].append(t)

    def report(self):
        for name in self.times:
            self.times_sum[name] = sum(self.times[name])
        tot = sum(v for v in self.times_sum.values())
        print('\n\nTime profiling')
        print('%-17s %10s %8s' % ('Name', 'time[s]', '%'))
        for name in self.times_sum:
            print("%-17s %10.2f %8.1f" % (name, self.times_sum[name], 100 * self.times_sum[name] / tot))


@nine
class FileNamesManager(with_metaclass(Singleton)):

    def __init__(self, unique_domain=''):
        # Dictionary of pairs (current_file_idx, [file1, file2, ...])
        self.input_files = {}
        self.domain = unique_domain

    @staticmethod
    def process_file_pattern(file_pattern=''):
        new_file_pattern = file_pattern
        is_pattern = 1 in [c in new_file_pattern for c in '*?']
        if not is_pattern and not new_file_pattern.endswith('.nc'):
            new_file_pattern += '*'
        return new_file_pattern

    def get_file_name(self, variable_binding):
        if variable_binding not in self.input_files:
            settings = LisSettings.instance()
            file_pattern = FileNamesManager.process_file_pattern(settings.binding[variable_binding])
            current_file_idx = 0
            self.input_files[variable_binding] = (current_file_idx, sorted(glob.glob(file_pattern)))
        current_file_idx, file_list = self.input_files[variable_binding]
        return file_list[current_file_idx]

    def next(self, variable_binding):
        current_file_idx, file_list = self.input_files[variable_binding]
        new_file_idx = min(max(0, len(file_list)-1), current_file_idx+1)
        self.input_files[variable_binding] = (new_file_idx, file_list)


cdf_flags = Counter({'all': 0, 'steps': 0, 'end': 0})


def usage():
    """ prints some lines describing how to use this program
        which arguments and parameters it accepts, etc
    """
    print(
        """\n\n
LisvapPy - Lisvap (Global) using pcraster Python framework

    Version      : {version}
    Last updated : {date}
    Status       : {status}
    Authors      : {authors}
    Maintainers  : {maintainers}

    Arguments list:

    settings.xml     settings file

    -q --quiet       output progression given as .
    -v --veryquiet   no output progression is given
    -l --loud        output progression given as time step, date and discharge
    -c --checkfiles  input maps and stack maps are checked, output for each input map BUT no model run
    -h --noheader    .tss file have no header and start immediately with the time series
    -t --printtime   the computation time for hydrological modules are printed\n
    """.format(version=__version__, date=__date__, status=__status__, authors=__authors__, maintainers=__maintainers__)
    )
