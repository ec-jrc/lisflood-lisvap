# -------------------------------------------------------------------------
# Name:       Lisvap Model Initial
# Purpose:
#
# Author:      burekpe
#
# Created:     27/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

from hydrological_modules.miscInitial import *
from hydrological_modules.readmeteo import *


from global_modules.output import *


# --------------------------------------------
class LisvapModel_ini(DynamicModel):

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
        DynamicModel.__init__(self)

        # try to make the maskmap more flexible e.g. col, row,x1,y1  or x1,x2,y1,y2
        self.MaskMap = loadsetclone('MaskMap')

        if option['readNetcdfStack']:
            # get the extent of the maps from the precipitation input maps
            # and the modelling extent from the MaskMap
            # cutmap[] defines the MaskMap inside the precipitation map
            cutmap[0], cutmap[1], cutmap[2], cutmap[3] = mapattrNetCDF(binding['TMinMaps'])
        if option['writeNetcdfStack'] or option['writeNetcdf']:
            # if NetCDF is writen, the pr.nc is read to get the metadata
            # like projection
            metaNetCDF(binding['TMinMaps'])

        # ----------------------------------------
        # include output of tss and maps
        self.output_module = outputTssMap(self)
        # include all the hydrological modules
        self.misc_module = miscInitial(self)
        self.readmeteo_module = readmeteo(self)

# ====== INITIAL ================================
    def initial(self):
        """ Initial part of LISFLOOD
            calls the initial part of the hydrological modules
        """

        MMaskMap = self.MaskMap
        # for checking maps

        self.ReportSteps = ReportSteps['rep']
        self.misc_module.initial()
        self.output_module.initial()

        self.sumEW=scalar(0.0)
        self.sumET=scalar(0.0)

        # ----------------------------------------------------------------------
