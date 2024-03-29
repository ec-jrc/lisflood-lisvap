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
from __future__ import (absolute_import, print_function, unicode_literals)

from ..utils.operators import scalar, maximum, sqrt, sqr, exp
from ..utils.readers import readnetcdf


class ReadMeteo(object):

    """
     # ************************************************************
     # ***** READ METEOROLOGICAL DATA              ****************
     # ************************************************************
    """

    def __init__(self, readmeteo_variable):
        self.var = readmeteo_variable
        self.settings = self.var.settings
        self.splitIO = self.settings.get_option('splitInput')

    def read_temperature(self):
        """
        Read the grids of Average, Min, Max daily temperature (C)
        """
        if self.settings.get_option('useTAvg'):
            # Average daily temperature (C)
            self.var.TAvg = readnetcdf(self.settings.binding['TAvgMaps'], self.var.currentTimeStep(), variable_binding='TAvgMaps', splitIO=self.splitIO)
        else:
            # Minimum daily temperature (C)
            self.var.TMin = readnetcdf(self.settings.binding['TMinMaps'], self.var.currentTimeStep(), variable_binding='TMinMaps', splitIO=self.splitIO)
            # Maximum daily temperature (C)
            self.var.TMax = readnetcdf(self.settings.binding['TMaxMaps'], self.var.currentTimeStep(), variable_binding='TMaxMaps', splitIO=self.splitIO)
            self.var.TAvg = 0.5 * (self.var.TMin + self.var.TMax)

    def read_windspeed(self):
        """
        Read the grids of near surface windspeed at 10 m, also the U and V components.
        """
        # near surface windspeed at 10 m
        if not self.settings.get_option('useWindUVMaps'):
            self.var.Wind = readnetcdf(self.settings.binding['WindMaps'], self.var.currentTimeStep(), variable_binding='WindMaps', splitIO=self.splitIO)
        else:
            self.var.WindU = readnetcdf(self.settings.binding['WindUMaps'], self.var.currentTimeStep(), variable_binding='WindUMaps', splitIO=self.splitIO)
            self.var.WindV = readnetcdf(self.settings.binding['WindVMaps'], self.var.currentTimeStep(), variable_binding='WindVMaps', splitIO=self.splitIO)
            self.var.Wind = sqrt(sqr(self.var.WindV) + sqr(self.var.WindU))

    def read_vapor_pressure(self):
        """
        Read the grids of Vapor Pressure.
        """
        if self.settings.get_option('useTDewMaps'):
            # Synoptic weather stations often do not supply vapour pressure data,
            # but provided dew point temperature instead.
            # In that case Eact can be calculated using Goudriaan Formula(1977)
            self.var.Tdew = readnetcdf(self.settings.binding['TDewMaps'], self.var.currentTimeStep(), variable_binding='TDewMaps', splitIO=self.splitIO)
            self.var.EAct = 6.10588 * exp((17.32491 * self.var.Tdew) / (self.var.Tdew + 238.102))
        else:
            # actual vapor pressure; has to be in mbar = hPa
            # self.var.EAct = self.var.EAct / 10
            # from hPa tp kPa
            # actual vapour pressure (pd maps): typical value 0-70 hPa = 0-7 kPa
            self.var.EAct = readnetcdf(self.settings.binding['EActMaps'], self.var.currentTimeStep(), variable_binding='EActMaps', splitIO=self.splitIO, negative_value_substitute=0.0)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def dynamic(self):
        """ dynamic part of the readmeteo module
            read meteo input maps
        """
        # ************************************************************
        # ***** READ METEOROLOGICAL DATA *****************************
        # ************************************************************
        if self.settings.get_option('readNetcdfStack'):
            self.read_temperature()
            self.read_windspeed()

            if self.settings.get_option('CORDEX'):
                self.var.Psurf = readnetcdf(self.settings.binding['PSurfMaps'], self.var.currentTimeStep(), variable_binding='PSurfMaps', splitIO=self.splitIO)
                self.var.Qair = readnetcdf(self.settings.binding['QAirMaps'], self.var.currentTimeStep(), variable_binding='QAirMaps', splitIO=self.splitIO)
                # Downward  short wave radiation [W/m2]
                self.var.Rds = readnetcdf(self.settings.binding['RdsMaps'], self.var.currentTimeStep(), variable_binding='RdsMaps', splitIO=self.splitIO)
                # Down long wave radiation [W/m2]
                self.var.Rdl = readnetcdf(self.settings.binding['RdlMaps'], self.var.currentTimeStep(), variable_binding='RdlMaps', splitIO=self.splitIO)
                # upward  short wave radiation [W/m2]
                self.var.Rus = readnetcdf(self.settings.binding['RusMaps'], self.var.currentTimeStep(), variable_binding='RusMaps', splitIO=self.splitIO)
                # upward long wave radiation [W/m2]
                self.var.Rul = readnetcdf(self.settings.binding['RulMaps'], self.var.currentTimeStep(), variable_binding='RulMaps', splitIO=self.splitIO)
            else: # EFAS or GLOFAS
                self.read_vapor_pressure()

                # calculated radiation [J/m2/day]
                # Incoming (downward surface) solar radiation [J/m2/d] (SSRD variable in ERA40)
                # typical vale: 29410560 J/m2/day = 340.4 W/m2 (1 W = 1 J/s)
                self.var.Rgd = readnetcdf(self.settings.binding['RgdMaps'], self.var.currentTimeStep(), variable_binding='RgdMaps', splitIO=self.splitIO)

                if self.settings.get_option('GLOFAS'):
                    # set of forcings (rg, rn, ta, td, wu, wv)
                    # Net long wave radiation [J/m2/day]
                    self.var.Rnl = readnetcdf(self.settings.binding['RNMaps'], self.var.currentTimeStep(), variable_binding='RNMaps', splitIO=self.splitIO) * -1

        if self.settings.get_option('TemperatureInKelvinFlag'):
            self.var.TAvg = self.var.TAvg - self.var.ZeroKelvin
            if not self.settings.get_option('useTAvg'):
                self.var.TMin = self.var.TMin - self.var.ZeroKelvin
                self.var.TMax = self.var.TMax - self.var.ZeroKelvin

        if self.settings.get_option('CORDEX'):
            self.var.Rds = self.var.Rds * 86400
            self.var.Rdl = self.var.Rdl * 86400
            self.var.Rus = self.var.Rus * 86400
            self.var.Rul = self.var.Rul * 86400
            self.var.EAct = (self.var.Psurf * self.var.Qair) / 62.2
            # [KPA] * [kg/kg] = KPa

        # wind correction from 10m to 2m
        self.var.Wind = self.var.Wind * 0.749
        # Adjust wind speed for measurement height: wind speed measured at
        # 10 m, but needed at 2 m height
        # Shuttleworth, W.J. (1993) in Maidment, D.R. (1993), p. 4.36
