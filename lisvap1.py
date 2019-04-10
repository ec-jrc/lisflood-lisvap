"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

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
__version__ = "Version: 0.2"
__date__ = "12/04/2019"
__copyright__ = "Copyright 2019, Lisflood Open Source"
__maintainer__ = "Domenico Nappo, Valerio Lorini"
__status__ = "Development"

import datetime
import os
import sys

from pyexpat import *

from global_modules import LisSettings, TimeProfiler
from global_modules.zusatz import checkifDate, DynamicFrame
from Lisvap_dynamic import LisvapModelDyn
from Lisvap_initial import LisvapModelIni


class LisvapModel(LisvapModelIni, LisvapModelDyn):
    """ Joining the initial and the dynamic part
        of the Lisflood model
    """

# ==================================================
# ============== LISFLOOD execute ==================
# ==================================================


def lisvapexe(settings):
    tp = TimeProfiler()
    step_start = settings.binding['StepStart']
    step_end = settings.binding['StepEnd']
    start_date, end_date = datetime.datetime.strptime(step_start, '%d/%m/%Y %H:%M'), datetime.datetime.strptime(step_end, '%d/%m/%Y %H:%M')
    start_date_simulation = datetime.datetime.strptime(settings.binding['CalendarDayStart'], '%d/%m/%Y %H:%M')
    timestep_start = (start_date - start_date_simulation).days + 1
    timestep_end = (end_date - start_date_simulation).days + 1
    checkifDate('StepStart', 'StepEnd')
    print 'Start date: {} ({}) - End date: {} ({})'.format(step_start, timestep_start, step_end, timestep_end)

    if settings.flags['loud']:
        print '%-6s %10s %11s\n' % ('Step', 'Date', 'ET0')

    Lisvap = LisvapModel()
    stLisvap = DynamicFrame(Lisvap, firstTimestep=timestep_start, lastTimeStep=timestep_end)
    stLisvap.rquiet = True
    stLisvap.rtrace = False
    stLisvap.run()
    # cProfile.run('stLisflood.run()')
    # python -m cProfile -o  l1.pstats lisf1.py settingsNew3.xml
    # gprof2dot -f pstats l1.pstats | dot -Tpng -o callgraph.png
    # TODO check profile results with snakeviz

    if settings.flags['printtime']:
        tp.report()

# ==================================================
# ============== USAGE =============================
# ==================================================


def usage():
    """ prints some lines describing how to use this program
        which arguments and parameters it accepts, etc
    """
    print 'LisvapPy - Lisvap (Global) using pcraster Python framework'
    print 'Authors: ', __authors__
    print 'Version: ', __version__
    print 'Date: ', __date__
    print 'Status: ', __status__
    print """
    Arguments list:
    settings.xml     settings file

    -q --quiet       output progression given as .
    -v --veryquiet   no output progression is given
    -l --loud        output progression given as time step, date and discharge
    -c --check       input maps and stack maps are checked, output for each input map BUT no model run
    -h --noheader    .tss file have no header and start immediately with the time series
    -t --printtime   the computation time for hydrological modules are printed
    """
    sys.exit(1)


def headerinfo():
    print "Lisvap ", __version__, " ", __date__,
    print """
Water balance and flood simulation model for large catchments\n
(C) Disaster Risk Management Knowledge Centre
    Joint Research Centre of the European Commission
    TP122, I-21020 Ispra (Va), Italy\n"""


# ==================================================
# ============== MAIN ==============================
# ==================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        usage()

    LF_Path = os.path.dirname(sys.argv[0])
    LF_Path = os.path.abspath(LF_Path)
    optionxml = os.path.normpath(LF_Path + '/OptionTserieMapsLisvap.xml')
    settingsxml = sys.argv[1]  # setting.xml file
    lissettings = LisSettings(settingsxml, optionxml)
    # setting of global flag e.g checking input maps, producing more output information
    if not lissettings.flags['veryquiet'] and not lissettings.flags['quiet']:
        headerinfo()
    lisvapexe(lissettings)
