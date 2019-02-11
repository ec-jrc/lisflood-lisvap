
# -------------------------------------------------------------------------
# Name:        MiscInitial
# Purpose:
#
# Author:      pb
#
# Created:     29.03.2014
# Copyright:   (c) pb 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------
import datetime

from pcraster.operations import scalar, cover

from global_modules.add1 import loadmap
from global_modules.globals import binding
from global_modules.zusatz import Calendar


class MiscInitial(object):

    """
    Miscellaneous repeatedly used expressions
    """

    def __init__(self, misc_variable):
        self.var = misc_variable

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def initial(self):
        """ initial part of the misc module
        """

# -----------------------------------------------------------------
        # Miscellaneous repeatedly used expressions (as suggested by GF)

        self.var.DtSec = loadmap('DtSec')
        self.var.DtDay = self.var.DtSec / 86400
        # Time step, expressed as fraction of day (used to convert
        # rate variables that are expressed as a quantity per day to
        # into an amount per time step)

        self.var.ZeroKelvin = 273.15
        # Temperature in Kelvin corresponding to 0 degrees Centigrade
        self.var.Pi = 3.14159265358979323846
        # Numerical value of Pi

        self.var.MJtoJ = 1E6
        # Conversion factor from [MJ] to [J]
        self.var.JtoMJ = 1E-6
        # Conversion factor from [J] to [MJ]
        self.var.WtoMJ = 86400 * 1E-6
        # Conversion factor from [W] to [MJ]

        # menta: loading some more maps and constandts
        self.var.FactorCanopy = loadmap('FactorCanopy')
        self.var.FactorSoil = loadmap('FactorSoil')
        self.var.FactorWater = loadmap('FactorWater')
        self.var.Press0 = loadmap('Press0')
        self.var.Dem = loadmap('Dem')
        self.var.AvSolarConst = loadmap('AvSolarConst')
        # self.var.PD = loadmap('PD')
        self.var.Lat = loadmap('Lat')
        self.var.StefBolt = loadmap('StefBolt')
        self.var.AlbedoSoil = loadmap('AlbedoSoil')
        ##############################
        self.var.AlbedoCanopy = loadmap('AlbedoCanopy')
        self.var.AlbedoSoil = loadmap('AlbedoSoil')
        self.var.AlbedoWater = loadmap('AlbedoWater')

        self.var.dem = cover(loadmap('Dem'), scalar(0.0))

        # **************************************************************
        # SPECIAL FLAGS AND SWITCHES
        # **************************************************************
        self.var.TemperatureInKelvinFlag = loadmap('TemperatureInKelvinFlag')

        # ************************************************************
        # ***** Some additional stuff
        # ************************************************************

        self.var.CalendarDayStart = Calendar(binding['CalendarDayStart']) - datetime.timedelta(days=self.var.DtDay)

        self.var.TAvg = None
        self.var.TMin = None
        self.var.TMax = None
        self.var.Psurf = None
        self.var.Qair = None
        self.var.Wind = None

        self.var.Rds = None
        self.var.Rdl = None
        self.var.Rus = None
        self.var.Rul = None
        # setting meteo data to none - is this necessary?
