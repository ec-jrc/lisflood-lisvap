# -*- coding: utf-8 -*-

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

import numpy as np

from .utils import LisSettings, NetcdfMetadata, CutMap, FileNamesManager, DynamicModel
from .utils.readers import loadsetclone
from .utils.output import OutputMap
from .utils.operators import scalar
from .hydrological.miscinitial import MiscInitial
from .hydrological.readmeteo import ReadMeteo


class LisvapModelIni(DynamicModel):

    """ LISVAP initial part
        this part is to initialize the variables
        it will call the initial part of the hydrological modules
    """

    def __init__(self):
        """ init part of the initial part
            defines the mask map and the outlet points
            initialization of the hydrological modules
        """
        # DynamicModel.__init__(self)
        super(LisvapModelIni, self).__init__()

        # try to make the maskmap more flexible e.g. col, row,x1,y1  or x1,x2,y1,y2
        self.MaskMap = loadsetclone('MaskMap')
        self.settings = LisSettings.instance()
        fileManager = FileNamesManager.instance()
        map_for_metadata = ''
        if self.settings.get_option('useTAvg') and self.settings.binding.get('TAvgMaps'):
            map_for_metadata = fileManager.get_file_name('TAvgMaps')
        elif self.settings.get_option('useTDewMaps') and self.settings.binding.get('TDewMaps'):
            map_for_metadata = fileManager.get_file_name('TDewMaps')
        elif self.settings.get_option('useRelHumidityMaps') and self.settings.binding.get('RelHMaps'):
            map_for_metadata = fileManager.get_file_name('RelHMaps')
        elif self.settings.binding.get('TMinMaps'):
            map_for_metadata = fileManager.get_file_name('TMinMaps')

        # CutMap defines the extent to read from input netcdf data (cropping)
        CutMap.register(map_for_metadata)

        # if NetCDF is written, the pr.nc is read to get the metadata
        # like projection
        NetcdfMetadata.register(map_for_metadata)

        # ----------------------------------------
        self.output_module = OutputMap(self)
        self.misc_module = MiscInitial(self)
        self.readmeteo_module = ReadMeteo(self)
        self.ReportSteps = None
        self.sumEW = None
        self.sumET = None

    # ====== INITIAL ================================
    def initial(self):
        """ Initial part of LISVAP
            calls the initial part of the hydrological modules
        """
        self.ReportSteps = self.settings.report_steps['rep']
        self.misc_module.initial()
        self.output_module.initial()
        self.sumEW = scalar(0.0)
        self.sumET = scalar(0.0)
