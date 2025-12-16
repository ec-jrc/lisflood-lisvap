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
from decimal import Decimal

import numpy as np

from . import cdf_flags, LisfloodError, MaskMapMetadata
from .writers import writenet
from .readers import loadmap


class OutputMap(object):

    """
    # ************************************************************
    # ***** Output of time series maps ***************************
    # ************************************************************
    """

    def __init__(self, out_variable):
        self.var = out_variable
        self.settings = self.var.settings

    def initial(self):
        """ initial part of the output module
        """
        pass

    def dynamic(self):
        """ dynamic part of the output module
        """

        # ************************************************************
        # ***** WRITING RESULTS: MAPS   ******************************
        # ************************************************************

        checkifdouble = []  # list to check if map is reported more than once

        data_type = 'i2'

        for maps in self.settings.report_maps_all:
            flag_time=True
            current_output_index = cdf_flags['all']
            current_report_map = self.settings.report_maps_all[maps]
            # report maps for all timesteps
            what = getattr(self.var, current_report_map.output_var)
            where = self.settings.binding[maps]

            if where not in checkifdouble:
                checkifdouble.append(where)
                # checks if saved at same place, if no: add to list

                writenet(current_output_index, what, where,
                         self.var.currentTimeStep(),
                         current_report_map.standard_name,
                         current_report_map.output_var,
                         current_report_map.unit, data_type,
                         self.var.calendar_day_start, flag_time=flag_time,
                         scale_factor=current_report_map.scale_factor,
                         add_offset=current_report_map.add_offset,
                         value_min=current_report_map.value_min,
                         value_max=current_report_map.value_max)

        # if reportstep than increase the counter
        if self.var.currentTimeStep() in self.var.ReportSteps:
            cdf_flags['steps'] += 1
        # increase the counter for report all maps
        cdf_flags['end'] += 1
        cdf_flags['all'] += 1

