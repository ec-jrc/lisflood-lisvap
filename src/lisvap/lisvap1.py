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

__authors__ = "Peter Burek, Johan van der Knijff, Ad de Roo"
__version__ = "0.3.1"
__date__ = "19/04/2019"
__copyright__ = "Copyright 2019, Lisflood Open Source"
__maintainers__ = "Domenico Nappo, Valerio Lorini, Lorenzo Mentaschi"
__status__ = "Development"

import datetime
import sys

from pyexpat import *

from lisvap.utils import LisSettings, TimeProfiler
from lisvap.utils.tools import checkdate, DynamicFrame
from lisvap.lisvapdynamic import LisvapModelDyn
from lisvap.lisvapinitial import LisvapModelIni


class LisvapModel(LisvapModelIni, LisvapModelDyn):
    """ Joining the initial and the dynamic part
        of the Lisflood model
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
    print 'Start date: {} ({}) - End date: {} ({})'.format(step_start, timestep_start, step_end, timestep_end)

    if settings.flags['loud']:
        print '%-6s %10s %11s\n' % ('Step', 'Date', 'ET0')

    lisvap_model = LisvapModel()
    dynfmw = DynamicFrame(lisvap_model, firstTimestep=timestep_start, lastTimeStep=timestep_end)
    dynfmw.run()

    if settings.flags['printtime']:
        tp.report()


def usage():
    """ prints some lines describing how to use this program
        which arguments and parameters it accepts, etc
    """
    print '\n\nLisvapPy - Lisvap (Global) using pcraster Python framework'
    print 'Authors:      ', __authors__
    print 'Mantainers:   ', __maintainers__
    print 'Version:      ', __version__
    print 'Last updated: ', __date__
    print 'Status:       ', __status__
    print """\n
    Arguments list:
    settings.xml     settings file

    -q --quiet       output progression given as .
    -v --veryquiet   no output progression is given
    -l --loud        output progression given as time step, date and discharge
    -c --checkfiles  input maps and stack maps are checked, output for each input map BUT no model run
    -h --noheader    .tss file have no header and start immediately with the time series
    -t --printtime   the computation time for hydrological modules are printed\n
    """
    sys.exit(1)


def headerinfo():
    print 'Lisvap ', __version__, ' ', __date__,
    print """\n
(C) Disaster Risk Management Knowledge Centre
    Joint Research Centre of the European Commission
    Unit E1, I-21020 Ispra (Va), Italy
\n
"""


def main():
    if len(sys.argv) < 2:
        usage()
    settingsxml = sys.argv[1]  # setting.xml file
    lissettings = LisSettings(settingsxml)
    # setting of global flag e.g checking input maps, producing more output information
    if not lissettings.flags['veryquiet'] and not lissettings.flags['quiet']:
        headerinfo()
    lisvapexe(lissettings)


if __name__ == "__main__":
    sys.exit(main())
