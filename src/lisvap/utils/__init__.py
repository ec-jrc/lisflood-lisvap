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

import threading

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
import numpy.ma as ma
from netCDF4 import Dataset
from decimal import *

from .. import __version__, __date__, __status__, __authors__, __maintainers__
from .defaults_options import defaults
from .decorators import cached


__DECIMAL_CASES = 20

getcontext().prec = __DECIMAL_CASES

project_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))

process_time = time.process_time


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
    Thread safe Singleton metaclass to keep single instances by init arguments
    """
    _instances = {}
    _init = {}
    _current = {}
    _lock = threading.Lock()

    def __init__(cls, name, bases, dct):
        cls._init[cls] = dct.get('__init__', None)
        super(Singleton, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs):
        with cls._lock:
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


class LisSettings(metaclass=Singleton):
    printer = pprint.PrettyPrinter(indent=4, width=120)

    def __init__(self, settings_file):
        dom = xml.dom.minidom.parse(settings_file)

        self.settings_path = os.path.normpath(os.path.dirname((os.path.abspath(settings_file))))
        self.flags = self.config_flags()

        user_settings, bindings = self.get_binding(dom)

        self.binding = bindings
        self.options = self.get_options(dom)
        self.unit_conversions = self.get_unit_conversions(dom)
        self.report_steps = self._report_steps(user_settings, bindings)
        self.report_maps_all = self._reported_maps()
        self.set_default_units()
        self.issues_list = []
        self.issues_list_new_issue_identation = '        - '
        self.issues_list_line_break_identation = '\n          '

    def set_default_units(self):
        self.kelvin_units = ['kelvin', 'k']
        # IMPORTANT: Keys and values need to be in lower case
        self.default_units = {
            'tdewmaps': {'is_temperature': True, 'unit': 'degree_celsius', 'defaults': ['c', 'celsius', '°c'], 'conversions': {}},
            'tavgmaps': {'is_temperature': True, 'unit': 'degree_celsius', 'defaults': ['c', 'celsius', '°c'], 'conversions': {}},
            'tminmaps': {'is_temperature': True, 'unit': 'degree_celsius', 'defaults': ['c', 'celsius', '°c'], 'conversions': {}},
            'tmaxmaps': {'is_temperature': True, 'unit': 'degree_celsius', 'defaults': ['c', 'celsius', '°c'], 'conversions': {}},
            'relhmaps': {'is_temperature': False, 'unit': '%', 'defaults': [], 'conversions': {}},
            'windmaps': {'is_temperature': False, 'unit': 'm/s', 'defaults': ['ms-1', 'ms^1', 'mps'], 'conversions': {'km/h': 0.277777778, 'kph': 0.277777778, 'mph': 0.44704}},
            'windumaps': {'is_temperature': False, 'unit': 'm/s', 'defaults': ['ms-1', 'ms^1', 'mps'], 'conversions': {'km/h': 0.277777778, 'kph': 0.277777778, 'mph': 0.44704}},
            'windvmaps': {'is_temperature': False, 'unit': 'm/s', 'defaults': ['ms-1', 'ms^1', 'mps'], 'conversions': {'km/h': 0.277777778, 'kph': 0.277777778, 'mph': 0.44704}},
            'eactmaps': {'is_temperature': False, 'unit': 'hpa', 'defaults': ['mb', 'milibar'], 'conversions': {'kpa': 10.0, 'pa': 0.01, 'b': 1000.0, 'bar': 1000.0, 'psi': 68.95, 'in.hg': 33.86}},
            'psurfmaps': {'is_temperature': False, 'unit': 'pa', 'defaults': ['n/m2', 'nm-2', 'nm^-2'],
                          'conversions': {'kpa': 1000.0, 'hpa': 100.0, 'mb': 100.0, 'milibar': 100.0, 'b': 100000.0, 'bar': 100000.0, 'psi': 6894.76, 'in.hg': 3386.39}},
            'qairmaps': {'is_temperature': False, 'unit': 'kg/kg', 'defaults': ['kilograms/kilograms'], 'conversions': {'g/kg': 1000.0, 'gr/kg': 1000.0, 'grams/kilograms': 1000.0}},
            'rgdmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
            'rnmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
            'rdsmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
            'rdlmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
            'rusmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
            'rulmaps': {'is_temperature': False, 'unit': 'j/m2', 'defaults': ['jm-2', 'j/m^2', 'jm^-2', 'j/m2/d', 'j/m2/day', 'j/d/m2', 'j/day/m2', 'j/m2/24h', 'j/24h/m2'],
                        'conversions': {'j/s/m2': 86400.0, 'w/m2': 86400.0, 'wm-2': 86400.0, 'w/m^2': 86400.0, 'wm^-2': 86400.0}},
        }

    def get_option(self, option_key=''):
        return self.options[option_key.lower()]

    def get_unit_conversion(self, variable_name=''):
        if variable_name is not None:
            var_name = variable_name.lower()
            if var_name in self.unit_conversions:
                return self.unit_conversions[var_name]
        return None

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
report_maps_all: {report_maps_all}
""".format(binding=self.printer.pformat(self.binding), options=self.printer.pformat(self.options),
           report_steps=self.printer.pformat(self.report_steps),
           report_maps_all=self.printer.pformat(self.report_maps_all))
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

    def _reported_maps(self):

        report_maps_all = {}

        # running through all maps
        reportedmaps = self.get_option('reportedmaps')
        for rm in reportedmaps:
            rep_opt_all = rm.all.split(',') if rm.all else []
            restricted_options = rm.restrictoption.split(',') if rm.restrictoption else []

            self._set_active_options(rm, report_maps_all, rep_opt_all, restricted_options)

        return report_maps_all

    @staticmethod
    def config_flags():
        """ read flags - according to the flags the output is adjusted
            quiet, veryquiet, loud, checkfiles, printtime
        """
        flags = {'quiet': False, 'veryquiet': False, 'loud': False,
                 'checkfiles': False, 'printtime': False}

        @cached
        def _flags(argz):

            try:
                opts, arguments = getopt.getopt(argz, 'qvlcht', list(flags.keys()))
            except getopt.GetoptError:
                usage()
#                sys.exit(1)
            else:
                for o, a in opts:
                    for opt in (('-q', '--quiet'), ('-v', '--veryquiet'),
                                ('-l', '--loud'), ('-c', '--checkfiles'),
                                ('-t', '--printtime')):
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

    @staticmethod
    def get_unit_conversions(dom):
        # getting unit conversion values for each variable whose units are
        # different than the ones expected by Lisvap
        lfconversions_elem = dom.getElementsByTagName('lfconversions')
        conversion_setting = {}
        if len(lfconversions_elem) == 0: # No conversions defined
            return conversion_setting
        lfconversions_elem = lfconversions_elem[0]
        for conversionset in lfconversions_elem.getElementsByTagName('setconversion'):
            variable_name = conversionset.attributes['name'].value
            try:
                conversion_factor = conversionset.attributes['value'].value.replace(" ", "")
                if len(conversion_factor) > 0:
                    conversion_setting[str(variable_name).lower()] = float(conversion_factor)
            except Exception as e:
                msg = f'Invalid conversion factor for variable {variable_name} in the settings file.'
                raise LisfloodError(msg)
        return conversion_setting

    def existing_files(self, variable_binding):
        if variable_binding not in self.binding:
            return False
        file_pattern = FileNamesManager.process_file_pattern(self.binding[variable_binding])
        file_list = glob.glob(file_pattern)
        return len(file_list) > 0

    @staticmethod
    def get_netcdf_meteo_variable_name(nc_file_obj):
        # Only one variable must be present in netcdf files
        num_dims = 3 if 'time' in nc_file_obj.variables else 2
        varname = [v for v in nc_file_obj.variables if len(nc_file_obj.variables[v].dimensions) == num_dims][0]
        return varname

    def valid_units(self, variable_binding):
        """
        Validates the first file of a variable to guarantee it contains the correct units.
        Returns (bool, message_str)
        (True, _) if the meteo unit is correct and the message should be ignored
        (False, error_msg) in case the unit is incorrect or undefined and the error_message will contain the reason it is not valid.
        """
        file_pattern = FileNamesManager.process_file_pattern(self.binding[variable_binding])
        file_list = glob.glob(file_pattern)
        for filename in file_list:
            nf1 = Dataset(filename, 'r')
            var_name = self.get_netcdf_meteo_variable_name(nf1)
            var_unit_original = nf1.variables[var_name].units
            nf1.close()
            var_unit = var_unit_original.lower().replace(' ', '')
            default_units_key = variable_binding.lower()
            if default_units_key not in self.default_units:
                return False, f'ERROR: Variable [{variable_binding}] is not available in Lisvap.'
            units_config = self.default_units[default_units_key]
            is_temperature = units_config['is_temperature']
            unit = units_config['unit']
            unit_defaults = units_config['defaults']
            unit_conversions = units_config['conversions']
            option_temperature_kelvin = self.get_option('TemperatureInKelvinFlag')
            if var_unit == unit or var_unit in unit_defaults:
                return True, ''
            if is_temperature and option_temperature_kelvin:
                error_msg = f'ERROR: Variable {variable_binding} have units [{var_unit_original}] and it is expected to have one of {self.kelvin_units}.'
                # If the units are actually in kelvin the error message should be ignored because this expression will return True
                return var_unit in self.kelvin_units, error_msg
            settings_conversion_factor = self.get_unit_conversion(variable_binding)
            error_msg = f'ERROR: Variable {variable_binding} is expected to be in [{unit}] units but it is in [{var_unit_original}] units.'
            if var_unit in unit_conversions:
                conversion_factor = unit_conversions[var_unit]
                if settings_conversion_factor is None: # No conversion factor setup yet
                    error_msg += f'{self.issues_list_line_break_identation}It can be converted to [{unit}] using the conversion factor of [{conversion_factor}]'
                    error_msg += f'{self.issues_list_line_break_identation}Add to the <lfconversions><lfconversions/> section in the settings file:'
                    error_msg += f'{self.issues_list_line_break_identation}    <setconversion name="{variable_binding}" value="{conversion_factor}"/>'
                elif conversion_factor != settings_conversion_factor: # Conversion factor is setup but is wrong
                    error_msg += f'{self.issues_list_line_break_identation}Found in settings an eventually wrong conversion factor of {settings_conversion_factor}'
                    error_msg += f' when it should be {conversion_factor} to convert from [{var_unit_original}] to [{unit}]'
                else: # Conversion factor is setup and corresponds to one of the defined conversions
                    return True, ''
                return False, error_msg
            else: # Unknown units or no conversion factor defined for these units
                if settings_conversion_factor is None: # No conversion factor setup yet
                    error_msg += f'{self.issues_list_line_break_identation}If you are sure this file is correct and want to ignore this validation, please'
                    error_msg += f' setup a conversion factor of 1 for this variable.'
                    error_msg += f'{self.issues_list_line_break_identation}Add to the <lfconversions><lfconversions/> section in the settings file:'
                    error_msg += f'{self.issues_list_line_break_identation}    <setconversion name="{variable_binding}" value="1"/>'
                elif settings_conversion_factor == 1:
                    # Conversion factor exists and is equal to 1 which means no conversion will be applied and lisvap can proceed 
                    return True, ''
                return False, error_msg
        return False, f'ERROR: No file was found for variable {variable_binding} to validate the units.'
    
    def validate_variable(self, variable_binding, unexisting_files_msg=''):
        if not self.existing_files(variable_binding):
            self.issues_list.append(unexisting_files_msg)
        valid_units, error_msg = self.valid_units(variable_binding)
        if not valid_units:
            self.issues_list.append(error_msg)

    def valid(self):
        """
        Validates if the setup in the settings file is correct and coherent.
        Prints the error list and returns FALSE if there were errors or TRUE otherwise.
        """
        self.issues_list = []

        selected_setups = int(self.get_option('EFAS')) + int(self.get_option('GLOFAS')) + int(self.get_option('CORDEX'))
        if selected_setups > 1:
            self.issues_list.append('Only one setup can be selected from: EFAS, GLOFAS or CORDEX')
        elif selected_setups == 0:
            self.issues_list.append('One setup needs to be selected from: EFAS, GLOFAS or CORDEX')
        else:
            # ###############################################
            # Check input variables
            # ###############################################
            if self.get_option('useTAvg'):
                if self.get_option('repTAvgMaps'):
                    self.issues_list.append('Option "useTAvg" cannot be used together with option "repTAvgMaps".')
                else:
                    self.validate_variable('TAvgMaps', 'Option "useTAvg" ON: Missing "TAvgMaps" file(s).')
            else:
                self.validate_variable('TMinMaps', 'Option "useTAvg" OFF: Missing "TMinMaps" file(s).')
                self.validate_variable('TMaxMaps', 'Option "useTAvg" OFF: Missing "TMaxMaps" file(s).')

            if not self.get_option('useWindUVMaps'):
                self.validate_variable('WindMaps', 'Option "useWindUVMaps" OFF: Missing "WindMaps" file(s).')
            else:
                self.validate_variable('WindUMaps', 'Option "useWindUVMaps" ON: Missing "WindUMaps" file(s).')
                self.validate_variable('WindVMaps', 'Option "useWindUVMaps" ON: Missing "WindVMaps" file(s).')

            if not self.get_option('CORDEX'): # CORDEX calculates EAct from PSurf and Qair
                if self.get_option('useTDewMaps'):
                    self.validate_variable('TDewMaps', 'Option "useTDewMaps" ON: Missing "TDewMaps" file(s).')
                elif self.get_option('useRelHumidityMaps'):
                    self.validate_variable('RelHMaps', 'Option "useRelHumidityMaps" ON: Missing "RelHMaps" file(s).')
                else:
                    self.validate_variable('EActMaps', 'Option "useTDewMaps" OFF and "useRelHumidityMaps" OFF: Missing "EActMaps" file(s).')
            # ###############################################
            # Check setup specific input variables
            # ###############################################
            if self.get_option('EFAS'):
                self.validate_variable('RgdMaps', 'EFAS setup: Missing "RgdMaps" file(s).')
            elif self.get_option('GLOFAS'):
                self.validate_variable('RgdMaps', 'GLOFAS setup: Missing "RgdMaps" file(s).')
                self.validate_variable('RNMaps', 'GLOFAS setup: Missing "RNMaps" file(s).')
            elif self.get_option('CORDEX'):
                self.validate_variable('PSurfMaps', 'CORDEX setup: Missing "PSurfMaps" file(s).')
                self.validate_variable('QAirMaps', 'CORDEX setup: Missing "QAirMaps" file(s).')
                self.validate_variable('RdsMaps', 'CORDEX setup: Missing "RdsMaps" file(s).')
                if self.get_unit_conversion('RdsMaps') is None:
                    self.issues_list.append('CORDEX setup: Variable "RdsMaps" is expected to have a conversion factor of 86400.')
                self.validate_variable('RdlMaps', 'CORDEX setup: Missing "RdlMaps" file(s).')
                if self.get_unit_conversion('RdlMaps') is None:
                    self.issues_list.append('CORDEX setup: Variable "RdlMaps" is expected to have a conversion factor of 86400.')
                self.validate_variable('RusMaps', 'CORDEX setup: Missing "RusMaps" file(s).')
                if self.get_unit_conversion('RusMaps') is None:
                    self.issues_list.append('CORDEX setup: Variable "RusMaps" is expected to have a conversion factor of 86400.')
                self.validate_variable('RulMaps', 'CORDEX setup: Missing "RulMaps" file(s).')
                if self.get_unit_conversion('RulMaps') is None:
                    self.issues_list.append('CORDEX setup: Variable "RulMaps" is expected to have a conversion factor of 86400.')
            # ###############################################
            # Check constants
            # ###############################################
            if 'AvSolarConst' not in self.binding:
                self.issues_list.append('Missing "AvSolarConst" parameter.')
            if 'StefBolt' not in self.binding:
                self.issues_list.append('Missing "StefBolt" parameter.')
            if 'Press0' not in self.binding:
                self.issues_list.append('Missing "Press0" parameter.')
            if 'PD' not in self.binding:
                self.issues_list.append('Missing "PD" parameter.')
            if 'AlbedoSoil' not in self.binding:
                self.issues_list.append('Missing "AlbedoSoil" parameter.')
            if 'AlbedoWater' not in self.binding:
                self.issues_list.append('Missing "AlbedoWater" parameter.')
            if 'AlbedoCanopy' not in self.binding:
                self.issues_list.append('Missing "AlbedoCanopy" parameter.')
            if 'FactorSoil' not in self.binding:
                self.issues_list.append('Missing "FactorSoil" parameter.')
            if 'FactorWater' not in self.binding:
                self.issues_list.append('Missing "FactorWater" parameter.')
            if 'FactorCanopy' not in self.binding:
                self.issues_list.append('Missing "FactorCanopy" parameter.')
            # ###############################################
            # Checking output definition
            # ###############################################
            if self.get_option('repE0Maps') and 'E0Maps' not in self.binding:
                self.issues_list.append('OUTPUT: Missing "E0Maps" file path.')
            if self.get_option('repES0Maps') and 'ES0Maps' not in self.binding:
                self.issues_list.append('OUTPUT: Missing "ES0Maps" file path.')
            if self.get_option('repET0Maps') and 'ET0Maps' not in self.binding:
                self.issues_list.append('OUTPUT: Missing "ET0Maps" file path.')
            if self.get_option('repTAvgMaps') and 'TAvgMaps' not in self.binding:
                self.issues_list.append('OUTPUT: Missing "TAvgMaps" file path.')
            if self.get_option('monthlyOutput') and not self.get_option('splitOutput'):
                self.issues_list.append('OUTPUT: If "monthlyOutput" is True, "splitOutput" needs also to be True.')
            # ###############################################
            # Checking Base Maps definition
            # ###############################################
            if not self.existing_files('MaskMap'):
                self.issues_list.append('BaseMap: Missing "MaskMap" file.')
            if not self.existing_files('Dem'):
                self.issues_list.append('BaseMap: Missing "Dem" file.')
            if not self.existing_files('Lat'):
                self.issues_list.append('BaseMap: Missing "Lat" file.')
            # ###############################################
            # Checking TIME-RELATED CONSTANTS
            # ###############################################
            if 'CalendarDayStart' not in self.binding:
                self.issues_list.append('TIME-CONST: Missing "CalendarDayStart" value.')
            if 'DtSec' not in self.binding:
                self.issues_list.append('TIME-CONST: Missing "DtSec" value.')
            if 'StepStart' not in self.binding:
                self.issues_list.append('TIME-CONST: Missing "StepStart" value.')
            if 'StepEnd' not in self.binding:
                self.issues_list.append('TIME-CONST: Missing "StepEnd" value.')
            if 'ReportSteps' not in self.binding:
                self.issues_list.append('TIME-CONST: Missing "ReportSteps" value.')

        if len(self.issues_list) > 0:
            issues_str = '\n'.join(map(lambda s: self.issues_list_new_issue_identation + s, self.issues_list))
            print("""\n\n
LisvapPy - Lisvap (Global)

    Version      : {version}
    Last updated : {date}
    Status       : {status}
    Authors      : {authors}
    Maintainers  : {maintainers}
    
    WARNING: The provided settings file presents some issues.
             For more details refer to the documentation: https://ec-jrc.github.io/lisflood-lisvap/
    
    List of issues: \n{issues}\n
            """.format(version=__version__, date=__date__, status=__status__, authors=__authors__, maintainers=__maintainers__, issues=issues_str))
            return False
        return True


class NetcdfMetadata(metaclass=Singleton):

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


class MaskMapMetadata(metaclass=Singleton):
    """
    Class containing the maskmap and its metadata

    maskmap: The actual mask/clone map (np.array)
    west: Coordinate of west side of raster (decimal)
    north: Coordinate of north side of raster (decimal)
    num_cols: Number of columns of the raster (int)
    num_rows: Number of rows of the raster (int)
    cell_size_x: Size of a cell in the x axis (decimal)
    cell_size_y: Size of a cell in the y axis (decimal)
    """

    @classmethod
    def register(cls, maskmap_filename, west=None, north=None, num_cols=None, num_rows=None, cell_size_x=None, cell_size_y=None):
        return cls(maskmap_filename, west, north, num_cols, num_rows, cell_size_x, cell_size_y)

    def __init__(self, maskmap_filename, west=None, north=None, num_cols=None, num_rows=None, cell_size_x=None, cell_size_y=None):
        self.maskmap_filename = maskmap_filename
        self.maskmap = None
        self._metadata = self._set_metadata(west, north, num_cols, num_rows, cell_size_x, cell_size_y)

    def set_maskmap(self, maskmap):
        self.maskmap = ma.masked_where(np.isnan(maskmap), maskmap)

    def get_maskmap(self):
        assert not self.maskmap is None, 'MaskMapMetadata: Maskmap was not set'
        return self.maskmap

    @staticmethod
    def _set_metadata(west=None, north=None, num_cols=None, num_rows=None, cell_size_x=None, cell_size_y=None):
        decimal_format = '{:.20f}'
        # Definition of cellsize, coordinates of the meteomaps and maskmap
        # need some love for error handling
        return {'x': Decimal(decimal_format.format(west)),
                'y': Decimal(decimal_format.format(north)),
                'col': num_cols,
                'row': num_rows,
                'cell_x': Decimal(decimal_format.format(cell_size_x)),
                'cell_y': Decimal(decimal_format.format(cell_size_y))
        }

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
        cell size x: {cell_size_x}
        cell size y: {cell_size_y}
        num_rows: {num_rows}
        num_cols: {num_cols}
        """.format(west=self._metadata['x'], north=self._metadata['y'],
                   cell_size_x=self._metadata['cell_x'], cell_size_y=self._metadata['cell_y'],
                   num_rows=self._metadata['row'], num_cols=self._metadata['col'])
        return res


class CutMap(tuple, metaclass=Singleton):

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
        cellSizeX = Decimal(decimal_format.format(maskmap_attrs['cell_x']))
        cellSizeY = Decimal(decimal_format.format(maskmap_attrs['cell_y']))
        mask_x = Decimal(decimal_format.format(maskmap_attrs['x']))
        mask_y = Decimal(decimal_format.format(maskmap_attrs['y']))

        if 'lon' in nf1.variables.keys():
            x1 = Decimal(decimal_format.format(nf1.variables['lon'][0]))
            x2 = Decimal(decimal_format.format(nf1.variables['lon'][1]))
            # Detect if the x axis is inverted
            if int(mask_x + cellSizeX) != int(x1):
                x1 = Decimal(decimal_format.format(nf1.variables['lon'][-1]))
                x2 = Decimal(decimal_format.format(nf1.variables['lon'][-2]))
            y1 = Decimal(decimal_format.format(nf1.variables['lat'][0]))
            y2 = Decimal(decimal_format.format(nf1.variables['lat'][1]))
            # Detect if the y axis is inverted
            if int(mask_y - cellSizeY) != int(y1):
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
        round_cellSizeX = round(cellSizeX, 13)
        round_cellSizeY = round(cellSizeY, 13)

        if round_cellSizeX != round_x or round_cellSizeY != round_y:
            raise LisfloodError('Cell size different in maskmap {} ({}, {}) and {} (xinc {}, yinc {})'.format(
                settings.binding['MaskMap'], round_cellSizeX, round_cellSizeY, filename, round_x, round_y)
            )

        half_cell_x = cellSizeX * Decimal(0.5)
        half_cell_y = cellSizeY * Decimal(0.5)
        x = x1 - half_cell_x  # |
        y = y1 + half_cell_y  # | coordinates of the upper left corner of the input file upper left pixel
        cut0 = int(Decimal(decimal_format.format(abs(mask_x - x))) / cellSizeX)
        cut1 = cut0 + maskmap_attrs['col']
        cut2 = int(Decimal(decimal_format.format(abs(mask_y - y))) / cellSizeY)
        cut3 = cut2 + maskmap_attrs['row']
        return cut0, cut1, cut2, cut3  # input data will be sliced using [cut2:cut3, cut0:cut1]

    @property
    def slices(self):
        return slice(self.cuts[2], self.cuts[3]), slice(self.cuts[0], self.cuts[1])


class TimeProfiler(metaclass=Singleton):

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


class FileNamesManager(metaclass=Singleton):

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
    
    def reached_last_file(self, variable_binding):
        current_file_idx, file_list = self.input_files[variable_binding]
        return current_file_idx == len(file_list) - 1


class DynamicModel:

    def __init__(self):
        self._d_nrTimeSteps = 0
        self.currentStep = 0
        self._d_firstTimeStep = 1
        self.inTimeStep = False
        self.inInitial = False
        self.inDynamic = False
        self.silentModelOutput = False

    def initial(self):
        print("Implement 'initial' method")
    
    def dynamic(self):
        print("Implement 'dynamic' method")

    def setQuiet(self, quiet=True):
        """
        Disables the progress display of timesteps.
        """
        self.silentModelOutput = quiet
    
    def _silentModelOutput(self):
        return self.silentModelOutput
    
    def timeSteps(self):
        """
        Return a list of time steps configured
        """
        return range(self.firstTimeStep(), self.nrTimeSteps() + 1)
    
    def nrTimeSteps(self):
        """
        Return the number of time steps
        """
        assert self._d_nrTimeSteps
        return self._d_nrTimeSteps
    
    def currentTimeStep(self):
        """
        Return the current time step in the range from firstTimeStep to nrTimeSteps.
        """
        assert self.currentStep >= 0
        return self.currentStep
    
    def firstTimeStep(self):
        """
        Return first timestep of a model.
        """
        assert self._d_firstTimeStep
        return self._d_firstTimeStep

    def _inDynamic(self):
        return self.inDynamic

    def _inInitial(self):
        return self.inInitial

    def _setInInitial(self, value):
        assert isinstance(value, bool)
        self.inInitial = value
    
    def _setInDynamic(self, value):
        assert isinstance(value, bool)
        self.inDynamic = value
    
    def _inTimeStep(self):
        """
        Returns whether a time step is currently executing.
        """
        return self.inTimeStep
    
    def _setInTimeStep(self, value):
        assert isinstance(value, bool)
        self.inTimeStep = value
    
    
    def _setFirstTimeStep(self, firstTimeStep):
    
        if not isinstance(firstTimeStep, int):
          msg = "first timestep argument (%s) of DynamicFramework must be of type int" % (type(firstTimeStep))
          raise AttributeError(msg)
    
        if firstTimeStep <= 0:
          msg = "first timestep argument (%s) of DynamicFramework must be > 0" % (firstTimeStep)
          raise AttributeError(msg)
    
        if firstTimeStep > self.nrTimeSteps():
          msg = "first timestep argument (%s) of DynamicFramework must be smaller than given last timestep (%s)" % (firstTimeStep, self.nrTimeSteps())
          raise AttributeError(msg)
    
        self._d_firstTimeStep = firstTimeStep
    
    def _setCurrentTimeStep(self, step):
    
        if step <= 0:
          msg = "Current timestep must be > 0"
          raise AttributeError(msg)
    
        if step > self.nrTimeSteps():
          msg = "Current timestep must be <= %d (nrTimeSteps)"
          raise AttributeError(msg)
    
        self.currentStep = step
    
    def _setNrTimeSteps(self, lastTimeStep):
        """
        Set the number of time steps to run.
        """
        if not isinstance(lastTimeStep, int):
          msg = "last timestep argument (%s) of DynamicFramework must be of type int" % (type(lastTimeStep))
          raise AttributeError(msg)
    
        if lastTimeStep <= 0:
          msg = "last timestep argument (%s) of DynamicFramework must be > 0" % (lastTimeStep)
          raise AttributeError(msg)
    
        self._d_nrTimeSteps = lastTimeStep



cdf_flags = Counter({'all': 0, 'steps': 0, 'end': 0})


def usage():
    """ prints some lines describing how to use this program
        which arguments and parameters it accepts, etc
    """
    print(
        """\n\n
LisvapPy - Lisvap (Global)

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
    -t --printtime   the computation time for hydrological modules are printed\n
    """.format(version=__version__, date=__date__, status=__status__, authors=__authors__, maintainers=__maintainers__)
    )
