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

import datetime

try:
    from pcraster.multicore._operations import scalar, cover
except ImportError:
    from pcraster.operations import scalar, cover

from ..utils.readers import loadmap
from ..utils.tools import calendar


class MiscInitial(object):

    """
    Miscellaneous repeatedly used expressions
    """

    def __init__(self, misc_variable):
        self.var = misc_variable
        self.settings = self.var.settings

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
        self.var.PD = loadmap('PD')
        self.var.Lat = loadmap('Lat')
        self.var.StefBolt = loadmap('StefBolt')
        self.var.AlbedoSoil = loadmap('AlbedoSoil')
        ##############################
        self.var.AlbedoCanopy = loadmap('AlbedoCanopy')
        self.var.AlbedoWater = loadmap('AlbedoWater')

        self.var.dem = cover(loadmap('Dem'), scalar(0.0))

        # ************************************************************
        # ***** Some additional stuff
        # ************************************************************

        self.var.calendar_day_start = calendar(self.settings.binding['CalendarDayStart']) - datetime.timedelta(days=self.var.DtDay)

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
