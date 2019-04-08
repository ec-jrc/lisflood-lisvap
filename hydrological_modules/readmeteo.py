# -------------------------------------------------------------------------
# Name:        READ METEO input maps
# Purpose:
#
# Author:      burekpe
#
# Created:     12/08/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------
from pcraster import operations
from pcraster.operations import scalar

from global_modules.add1 import readnetcdf


class ReadMeteo(object):

    """
     # ************************************************************
     # ***** READ METEOROLOGICAL DATA              ****************
     # ************************************************************
    """

    def __init__(self, readmeteo_variable):
        self.var = readmeteo_variable
        self.settings = self.var.settings

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def dynamic(self):
        """ dynamic part of the readmeteo module
            read meteo input maps
        """

        # ************************************************************
        # ***** READ METEOROLOGICAL DATA *****************************
        # ************************************************************
        if self.settings.options['readNetcdfStack']:
            if self.settings.options['CORDEX']:
                self.var.TMin = readnetcdf(self.settings.binding['TMinMaps'], self.var.currentTimeStep())
                self.var.TMax = readnetcdf(self.settings.binding['TMaxMaps'], self.var.currentTimeStep())
                if  self.settings.options['useTavg']:
                    self.var.TAvg = readnetcdf(self.settings.binding['TAvgMaps'], self.var.currentTimeStep())
                else:
                    self.var.TAvg = .5 * (self.var.TMin + self.var.TMax)

                self.var.Psurf = readnetcdf(self.settings.binding['PSurfMaps'], self.var.currentTimeStep())
                self.var.Qair = readnetcdf(self.settings.binding['QAirMaps'], self.var.currentTimeStep())
                self.var.Wind = readnetcdf(self.settings.binding['WindMaps'], self.var.currentTimeStep())

                self.var.Rds = readnetcdf(self.settings.binding['RdsMaps'], self.var.currentTimeStep())
                # Downward  short wave radiation [W/m2]
                self.var.Rdl = readnetcdf(self.settings.binding['RdlMaps'], self.var.currentTimeStep())
                # Down long wave radiation [W/m2]
                self.var.Rus = readnetcdf(self.settings.binding['RusMaps'], self.var.currentTimeStep())
                # upward  short wave radiation [W/m2]
                self.var.Rul = readnetcdf(self.settings.binding['RulMaps'], self.var.currentTimeStep())
                # upward long wave radiation [W/m2]

            elif self.settings.options['EFAS']:

                self.var.TMin = readnetcdf(self.settings.binding['TMinMaps'], self.var.currentTimeStep())
                # Minimum daily temperature (C)
                self.var.TMax = readnetcdf(self.settings.binding['TMaxMaps'], self.var.currentTimeStep())
                # Maximum daily temperature (C)

                # FIXME do we need to use option['useTavg'] also here as it is in CORDEX run?
                self.var.TAvg = (self.var.TMin + self.var.TMax) / 2.0
                # Average daily temperature (C)

                self.var.EAct = readnetcdf(self.settings.binding['EActMaps'], self.var.currentTimeStep())
                # actual vapor pressure; has to be in mbar = hPa
                # self.var.EAct = self.var.EAct / 10
                # from hPa tp kPa
                # actual vapour pressure (pd maps): typical value 0-70 hPa = 0-7 kPa

                self.var.Wind = readnetcdf(self.settings.binding['WindMaps'], self.var.currentTimeStep())
                # near surface windspeed at 10 m
                self.var.Wind = self.var.Wind * 0.749
                # Adjust wind speed for measurement height: wind speed measured at
                # 10 m, but needed at 2 m height
                # Shuttleworth, W.J. (1993) in Maidment, D.R. (1993), p. 4.36
                # Typical input values 0-15 m/s (wind at 10m)

                self.var.Rgd = readnetcdf(self.settings.binding['RgdMaps'], self.var.currentTimeStep())
                # calculated radiation [J/m2/day]
                # Incoming (downward surface) solar radiation [J/m2/d] (SSRD variable in ERA40)
                # typical vale: 29410560 J/m2/day = 340.4 W/m2 (1 W = 1 J/s)

        if self.var.TemperatureInKelvinFlag:
            self.var.TAvg = self.var.TAvg - self.var.ZeroKelvin
            self.var.TMin = self.var.TMin - self.var.ZeroKelvin
            self.var.TMax = self.var.TMax - self.var.ZeroKelvin

        self.var.DeltaT = operations.max(self.var.TMax - self.var.TMin, scalar(0.0))

        if self.settings.options['CORDEX']:
            self.var.Rds = self.var.Rds * 86400
            self.var.Rdl = self.var.Rdl * 86400
            self.var.Rus = self.var.Rus * 86400
            self.var.Rul = self.var.Rul * 86400
            self.var.EAct = (self.var.Psurf * self.var.Qair) / 62.2
            # [KPA] * [kg/kg] = KPa
            self.var.Wind = self.var.Wind * 0.749
            # Adjust wind speed for measurement height: wind speed measured at
            # 10 m, but needed at 2 m height
            # Shuttleworth, W.J. (1993) in Maidment, D.R. (1993), p. 4.36
