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

from __future__ import (absolute_import, division, print_function, unicode_literals)

from nine import str, range

import os
from decimal import Decimal

import pcraster
from pcraster.framework.Timeoutput import TimeoutputTimeseries

from pcraster.operations import mapmaximum, catchmenttotal, nominal
from pcraster.framework import report

from . import cdf_flags, LisfloodError
from .tools import valuecell
from .writers import writenet
from .readers import loadmap


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
                    outpoints = valuecell(coord, outpoints)
                else:
                    try:
                        outpoints = loadmap(where)
                    except:
                        msg = '{} is not an existing file'.format(outpoints)
                        raise LisfloodError(msg)

            self.var.Tss[tss] = TimeoutputTimeseries(self.settings.binding[tss], self.var, outpoints, noHeader=self.settings.flags['noheader'])

    def dynamic(self):
        """ dynamic part of the output module
        """

        # ************************************************************
        # ***** WRITING RESULTS: TIME SERIES *************************
        # ************************************************************

        if self.settings.flags['loud']:
            # print the discharge of the first output map loc
            print(" %10.2f" % self.var.Tss["DisTS"].firstout(self.var.ChanQ))

        for tss in self.settings.report_timeseries:
            what = getattr(self.var, self.settings.report_timeseries[tss].output_var)
            how = self.settings.report_timeseries[tss]['operation'][0]
            if how == 'mapmaximum':
                changed = mapmaximum(what)
                what = 'changed'
            if how == 'total':
                changed = catchmenttotal(what * self.var.PixelArea, self.var.Ldd) * self.var.InvUpArea
                what = 'changed'
            self.var.Tss[tss].sample(what)

        # ************************************************************
        # ***** WRITING RESULTS: MAPS   ******************************
        # ************************************************************

        checkifdouble = []  # list to check if map is reported more than once

        for maps in self.settings.report_maps_end:
            what = getattr(self.var, self.settings.report_maps_end[maps].output_var)
            where = self.settings.binding[maps]
            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if self.var.currentTimeStep() == self.var.nrTimeSteps():
                    # if suffix with '.' is part of the filename report with
                    # suffix
                    head, tail = os.path.split(where)
                    if '.' in tail:
                        if self.settings.get_option('writeNetcdf'):
                            writenet(0, what, where, self.var.currentTimeStep(),
                                     self.settings.report_maps_end[maps].standard_name,
                                     self.settings.report_maps_end[maps].output_var,
                                     self.settings.report_maps_end[maps].unit, 'i2',
                                     self.var.calendar_day_start, flag_time=False,
                                     scale_factor=self.settings.report_maps_end[maps].scale_factor,
                                     add_offset=self.settings.report_maps_end[maps].add_offset,
                                     value_min=self.settings.report_maps_end[maps].value_min,
                                     value_max=self.settings.report_maps_end[maps].value_max)
                        else:
                            report(what, where)
                    else:
                        if self.settings.get_option('writeNetcdfStack'):
                            writenet(0, what, where, self.var.currentTimeStep(),
                                     self.settings.report_maps_steps[maps].standard_name,
                                     self.settings.report_maps_steps[maps].output_var,
                                     self.settings.report_maps_steps[maps].unit,
                                     'i2', self.var.calendar_day_start,
                                     scale_factor=self.settings.report_maps_steps[maps].scale_factor,
                                     add_offset=self.settings.report_maps_steps[maps].add_offset,
                                     value_min=self.settings.report_maps_steps[maps].value_min,
                                     value_max=self.settings.report_maps_steps[maps].value_max)
                        else:
                            self.var.report(what, where)

        for maps in self.settings.report_maps_steps:
            what = getattr(self.var, self.settings.report_maps_steps[maps].output_var)
            where = self.settings.binding[maps]
            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list
                if self.var.currentTimeStep() in self.var.ReportSteps:
                    if self.settings.get_option('writeNetcdfStack'):
                        writenet(cdf_flags['steps'], what, where,
                                 self.var.currentTimeStep(),
                                 self.settings.report_maps_steps[maps].standard_name,
                                 self.settings.report_maps_steps[maps].output_var,
                                 self.settings.report_maps_steps[maps].unit,
                                 'i2', self.var.calendar_day_start,
                                 scale_factor=self.settings.report_maps_steps[maps].scale_factor,
                                 add_offset=self.settings.report_maps_steps[maps].add_offset,
                                 value_min=self.settings.report_maps_steps[maps].value_min,
                                 value_max=self.settings.report_maps_steps[maps].value_max)
                    else:
                        self.var.report(what, where)

        for maps in self.settings.report_maps_all:
            # report maps for all timesteps
            what = getattr(self.var, self.settings.report_maps_all[maps].output_var)
            where = self.settings.binding[maps]

            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                if self.settings.get_option('writeNetcdfStack'):
                    writenet(cdf_flags['all'], what, where,
                             self.var.currentTimeStep(),
                             self.settings.report_maps_all[maps].standard_name,
                             self.settings.report_maps_all[maps].output_var,
                             self.settings.report_maps_all[maps].unit, 'i2', self.var.calendar_day_start,
                             scale_factor=self.settings.report_maps_all[maps].scale_factor,
                             add_offset=self.settings.report_maps_all[maps].add_offset,
                             value_min=self.settings.report_maps_all[maps].value_min,
                             value_max=self.settings.report_maps_all[maps].value_max)
                else:
                    self.var.report(what, where)

        # if reportstep than increase the counter
        if self.var.currentTimeStep() in self.var.ReportSteps:
            cdf_flags['steps'] += 1
        # increase the counter for report all maps
        cdf_flags['end'] += 1
        cdf_flags['all'] += 1


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
        if isinstance(idMap, (str, pcraster.pcraster.Field)):
            _idMap = True

        nrRows = self._userModel.nrTimeSteps() - self._userModel.firstTimeStep() + 1

        if _idMap:
            self._spatialId = idMap
            if isinstance(idMap, str):
                self._spatialId = pcraster.readmap(idMap)

            _allowdDataTypes = [pcraster.Nominal, pcraster.pcraster.Ordinal, pcraster.Boolean]
            if self._spatialId.dataType() not in _allowdDataTypes:
                # raise Exception(
                #    "idMap must be of type Nominal, Ordinal or Boolean")
                # changed into creating a nominal map instead of bailing out
                self._spatialId = nominal(self._spatialId)

            if self._spatialId.isSpatial():
                self._maxId, valid = pcraster.pcraster.cellvalue(pcraster.operations.mapmaximum(pcraster.operations.ordinal(self._spatialId)), 1)
            else:
                self._maxId = 1

            # cell indices of the sample locations

            # #self._sampleAddresses = []
            # for cellId in range(1, self._maxId + 1):
            # self._sampleAddresses.append(self._getIndex(cellId))

            self._sampleAddresses = [1 for _ in range(self._maxId)]
            # init with the left/top cell - could also be 0 but then you have to catch it in
            # the sample routine and put an exeption in
            nrCells = pcraster.pcraster.clone().nrRows() * pcraster.pcraster.clone().nrCols()
            for cell in range(1, nrCells + 1):
                if pcraster.pcraster.cellvalue(self._spatialId, cell)[1]:
                    self._sampleAddresses[pcraster.pcraster.cellvalue(self._spatialId, cell)[0] - 1] = cell

            self._spatialIdGiven = True

            nrCols = self._maxId
            self._sampleValues = [[Decimal("NaN")] * nrCols for _ in [0] * nrRows]
        else:
            self._sampleValues = [[Decimal("NaN")] * 1 for _ in [0] * nrRows]

    def firstout(self, expression):
        """
        returns the first cell as output value
        """
        try:
            cell_idx = self._sampleAddresses[0]
            tmp = pcraster.pcraster.areaaverage(pcraster.pcraster.spatial(expression), pcraster.pcraster.spatial(self._spatialId))
            value, valid = pcraster.pcraster.cellvalue(tmp, cell_idx)
            if not valid:
                value = Decimal("NaN")
        except:
            value = Decimal("NaN")
        return value
