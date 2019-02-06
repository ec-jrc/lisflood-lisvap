# -------------------------------------------------------------------------
# Name:        additional subroutines
# Purpose:
#
# Author:      burekpe
#
# Created:     26/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------


import xml.dom.minidom
import datetime
from time import *

from pcraster import*
from pcraster.framework import *

from globals import *
from netCDF4 import Dataset

class LisfloodError(Exception):

    """
    the error handling class
    prints out an error
    """

    def __init__(self, msg):
        header = "\n\n ========================== LISFLOOD ERROR =============================\n"
        self._msg = header + msg

    def __str__(self):
        return self._msg

def Calendar(input):
    """ Get date or number of steps from input.

    Get date from input string using one of the available formats or get time step number from input number or string.
    Used to get the date from CalendarDayStart (input) in the settings xml

    :param input: string containing a date in one of the available formats or time step number as number or string
    :rtype: datetime object or float number
    :returns: date as datetime or time step number as float 
    :raises ValueError: stop if input is not a step number AND it is in wrong date format
    """

    # list with all possible input date formats
    DATE_FORMATS = ['%d/%m/%Y %H:%M', '%Y/%m/%d %H:%M', '%d/%m/%Y', '%Y/%m/%d',
                    '%d/%m/%y %H:%M', '%y/%m/%d %H:%M', '%d/%m/%y', '%y/%m/%d',
                    '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d-%m-%Y', '%Y-%m-%d',
                    '%d-%m-%y %H:%M', '%y-%m-%d %H:%M', '%d-%m-%y', '%y-%m-%d',
                    '%d.%m.%Y %H:%M', '%Y.%m.%d %H:%M', '%d-%m-%Y', '%Y.%m.%d',
                    '%d.%m.%y %H:%M', '%y.%m.%d %H:%M', '%d.%m.%y', '%y.%m.%d'
                    ]
    try:
        # try reading step number from number or string
        date = float(input)
        return date
    except:
        # try reading a date in one of available formats
        for date_format in DATE_FORMATS:
            try:
                date = datetime.datetime.strptime(input, date_format)
                return date
            except ValueError:
                pass
        # if cannot read input then stop
        msg = "Wrong step or date format in XML settings file\n" \
              "Input " + str(input)
        raise LisfloodError(msg)
        quit(1)

    return date


def optionBinding(settingsfile, optionxml):
    """ read settings file and returns
    bindings = key and value (filename or value)
    options  = controll of Lisflood to use certain subroutines
    """

    optionSetting = {}
    user = {}
    repTimeserie = {}
    repMaps = {}

    # domopt = xml.dom.minidom.parseString(optionxml)
    domopt = xml.dom.minidom.parse(optionxml)
    dom = xml.dom.minidom.parse(settingsfile)

    # getting all posssible option from the general optionxml
    # and setting them tpo their default value
    optDef = domopt.getElementsByTagName("lfoptions")[0]
    for optset in optDef.getElementsByTagName("setoption"):
        option[optset.attributes['name'].value] = bool(
            int(optset.attributes['default'].value))

        # getting option set in the specific settings file
        # and resetting them to their choice value
    optSet = dom.getElementsByTagName("lfoptions")[0]
    for optset in optSet.getElementsByTagName("setoption"):
        optionSetting[optset.attributes['name'].value] = bool(
            int(optset.attributes['choice'].value))
    for key in optionSetting.keys():
        option[key] = optionSetting[key]

    # reverse the initLisflood option to use it as a restriction for output
    # eg. produce output if not(initLisflood)
    option['nonInit'] = not(option['InitLisflood'])
# -----------------------------------------

    # get all the bindings in the first part of the settingsfile = lfuser
    lfuse = dom.getElementsByTagName("lfuser")[0]
    for userset in lfuse.getElementsByTagName("textvar"):
        user[userset.attributes['name'].value] = str(
            userset.attributes['value'].value)

        # get all the binding in the last part of the settingsfile  = lfbinding
    bind = dom.getElementsByTagName("lfbinding")[0]
    for bindset in bind.getElementsByTagName("textvar"):
        binding[bindset.attributes['name'].value] = str(
            bindset.attributes['value'].value)

        # replace/add the information from lfuser to lfbinding
    for i in binding.keys():
        expr = binding[i]
        while expr.find('$(') > -1:
            a1 = expr.find('$(')
            a2 = expr.find(')')
            try:
                s2 = user[expr[a1 + 2:a2]]
            except KeyError:
                print 'no ', expr[a1 + 2:a2], ' in lfuser defined'
            expr = expr.replace(expr[a1:a2 + 1], s2)
        binding[i] = expr


# ---------------------------------------------
    # Split the string ReportSteps into an int array
    # replace endtime with number
    # replace .. with sequence

    repsteps = user['ReportSteps'].split(',')
    if repsteps[-1] == 'endtime':
        repsteps[-1] = binding['StepEnd']
    jjj = []
    for i in repsteps:
        if '..' in i:
            j = map(int, i.split('..'))
            for jj in xrange(j[0], j[1] + 1):
                jjj.append(jj)
        else:
            jjj.append(i)
    ReportSteps['rep'] = map(int, jjj)
    # maps are reported at these time steps


# -------------------------
    # running through all times series
    reportTimeSerie = domopt.getElementsByTagName("lftime")[0]
    for repTime in reportTimeSerie.getElementsByTagName("setserie"):
        d = {}
        for key in repTime.attributes.keys():
            if key != 'name':
                value = repTime.attributes[key].value
                d[key] = value.split(',')
        key = repTime.attributes['name'].value
        repTimeserie[key] = d
        repOpt = repTimeserie[key]['repoption']
        try:
            restOpt = repTimeserie[key]['restrictoption']
        except:
            # add restricted option if not in already
            repTimeserie[key]['restrictoption'] = ['']
            restOpt = repTimeserie[key]['restrictoption']
        try:
            test = repTimeserie[key]['operation']
        except:
            # add operation if not in already
            repTimeserie[key]['operation'] = ['']

        # sort out if this option is not active
        # put in if one of this option is active
        for i in repOpt:
            for o1key in option.keys():
                if option[o1key]:  # if option is active = 1
                    # print o1key, option[o1key],i
                    if o1key == i:
                        # option is active and time series has this option to select it
                        # now test if there is any restrictions
                        allow = True
                        for j in restOpt:
                            for o2key in option.keys():
                                if o2key == j:
                                    # print o2key, option[o2key],j
                                    if not(option[o2key]):
                                        allow = False
                        if allow:
                            reportTimeSerieAct[key] = repTimeserie[key]

# -------------------------
    # running through all maps

    reportMap = domopt.getElementsByTagName("lfmaps")[0]
    for repMap in reportMap.getElementsByTagName("setmap"):
        d = {}
        for key in repMap.attributes.keys():
            if key != 'name':
                value = repMap.attributes[key].value
                d[key] = value.split(',')
        key = repMap.attributes['name'].value
        repMaps[key] = d
        try:
            repAll = repMaps[key]['all']
        except:
            repMaps[key]['all'] = ['']
            repAll = ['']
        try:
            repSteps = repMaps[key]['steps']
        except:
            repMaps[key]['steps'] = ['']
            repSteps = ['']
        try:
            repEnd = repMaps[key]['end']
        except:
            repMaps[key]['end'] = ['']
            repEnd = ['']
        try:
            restOpt = repMaps[key]['restrictoption']
        except:
            # add restricted option if not in already
            repMaps[key]['restrictoption'] = ['']
            restOpt = repMaps[key]['restrictoption']
        try:
            repUnit = repMaps[key]['unit']
        except:
            repMaps[key]['unit'] = ['-']
        #  -------- All -----------------
        # sort out if this option is not active
        # put in if one of this option is active
        for i in repAll:
            # run through all the output option
            for o1key in option.keys():
                # run through all the options
                if option[o1key]:  # if option is active = 1
                    # print o1key, option[o1key],i
                    if o1key == i:
                        # option is active and time series has this option to select it
                        # now test if there is any restrictions
                        allow = True
                        for j in restOpt:
                            # running through all the restrictions
                            for o2key in option.keys():
                                if (o2key == j) and (not(option[o2key])):
                                    allow = False
                        if allow:
                            reportMapsAll[key] = repMaps[key]

        #  -------- Steps -----------------
        for i in repSteps:
            for o1key in option.keys():
                if option[o1key]:  # if option is active = 1
                    if o1key == i:
                        allow = True
                        for j in restOpt:
                            for o2key in option.keys():
                                if (o2key == j) and (not(option[o2key])):
                                    allow = False
                        if allow:
                            reportMapsSteps[key] = repMaps[key]

        #  -------- End -----------------
        for i in repEnd:
            for o1key in option.keys():
                if option[o1key]:  # if option is active = 1
                    if o1key == i:
                        allow = True
                        for j in restOpt:
                            for o2key in option.keys():
                                if (o2key == j) and (not(option[o2key])):
                                    allow = False
                        if allow:
                            reportMapsEnd[key] = repMaps[key]

    # return option,binding,ReportSteps
    # return option,ReportSteps
    # return ReportSteps
    return


def counted(fn):
    def wrapper(*args, **kwargs):
        wrapper.called+= 1
        return fn(*args, **kwargs)
    wrapper.called= 0
    wrapper.__name__= fn.__name__
    return wrapper

@counted
def checkmap(name, value, map, flagmap, find):
    """ check maps if the fit to the mask map
    """
    s = [name, value]
    if flagmap:
        amap = scalar(defined(MMaskMap))
        try:
            smap = scalar(defined(map))
        except:
            msg = "Map: " + name + " in " + value + " does not fit"
            if name == "LZAvInflowMap":
                msg +="\nMaybe run initial run first"
            raise LisfloodError(msg)

        mvmap = maptotal(smap)
        mv = cellvalue(mvmap, 1, 1)[0]
        s.append(mv)

        less = maptotal(ifthenelse(defined(MMaskMap), amap - smap, scalar(0)))
        s.append(cellvalue(less, 1, 1)[0])
        less = mapminimum(scalar(map))
        s.append(cellvalue(less, 1, 1)[0])
        less = maptotal(scalar(map))
        if mv > 0:
            s.append(cellvalue(less, 1, 1)[0] / mv)
        else:
            s.append('0')
        less = mapmaximum(scalar(map))
        s.append(cellvalue(less, 1, 1)[0])
        if find > 0:
            if find == 2:
                s.append('last_Map_used')
            else:
                s.append('')

    else:
        s.append(0)
        s.append(0)
        s.append(float(map))
        s.append(float(map))
        s.append(float(map))

    if checkmap.called == 1:
        print "%-25s%-40s%11s%11s%11s%11s%11s" %("Name","File/Value","nonMV","MV","min","mean","max")
    print "%-25s%-40s%11i%11i%11.2f%11.2f%11.2f" %(s[0],s[1][-39:],s[2],s[3],s[4],s[5],s[6])
    return

def checkifDate(start,end):
    """ Check simulation start and end dates or timesteps
    
    Check simulation start and end dates/timesteps to be later than begin date (CalendarStartDay).
    If dates are used for binding[start] and binding[end], it substitutes dates with time step numbers.
    
    :param start: start date for model run (# or date as string)
    :param end: end date for model run (# or date as string)
    :returns: modelSteps (modelSteps[0] = intStart 
    modelSteps.append(intEnd)
    """
    # CM: calendar date start (CalendarDayStart)
    begin = Calendar(binding['CalendarDayStart'])

    intStart,strStart = datetoInt(binding[start],True)
    # CM mod
    # CM overwrite date with time step
    binding[start] = intStart
    intEnd,strEnd = datetoInt(binding[end],True)
    # CM mod
    binding[end] = intEnd

    # test if start and end > begin
    if (intStart<0) or (intEnd<0) or ((intEnd-intStart)<0):
        strBegin = begin.strftime("%d/%m/%Y %H:%M")
        msg="Simulation start date and/or simulation end date are wrong or do not match CalendarStartDate!\n"+ \
            "CalendarStartDay: "+strBegin +"\n" + \
            "Simulation start: "+strStart + " - "+str(intStart)+"\n" + \
            "Simulation end: "+strEnd + " - "+str(intEnd)
        raise LisfloodError(msg)
    modelSteps.append(intStart)
    modelSteps.append(intEnd)
    return
def timemeasure(name,loops=0):

    timeMes.append(clock())
    if loops == 0:
        s = name
    else:
        s = name+"_%i" %(loops)
    timeMesString.append(s)
    return


class DynamicFrame(DynamicFramework):

    """Adjusting the def _atStartOfTimeStep defined in DynamicFramework
       for a real quiet output
    """
    rquiet = False
    rtrace = False

    def _atStartOfTimeStep(self, step):
        self._userModel()._setInTimeStep(True)
        if not self.rquiet:
            if not self.rtrace:
                msg = u"#"

            else:
                msg = u"%s<time step=\"%s\">\n" % (self._indentLevel(), step)
            sys.stdout.write(msg)
            sys.stdout.flush()


# replacement of the __init__
# because it takes very long and it produce an error if pixel is at the
# lower left corner

class TimeoutputTimeseries(TimeoutputTimeseries):

    """
    Class to create pcrcalc timeoutput style timeseries
    """

    def __init__(self, tssFilename, model, idMap=None, noHeader=False):
        """

        """

        if not isinstance(tssFilename, str):
            raise Exception(
                "timeseries output filename must be of type string")

        self._outputFilename = tssFilename
        self._maxId = 1
        self._spatialId = None
        self._spatialDatatype = None
        self._spatialIdGiven = False
        self._userModel = model
        self._writeHeader = not noHeader
        # array to store the timestep values
        self._sampleValues = None

        _idMap = False
        if isinstance(idMap, str) or isinstance(idMap, pcraster._pcraster.Field):
            _idMap = True

        nrRows = self._userModel.nrTimeSteps(
        ) - self._userModel.firstTimeStep() + 1

        if _idMap:
            self._spatialId = idMap
            if isinstance(idMap, str):
                self._spatialId = pcraster.readmap(idMap)

            _allowdDataTypes = [
                pcraster.Nominal, pcraster.Ordinal, pcraster.Boolean]
            if self._spatialId.dataType() not in _allowdDataTypes:
                #raise Exception(
                #    "idMap must be of type Nominal, Ordinal or Boolean")
                # changed into creating a nominal map instead of bailing out
                self._spatialId = pcraster.nominal(self._spatialId)

            if self._spatialId.isSpatial():
                self._maxId, valid = pcraster.cellvalue(
                    pcraster.mapmaximum(pcraster.ordinal(self._spatialId)), 1)
            else:
                self._maxId = 1

            # cell indices of the sample locations

            # #self._sampleAddresses = []
            # for cellId in range(1, self._maxId + 1):
            # self._sampleAddresses.append(self._getIndex(cellId))

            self._sampleAddresses = [1 for i in xrange(self._maxId)]
            # init with the left/top cell - could also be 0 but then you have to catch it in
            # the sample routine and put an exeption in
            nrCells = pcraster.clone().nrRows() * pcraster.clone().nrCols()
            for cell in xrange(1, nrCells + 1):
                if (pcraster.cellvalue(self._spatialId, cell)[1]):
                    self._sampleAddresses[
                        pcraster.cellvalue(self._spatialId, cell)[0] - 1] = cell

            self._spatialIdGiven = True

            nrCols = self._maxId
            self._sampleValues = [
                [Decimal("NaN")] * nrCols for _ in [0] * nrRows]
        else:
            self._sampleValues = [[Decimal("NaN")] * 1 for _ in [0] * nrRows]

    def firstout(self,expression):
        """
        returns the first cell as output value
        """
        try:
            cellIndex = self._sampleAddresses[0]
            tmp = pcraster.areaaverage(pcraster.spatial(expression), pcraster.spatial(self._spatialId))
            value, valid = pcraster.cellvalue(tmp, cellIndex)
            if not valid:
               value = Decimal("NaN")
        except:
            value = Decimal("NaN")
        return value
        
        
        
#####################################################################################################################
# TOOLS TO OPEN/READ INPUT FILES ITERATIVELY, IN CASE OF NETWORK TEMPORARILY DOWN
#####################################################################################################################

def iterOpenNetcdf(file_path, error_msg, mode, **kwargs):
    """Wrapper around netCDF4.Dataset function exploiting the iterAccess class to access file_path according to the specified mode"""
    access_function = lambda path: Dataset(path, mode, **kwargs)
    return remoteInputAccess(access_function, file_path, error_msg)


def iterReadPCRasterMap(file_path, error_msg=""):
    """Wrapper around pcraster.readmap function exploiting the iterAccess class to open file_path."""
    return remoteInputAccess(pcraster.readmap, file_path, error_msg)


def iterSetClonePCR(file_path, error_msg=""):
    """Wrapper around pcraster.setclone function exploiting the iterAccess class to access file_path."""
    return remoteInputAccess(pcraster.setclone, file_path, error_msg)


def remoteInputAccess(function, file_path, error_msg):
    """
    Wrapper around the provided file access function.
    It allows re-trying the open/read operation if network is temporarily down.
    Arguments:
        function: function to be called to read/open the file.
        file_path: path of the file to be read/open.
    """
    operating_system="Linux"
    num_trials = 1
    bad_sep = "/" if operating_system == "Windows" else "\\"
    file_path = file_path.replace(bad_sep, os.path.sep)
    root = os.path.sep.join(file_path.split(os.path.sep)[:4])
    while num_trials <= 10:
        try:
            obj = function(file_path)
            if num_trials > 1:
                print("File {0} succesfully accessed after {1} attempts".format(file_path, num_trials))
            num_trials = 10 + 1
        except IOError:
            if os.path.exists(root) and not os.path.exists(file_path):
                raise LisfloodFileError(file_path, error_msg)
            elif num_trials == 10:
                raise Exception("Cannot access file {0}!\nNetwork down for too long OR bad root directory {1}!".format(file_path, root))
            else:
                num_trials += 1
                print("Trying to access file {0}: attempt n. {1}".format(file_path, num_trials))
                xtime.sleep(READ_PAUSE)
    return obj
    
def datetoInt(dateIn,both=False):
    """ Get number of steps between dateIn and CalendarDayStart.
    
    Get the number of steps between dateIn and CalendarDayStart and return it as integer number.
    It can now compute the number of sub-daily steps.
    dateIn can be either a date or a number. If dateIn is a number, it must be the number of steps between
    dateIn and CalendarDayStart.
    
    :param dateIn: date as string or number
    :param both: if true it returns both the number of steps as integer and the input date as string. If false only
    the number of steps as integer is returned
    :return: number of steps as integer and input date as string
    """

    # CM: get reference date to be used with step numbers from 'CalendarDayStart' in Settings.xml file
    date1 = Calendar(dateIn)
    begin = Calendar(binding['CalendarDayStart'])
    # CM: get model time step as float form 'DtSec' in Settings.xml file
    DtSec = float(binding['DtSec'])
    # CM: compute fraction of day corresponding to model time step as float
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    if type(date1) is datetime.datetime:
         str1 = date1.strftime("%d/%m/%Y %H:%M")
         # CM: get total number of seconds corresponding to the time interval between dateIn and CalendarDayStart
         timeinterval_in_sec = int((date1 - begin).total_seconds())
         # CM: get total number of steps between dateIn and CalendarDayStart
         int1 = int(timeinterval_in_sec/DtSec +1)
         # int1 = (date1 - begin).days + 1
    else:
        int1 = int(date1)
        str1 = str(date1)
    if both: return int1,str1
    else: return int1


def inttoDate(intIn,refDate):
    """ Get date corresponding to a number of steps from a reference date.

    Get date corresponding to a number of steps from a reference date and return it as datetime.
    It can now use sub-daily steps.
    intIn is a number of steps from the reference date refDate.

    :param intIn: number of steps as integer
    :param refDate: reference date as datetime
    :return: stepDate: date as datetime corresponding to intIn steps from refDate
    """

    # CM: get model time step as float form 'DtSec' in Settings.xml file
    DtSec = float(binding['DtSec'])
    # CM: compute fraction of day corresponding to model time step as float
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    # CM: compute date corresponding to intIn steps from reference date refDate
    stepDate = refDate + datetime.timedelta(days=(intIn*DtDay))

    return stepDate

