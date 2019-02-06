<<<<<<< HEAD
# -------------------------------------------------------------------------
# Name:        globals
# Purpose:
#
# Author:      burekpe
#
# Created:     26/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

import getopt

global binding, option, FlagName, Flags, ReportSteps
global MMaskMap, maskmapAttr, bigmapAttr, cutmap, metadataNCDF

binding = {}
option = {}

reportTimeSerieAct = {}
reportMapsAll = {}
reportMapsSteps = {}
reportMapsEnd = {}

MMaskMap = 0
ReportSteps = {}

maskmapAttr = {}
bigmapAttr = {}
cutmap = [0, 1, 0, 1]
cdfFlag = [0, 0, 0]  # flag for netcdf output for all, steps and end
metadataNCDF = {}

global timeMes,TimeMesString, timeMesSum
timeMes=[]
timeMesString = []  # name of the time measure - filled in dynamic
timeMesSum = []    # time measure of hydrological modules

# ----------------------------------
FlagName = ['quiet', 'veryquiet', 'loud',
            'checkfiles', 'noheader', 'printtime']
Flags = {'quiet': False, 'veryquiet': False, 'loud': False,
         'check': False, 'noheader': False, 'printtime': False}


def globalFlags(arg):
    """ read flags - according to the flags the output is adjusted
        quiet,veryquiet, loud, checkfiles, noheader,printtime
    """
    try:
        opts, args = getopt.getopt(arg, 'qvlcht', FlagName)
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ('-q', '--quiet'):
            Flags['quiet'] = True          # Flag[0]=1
        if o in ('-v', '--veryquiet'):
            Flags['veryquiet'] = True      # Flag[1]=1
        if o in ('-l', '--loud'):
            Flags['loud'] = True  # Loud=True
        if o in ('-c', '--checkfiles'):
            Flags['check'] = True  # Check=True
        if o in ('-h', '--noheader'):
            Flags['noheader'] = True  # NoHeader=True
        if o in ('-t', '--printtime'):
            Flags['printtime'] = True      # Flag[2]=1
=======
# -------------------------------------------------------------------------
# Name:        globals
# Purpose:
#
# Author:      burekpe
#
# Created:     26/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

import getopt

global binding, option, FlagName, Flags, ReportSteps
global MMaskMap, maskmapAttr, bigmapAttr, cutmap, metadataNCDF

binding = {}
option = {}

reportTimeSerieAct = {}
reportMapsAll = {}
reportMapsSteps = {}
reportMapsEnd = {}

MMaskMap = 0
ReportSteps = {}

maskmapAttr = {}
bigmapAttr = {}
cutmap = [0, 1, 0, 1]
cdfFlag = [0, 0, 0]  # flag for netcdf output for all, steps and end
metadataNCDF = {}

global timeMes,TimeMesString, timeMesSum
timeMes=[]
timeMesString = []  # name of the time measure - filled in dynamic
timeMesSum = []    # time measure of hydrological modules

global modelSteps       # CM: list of start and end time step for the model (modelSteps[0] = start; modelSteps[1] = end)
modelSteps=[]
# ----------------------------------
FlagName = ['quiet', 'veryquiet', 'loud',
            'checkfiles', 'noheader', 'printtime']
Flags = {'quiet': False, 'veryquiet': False, 'loud': False,
         'check': False, 'noheader': False, 'printtime': False}


def globalFlags(arg):
    """ read flags - according to the flags the output is adjusted
        quiet,veryquiet, loud, checkfiles, noheader,printtime
    """
    try:
        opts, args = getopt.getopt(arg, 'qvlcht', FlagName)
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ('-q', '--quiet'):
            Flags['quiet'] = True          # Flag[0]=1
        if o in ('-v', '--veryquiet'):
            Flags['veryquiet'] = True      # Flag[1]=1
        if o in ('-l', '--loud'):
            Flags['loud'] = True  # Loud=True
        if o in ('-c', '--checkfiles'):
            Flags['check'] = True  # Check=True
        if o in ('-h', '--noheader'):
            Flags['noheader'] = True  # NoHeader=True
        if o in ('-t', '--printtime'):
            Flags['printtime'] = True      # Flag[2]=1
>>>>>>> origin/correctversion
