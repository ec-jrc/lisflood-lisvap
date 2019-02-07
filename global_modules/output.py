# -------------------------------------------------------------------------
# Name:        Output module
# Purpose:
#
# Author:      burekpe
#
# Created:     29.03.2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

from pcraster import*
from pcraster.framework import *
import sys
import os
import string
import math

from global_modules.globals import *
from global_modules.add1 import *


class outputTssMap(object):

    """
    # ************************************************************
    # ***** Output of time series (.tss) and maps*****************
    # ************************************************************
    """

    def __init__(self, out_variable):
        self.var = out_variable

    def initial(self):
        """ initial part of the output module
        """
        #binding['Catchments'] = self.var.Catchments
        binding['1'] = None
        # output for single column eg mapmaximum

        self.var.Tss = {}

        for tss in reportTimeSerieAct.keys():
            where = reportTimeSerieAct[tss]['where'][0]
            outpoints = binding[where]
            if where == "1":
                pass
            elif where == "Catchments":
                pass
            else:
                coord = binding[where].split()  # could be gauges, sites, lakeSites etc.
                if len(coord) % 2 == 0:
                    outpoints = valuecell(self.var.MaskMap, coord, outpoints)
                else:
                    try:
                        outpoints = loadmap(where)
                    except:
                        msg = outpoints + " is not an existing file"
                        raise LisfloodError(msg)

            self.var.Tss[tss] = TimeoutputTimeseries(binding[tss], self.var, outpoints, noHeader=Flags['noheader'])


    def dynamic(self):
        """ dynamic part of the output module
        """

        # ************************************************************
        # ***** WRITING RESULTS: TIME SERIES *************************
        # ************************************************************

        # xxx=catchmenttotal(self.var.SurfaceRunForest * self.var.PixelArea, self.var.Ldd) * self.var.InvUpArea
        # self.var.Tss['DisTS'].sample(xxx)
        # self.report(self.Precipitation,binding['TaMaps'])

        # if fast init than without time series
        if not(option['InitLisfloodwithoutSplit']):

            if Flags['loud']:
                # print the discharge of the first output map loc
                print " %10.2f"  %self.var.Tss["DisTS"].firstout(self.var.ChanQ)

            for tss in reportTimeSerieAct.keys():
                what = 'self.var.' + reportTimeSerieAct[tss]['outputVar'][0]
                how = reportTimeSerieAct[tss]['operation'][0]
                if how == 'mapmaximum':
                    changed = mapmaximum(eval(what))
                    what = 'changed'
                if how == 'total':
                    changed = catchmenttotal(eval(what) * self.var.PixelArea, self.var.Ldd) * self.var.InvUpArea
                    what = 'changed'
                self.var.Tss[tss].sample(eval(what))

        # ************************************************************
        # ***** WRITING RESULTS: MAPS   ******************************
        # ************************************************************

        checkifdouble = []  # list to check if map is reported more than once

        for maps in reportMapsEnd.keys():
            # report end maps
            what = 'self.var.' + reportMapsEnd[maps]['outputVar'][0]
            where = binding[maps]
            if not(where in checkifdouble):
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if self.var.currentTimeStep() == self.var.nrTimeSteps():
                    # if suffix with '.' is part of the filename report with
                    # suffix
                    head, tail = os.path.split(where)
                    if '.' in tail:
                        if option['writeNetcdf']:
                            #print 'writeNetcdf'
                            writenet(0, eval(what), where, self.var.currentTimeStep(), maps, reportMapsEnd[maps][
                                     'outputVar'][0], reportMapsEnd[maps]['unit'][0], 'f4', self.var.CalendarDate, flagTime=False)
                        else:
                            report(eval(what), where)
                    else:
                        if option['writeNetcdfStack']:
                            #print 'writenetcdfStack'
                            writenet(0, eval(what), where, self.var.currentTimeStep(), maps, reportMapsSteps[
                                     maps]['outputVar'][0], reportMapsSteps[maps]['unit'][0], 'f4', self.var.CalendarDate)
                        else:
                            self.var.report(eval(what), where)

        for maps in reportMapsSteps.keys():
            # report reportsteps maps
            what = 'self.var.' + reportMapsSteps[maps]['outputVar'][0]
            where = binding[maps]
            if not(where in checkifdouble):
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list
                if self.var.currentTimeStep() in self.var.ReportSteps:
                    if option['writeNetcdfStack']:
                        #print 'writenetstack1'
                        writenet(cdfFlag[1], eval(what), where, self.var.currentTimeStep(), maps, reportMapsSteps[
                                 maps]['outputVar'][0], reportMapsSteps[maps]['unit'][0], 'f4', self.var.CalendarDate)
                    else:
                        self.var.report(eval(what), where)

        for maps in reportMapsAll.keys():
            # report maps for all timesteps
            what = 'self.var.' + reportMapsAll[maps]['outputVar'][0]
            where = binding[maps]
            if not(where in checkifdouble):
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if option['writeNetcdfStack']:
                    #print 'writenetcdfstack2',self.var.currentTimeStep(),what
                    writenet(cdfFlag[2], eval(what), where, self.var.currentTimeStep(), maps, reportMapsAll[
                             maps]['outputVar'][0], reportMapsAll[maps]['unit'][0], 'f4', self.var.CalendarDate)
                    
                else:
                    self.var.report(eval(what), where)

        # if reportstep than increase the counter
        if self.var.currentTimeStep() in self.var.ReportSteps:
            cdfFlag[1] += 1
        # increase the counter for report all maps
        cdfFlag[2] += 1
