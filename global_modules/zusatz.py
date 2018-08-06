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