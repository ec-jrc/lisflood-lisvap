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
from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import sys

from lisvap import __date__, __version__
from lisvap.utils import LisSettings, TimeProfiler, FileNamesManager, usage
from lisvap.utils.tools import checkdate, DynamicFrame
from lisvap.lisvapdynamic import LisvapModelDyn
from lisvap.lisvapinitial import LisvapModelIni


class LisvapModel(LisvapModelIni, LisvapModelDyn):
    """ Joining the initial and the dynamic part
        of the Lisvap model
    """


def lisvapexe(settings):
    tp = TimeProfiler()
    step_start = settings.binding['StepStart']
    step_end = settings.binding['StepEnd']
    start_date, end_date = datetime.datetime.strptime(step_start, '%d/%m/%Y %H:%M'), datetime.datetime.strptime(step_end, '%d/%m/%Y %H:%M')
    start_date_simulation = datetime.datetime.strptime(settings.binding['CalendarDayStart'], '%d/%m/%Y %H:%M')
    timestep_start = (start_date - start_date_simulation).days + 1
    timestep_end = (end_date - start_date_simulation).days + 1
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
        sys.exit(1)
    settingsxml = sys.argv[1]  # setting.xml file
    lissettings = LisSettings(settingsxml)
    fileManager = FileNamesManager(lissettings.binding.get('PathOut'))
    # setting of global flag e.g checking input maps, producing more output information
    if not lissettings.flags['veryquiet'] and not lissettings.flags['quiet']:
        headerinfo()
    lisvapexe(lissettings)


if __name__ == "__main__":
    sys.exit(main())
