#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
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
__version__ = "Version: 0.02"
__date__ ="12/09/2014"
__copyright__ = "Copyright 2014, The LisfloodPy Project"
__maintainer__ = "Peter Burek"
__status__ = "Development"


#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import datetime

from pyexpat import *
import xml.dom.minidom
from netCDF4 import Dataset
from pcraster import *
from pcraster.framework import *
from Lisvap_initial import *
from Lisvap_dynamic import *


class LisvapModel(LisvapModel_ini, LisvapModel_dyn):
    """ Joining the initial and the dynamic part
        of the Lisflood model
    """


# ==================================================
# ============== LISFLOOD execute ==================
# ==================================================

def Lisvapexe():

    optionBinding(settings, optionxml)
    # read all the possible option for modelling and for generating output
    # read the settingsfile with all information about the catchments(s)
    # and the choosen option for mdelling and output
    bindkey = sorted(binding.keys())

    """
    for key in bindkey:
        try: x = float(binding[key])
        except: s = '\'' + binding[key] + '\''
    """

    StepStart = (binding['StepStart'])
    StepEnd = (binding['StepEnd'])
    start_date, end_date = datetime.datetime.strptime(StepStart, "%d/%m/%Y %H:%M"), datetime.datetime.strptime(StepEnd, "%d/%m/%Y %H:%M")
    start_date_simulation = datetime.datetime.strptime(binding['CalendarDayStart'], "%d/%m/%Y %H:%M")
    timestep_start = (start_date - start_date_simulation).days + 1
    timestep_end = (end_date - start_date_simulation).days + 1
    checkifDate('StepStart', 'StepEnd')
    print 'Start date: {} ({}) - End date: {} ({})'.format(StepStart, timestep_start, StepEnd, timestep_end)
    if Flags['loud']:
        print"%-6s %10s %11s\n" %("Step","Date","ET0"),

    Lisvap = LisvapModel()
    stLisvap = DynamicFrame(Lisvap, firstTimestep=timestep_start, lastTimeStep=timestep_end)
    stLisvap.rquiet = True
    stLisvap.rtrace = False
    stLisvap.run()
    # cProfile.run('stLisflood.run()')
    # python -m cProfile -o  l1.pstats lisf1.py settingsNew3.xml
    # gprof2dot -f pstats l1.pstats | dot -Tpng -o callgraph.png

    if Flags['printtime']:
        print "\n\nTime profiling"
        print "%2s %-17s %10s %8s" %("No","Name","time[s]","%")
        for i in xrange(len(timeMesSum)):
            print "%2i %-17s %10.2f %8.1f"  %(i,timeMesString[i],timeMesSum[i],100 * timeMesSum[i] / timeMesSum[-1])

# ==================================================
# ============== USAGE ==============================
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

   print "Lisvap ",__version__," ",__date__,
   print """
Water balance and flood simulation model for large catchments\n
(C) Institute for Environment and Sustainability
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
    optionxml = os.path.normpath(LF_Path + "/OptionTserieMapsLisvap.xml")

    settings = sys.argv[1]    # setting.xml file

    args = sys.argv[2:]
    globalFlags(args)
    # setting of global flag e.g checking input maps, producing more output information
    if not(Flags['veryquiet']) and not(Flags['quiet']) : headerinfo()
    Lisvapexe()
