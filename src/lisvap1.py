# -*- coding: utf-8 -*-

"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.

You may obtain a copy of the Licence at:
https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the Licence for the specific language governing permissions and limitations under the Licence.

#######################################################

  ##       ####  ######  ##     ##    ###    ########
  ##        ##  ##    ## ##     ##   ## ##   ##     ##
  ##        ##  ##       ##     ##  ##   ##  ##     ##
  ##        ##   ######  ##     ## ##     ## ########
  ##        ##        ##  ##   ##  ######### ##
  ##        ##  ##    ##   ## ##   ##     ## ##
  ######## ####  ######     ###    ##     ## ##

#######################################################
"""

import datetime
import sys

from lisvap import __date__, __version__
from lisvap.utils import LisSettings, TimeProfiler, FileNamesManager, usage
from lisvap.utils.tools import checkdate, DynamicFrame, date2calendar, get_calendar_configuration
from lisvap.utils.readers import iter_open_netcdf
from lisvap.lisvapdynamic import LisvapModelDyn
from lisvap.lisvapinitial import LisvapModelIni


class LisvapModel(LisvapModelIni, LisvapModelDyn):
    """ Joining the initial and the dynamic part
        of the Lisvap model
    """


def setup_calendar(settings=None):
    fileManager = FileNamesManager.instance()
    map_for_metadata = ''
    if settings.get_option('useTAvg') and settings.binding.get('TAvgMaps'):
        map_for_metadata = fileManager.get_file_name('TAvgMaps')
    elif settings.get_option('useTDewMaps') and settings.binding.get('TDewMaps'):
        map_for_metadata = fileManager.get_file_name('TDewMaps')
    elif settings.get_option('useRelHumidityMaps') and settings.binding.get('RelHMaps'):
        map_for_metadata = fileManager.get_file_name('RelHMaps')
    elif settings.binding.get('TMinMaps'):
        map_for_metadata = fileManager.get_file_name('TMinMaps')
    nf1 = iter_open_netcdf(map_for_metadata, 'r')
    get_calendar_configuration(nf1, settings)


def lisvapexe(settings):
    setup_calendar(settings)
    tp = TimeProfiler()
    step_start = settings.binding['StepStart']
    step_end = settings.binding['StepEnd']
    timestep_stride = int(settings.binding['DtSec'])
    start_date = date2calendar(datetime.datetime.strptime(step_start, '%d/%m/%Y %H:%M'), settings)
    end_date = date2calendar(datetime.datetime.strptime(step_end, '%d/%m/%Y %H:%M'), settings)
    start_date_simulation = date2calendar(datetime.datetime.strptime(settings.binding['CalendarDayStart'], '%d/%m/%Y %H:%M'), settings)
    timestep_start = int((start_date - start_date_simulation).total_seconds() / timestep_stride) + 1
    timestep_end = int((end_date - start_date_simulation).total_seconds() / timestep_stride) + 1
    checkdate('StepStart', 'StepEnd')
    print('Start date: {} ({}) - End date: {} ({})'.format(step_start, timestep_start, step_end, timestep_end))

    if settings.flags['loud']:
        print('%-6s %10s %11s\n' % ('Step', 'Date', 'ET0'))

    lisvap_model = LisvapModel()
    dynfmw = DynamicFrame(lisvap_model, firstTimestep=timestep_start, lastTimeStep=timestep_end)
    dynfmw.run()

    if settings.flags['printtime']:
        tp.report()


def headerinfo():
    print('Lisvap ', __version__, ' ', __date__,)
    print("""
(C) Disaster Risk Management Knowledge Centre
    Joint Research Centre of the European Commission
    Units E1,D2 I-21020 Ispra (Va), Italy
\n
""")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    settingsxml = sys.argv[1]  # setting.xml file
    lissettings = LisSettings(settingsxml)
    fileManager = FileNamesManager(lissettings.binding.get('PathOut'))
    if not lissettings.valid():
        sys.exit(1)
    # setup_calendar(lissettings)
    # setting of global flag e.g checking input maps, producing more output information
    if not lissettings.flags['veryquiet'] and not lissettings.flags['quiet']:
        headerinfo()
    lisvapexe(lissettings)


if __name__ == "__main__":
    sys.exit(main())
