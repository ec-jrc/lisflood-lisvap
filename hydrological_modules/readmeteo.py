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

from global_modules.add1 import *


class readmeteo(object):

    """
     # ************************************************************
     # ***** READ METEOROLOGICAL DATA              ****************
     # ************************************************************
    """

    def __init__(self, readmeteo_variable):
        self.var = readmeteo_variable

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def dynamic(self):
        """ dynamic part of the readmeteo module
            read meteo input maps
        """

        # ************************************************************
        # ***** READ METEOROLOGICAL DATA *****************************
        # ************************************************************
        if option['readNetcdfStack']:
            if option['CORDEX']:
                self.var.TAvg = readnetcdf(binding['TAvgMaps'], self.var.currentTimeStep())
                self.var.TMin = readnetcdf(binding['TMinMaps'], self.var.currentTimeStep())
                self.var.TMax = readnetcdf(binding['TMaxMaps'], self.var.currentTimeStep())

                self.var.Psurf = readnetcdf(binding['PSurfMaps'], self.var.currentTimeStep())
                self.var.Qair = readnetcdf(binding['QAirMaps'], self.var.currentTimeStep())
                self.var.Wind = readnetcdf(binding['WindMaps'], self.var.currentTimeStep())

                self.var.Rds = readnetcdf(binding['RdsMaps'], self.var.currentTimeStep())
                # Downward  short wave radiation [W/m2]
                self.var.Rdl = readnetcdf(binding['RdlMaps'], self.var.currentTimeStep())
                # Down long wave radiation [W/m2]
                self.var.Rus = readnetcdf(binding['RusMaps'], self.var.currentTimeStep())
                # upward  short wave radiation [W/m2]
                self.var.Rul = readnetcdf(binding['RulMaps'], self.var.currentTimeStep())
                # upward long wave radiation [W/m2]
            if option['EFAS']:
                self.var.TMin = readnetcdf(binding['TMinMaps'], self.var.currentTimeStep())
                # Minimum daily temperature (C)
                self.var.TMax = readnetcdf(binding['TMaxMaps'], self.var.currentTimeStep())
                # Maximum daily temperature (C)
                self.var.TAvg = (self.var.TMin + self.var.TMax) / 2.0
                               
                # Average daily temperature (C)
                

                self.var.EAct = readnetcdf(binding['EActMaps'], self.var.currentTimeStep())
                # actual vapor pressure; has to be in mbar = hPa
                # self.var.EAct = self.var.EAct / 10
                # from hPa tp kPa
                # actual vapour pressure (pd maps): typical value 0-70 hPa = 0-7 kPa

                self.var.Wind = readnetcdf(binding['WindMaps'], self.var.currentTimeStep())
                # near surface windspeed at 10 m
                self.var.Wind = self.var.Wind * 0.749
                # Adjust wind speed for measurement height: wind speed measured at
                # 10 m, but needed at 2 m height
                # Shuttleworth, W.J. (1993) in Maidment, D.R. (1993), p. 4.36
                # Typical input values 0-15 m/s (wind at 10m)

                self.var.Rgd = readnetcdf(binding['RgdMaps'], self.var.currentTimeStep())
                # calculated radiation [J/m2/day]
                # Incoming (downward surface) solar radiation [J/m2/d] (SSRD variable in ERA40)
                # typical vale: 29410560 J/m2/day = 340.4 W/m2 (1 W = 1 J/s)



        if self.var.TemperatureInKelvinFlag==1:
            self.var.TAvg = self.var.TAvg - self.var.ZeroKelvin
            self.var.TMin = self.var.TMin - self.var.ZeroKelvin
            self.var.TMax = self.var.TMax - self.var.ZeroKelvin

        self.var.DeltaT=pcraster.max(self.var.TMax-self.var.TMin,scalar(0.0))


        if option['CORDEX']:
            # correction from sea level pressure to pressure at elevation of dem
            a = 16000+64*self.var.TAvg
            self.var.Psurf = self.var.Psurf*(a-self.var.dem)/(a+self.var.dem)
            # and back to the high reso dem with adjusted temp
            self.var.Rds = self.var.Rds * self.var.WtoMJ
            self.var.Rdl = self.var.Rdl * self.var.WtoMJ
            self.var.Rus = self.var.Rus * self.var.WtoMJ
            self.var.Rul = self.var.Rul * self.var.WtoMJ


            self.var.Psurf = self.var.Psurf * 0.001
            # [Pa] to [KPa]


            self.var.EAct = (self.var.Psurf * self.var.Qair)/0.622
             # [KPA] * [kg/kg] = KPa
            self.var.Wind = self.var.Wind * 0.749
            # Adjust wind speed for measurement height: wind speed measured at
            # 10 m, but needed at 2 m height
            # Shuttleworth, W.J. (1993) in Maidment, D.R. (1993), p. 4.36
        
        


