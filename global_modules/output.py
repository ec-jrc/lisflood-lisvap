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

import os

from pcraster.operations import mapmaximum, catchmenttotal
from pcraster.framework import report

from global_modules import cdf_flags
from .add1 import writenet, loadmap, valuecell
# from .globals import cdfFlag
from .zusatz import TimeoutputTimeseries, LisfloodError


class OutputTssMap(object):

    """
    # ************************************************************
    # ***** Output of time series (.tss) and maps*****************
    # ************************************************************
    """

    def __init__(self, out_variable):
        self.var = out_variable
        self.settings = self.var.settings

    def initial(self):
        """ initial part of the output module
        """
        self.settings.binding['1'] = None
        # output for single column eg mapmaximum
        self.var.Tss = {}

        for tss in self.settings.report_timeseries:
            where = self.settings.report_timeseries[tss]['where'][0]
            outpoints = self.settings.binding[where]
            if where in ('1', 'Catchments'):
                pass
            else:
                coord = self.settings.binding[where].split()  # could be gauges, sites, lakeSites etc.
                if len(coord) % 2 == 0:
                    outpoints = valuecell(self.var.MaskMap, coord, outpoints)
                else:
                    try:
                        outpoints = loadmap(where)
                    except:
                        msg = outpoints + ' is not an existing file'
                        raise LisfloodError(msg)

            self.var.Tss[tss] = TimeoutputTimeseries(self.settings.binding[tss], self.var, outpoints, noHeader=self.settings.flags['noheader'])

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
        if not self.settings.options['InitLisfloodwithoutSplit']:

            if self.settings.flags['loud']:
                # print the discharge of the first output map loc
                print " %10.2f" % self.var.Tss["DisTS"].firstout(self.var.ChanQ)

            for tss in self.settings.report_timeseries:
                what = 'self.var.' + self.settings.report_timeseries[tss]['outputVar'][0]
                how = self.settings.report_timeseries[tss]['operation'][0]
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

        for maps in self.settings.report_maps_end:
            # report end maps
            what = 'self.var.' + self.settings.report_maps_end[maps]['outputVar'][0]
            where = self.settings.binding[maps]
            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if self.var.currentTimeStep() == self.var.nrTimeSteps():
                    # if suffix with '.' is part of the filename report with
                    # suffix
                    head, tail = os.path.split(where)
                    if '.' in tail:
                        if self.settings.options['writeNetcdf']:
                            writenet(0, eval(what), where, self.var.currentTimeStep(), maps, self.settings.report_maps_end[maps][
                                     'outputVar'][0], self.settings.report_maps_end[maps]['unit'][0], 'f4', self.var.CalendarDate, flag_time=False)
                        else:
                            report(eval(what), where)
                    else:
                        if self.settings.options['writeNetcdfStack']:
                            writenet(0, eval(what), where, self.var.currentTimeStep(), maps, self.settings.report_maps_steps[
                                     maps]['outputVar'][0], self.settings.report_maps_steps[maps]['unit'][0], 'f4', self.var.CalendarDate)
                        else:
                            self.var.report(eval(what), where)

        for maps in self.settings.report_maps_steps.keys():
            # report reportsteps maps
            what = 'self.var.' + self.settings.report_maps_steps[maps]['outputVar'][0]
            where = self.settings.binding[maps]
            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list
                if self.var.currentTimeStep() in self.var.ReportSteps:
                    if self.settings.options['writeNetcdfStack']:
                        writenet(cdf_flags['steps'],
                                 eval(what),
                                 where,
                                 self.var.currentTimeStep(),
                                 maps,
                                 self.settings.report_maps_steps[maps]['outputVar'][0],
                                 self.settings.report_maps_steps[maps]['unit'][0],
                                 'f4',
                                 self.var.CalendarDate)
                    else:
                        self.var.report(eval(what), where)

        for maps in self.settings.report_maps_all:
            # report maps for all timesteps
            what = 'self.var.' + self.settings.report_maps_all[maps]['outputVar'][0]
            where = self.settings.binding[maps]

            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if self.settings.options['writeNetcdfStack']:
                    writenet(cdf_flags['end'], eval(what), where, self.var.currentTimeStep(), maps, self.settings.report_maps_all[
                             maps]['outputVar'][0], self.settings.report_maps_all[maps]['unit'][0], 'f4', self.var.CalendarDate)
                else:
                    self.var.report(eval(what), where)

        # if reportstep than increase the counter
        if self.var.currentTimeStep() in self.var.ReportSteps:
            cdf_flags['steps'] += 1
        # increase the counter for report all maps
        cdf_flags['end'] += 1
