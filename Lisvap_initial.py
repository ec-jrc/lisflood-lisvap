# -------------------------------------------------------------------------
# Name:       Lisvap Model Initial
# Purpose:
#
# Author:      burekpe
#
# Created:     27/02/2014
# Licence:     EPL 2.0
# -------------------------------------------------------------------------


from pcraster.framework.dynamicPCRasterBase import DynamicModel
from pcraster.operations import scalar

from global_modules import LisSettings
from global_modules.add1 import loadsetclone, metaNetCDF, mapattrNetCDF
from global_modules.globals import cutmap
from global_modules.output import OutputTssMap
from hydrological_modules.miscInitial import MiscInitial
from hydrological_modules.readmeteo import ReadMeteo


class LisvapModelIni(DynamicModel):

    """ LISVAP initial part
        same as the PCRaster script -initial-
        this part is to initialize the variables
        it will call the initial part of the hydrological modules
    """

    def __init__(self):
        """ init part of the initial part
            defines the mask map and the outlet points
            initialization of the hydrological modules
        """
        # DynamicModel.__init__(self)
        super(DynamicModel, self).__init__()

        # try to make the maskmap more flexible e.g. col, row,x1,y1  or x1,x2,y1,y2
        self.MaskMap = loadsetclone('MaskMap')
        self.settings = LisSettings.instance()
        if self.settings.options['readNetcdfStack']:
            # get the extent of the maps from the precipitation input maps
            # and the modelling extent from the MaskMap
            # cutmap[] defines the MaskMap inside the precipitation map
            cutmap[0], cutmap[1], cutmap[2], cutmap[3] = mapattrNetCDF(self.settings.binding['TMinMaps'])
        if self.settings.options['writeNetcdfStack'] or self.settings.options['writeNetcdf']:
            # if NetCDF is written, the pr.nc is read to get the metadata
            # like projection
            metaNetCDF(self.settings.binding['TMinMaps'])

        # ----------------------------------------
        # include output of tss and maps
        self.output_module = OutputTssMap(self)
        # include all the hydrological modules
        self.misc_module = MiscInitial(self)
        self.readmeteo_module = ReadMeteo(self)
        self.ReportSteps = None
        self.sumEW = None
        self.sumET = None

    # ====== INITIAL ================================
    def initial(self):
        """ Initial part of LISFLOOD
            calls the initial part of the hydrological modules
        """
        self.ReportSteps = self.settings.report_steps['rep']
        self.misc_module.initial()
        self.output_module.initial()
        self.sumEW = scalar(0.0)
        self.sumET = scalar(0.0)
