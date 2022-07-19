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

from __future__ import (absolute_import, print_function)

import sys
import datetime

import numpy as np
from pcraster.framework import DynamicModel

from .utils.operators import exp, maximum, cos, sin, ifthenelse, asin, scalar, cover, tan, sqr, sqrt, abs
from .utils import LisSettings, TimeProfiler


class LisvapModelDyn(DynamicModel):

    def __init__(self):
        """ init part of the initial part
            defines the mask map and the outlet points
            initialization of the hydrological modules
        """
        super(LisvapModelDyn, self).__init__()
        self.calendar_date = None
        self.calendar_day = None
        self.time_since_start = None
        self.ETRef = None
        self.ESRef = None
        self.EWRef = None


    def int_solar_height_main(self, day_length, declin):
        """
            integral of solar height [s] over the day
        """
        return 3600. * (day_length * sin(declin) * sin(self.Lat) + (24./self.Pi) * cos(declin) * cos(self.Lat) * sqrt(1 - sqr(tan(declin) * tan(self.Lat))))


    def int_solar_height_north_pole(self, day_length, declin):
        """
            integral of solar height [s] over the day in the north pole during summer solstice
        """
        return 3600. * (day_length * sin(declin) * sin(self.Lat))


    # =========== DYNAMIC ====================================================

    def dynamic(self):
        """ Dynamic part of LISVAP
            calls the dynamic part of the hydrological modules
        """
        tp = TimeProfiler.instance()
        settings = LisSettings.instance()
        # CM: get time for operation "Start dynamic"
        tp.timemeasure('Start dynamic')
        # CM: date corresponding to the model time step (yyyy-mm-dd hh:mm:ss)
        self.calendar_date = self.calendar_day_start + datetime.timedelta(days=(self.currentTimeStep()) * self.DtDay)
        # CM: day of the year corresponding to the model time step
        self.calendar_day = int(self.calendar_date.strftime("%j"))

        # correct method to calculate the day of the year
        # CM: model time step

        i = self.currentTimeStep()
        self.time_since_start = self.currentTimeStep() - self.firstTimeStep() + 1

        if settings.flags['loud']:
            print("%-6i %10s" % (self.currentTimeStep(), self.calendar_date.strftime("%d/%m/%Y")))
        elif not settings.flags['checkfiles']:
            if settings.flags['quiet'] and not settings.flags['veryquiet']:
                sys.stdout.write(".")
            elif not settings.flags['quiet'] and not(settings.flags['veryquiet']):
                sys.stdout.write("\r%d" % i)
                sys.stdout.flush()

        # ************************************************************
        self.readmeteo_module.dynamic()
        tp.timemeasure('Read meteo')  # 1. timing after read input maps

        if settings.flags['checkfiles']:
            return  # if check then finish here

        """ Here it starts with meteorological modules:
        """

        if settings.get_option('EFAS'):
            # ESat=.0610588*exp((17.32491*self.TAvg)/(self.TAvg+238.102))
            # the formula above returns value in pascal, not mbar
            # Goudriaan equation (1977)
            # saturated vapour pressure [mbar]
            # TAvg [deg Celsius]
            # exp is correct (e-power) (Van Der Goot, pers. comm 1999)
            # ESat = 6.10588 * exp((17.32491 * self.TAvg) / (self.TAvg + 238.102))
            ESat = 6.10588 * exp((17.32491 * self.TAvg) / (self.TAvg + 238.102))

            Windspeed2 = self.Wind

            # difference between daily maximum and minimum temperature [deg C]
            # DeltaT = operations.max(self.TMax - self.TMin, 0.0)
            DeltaT = maximum(self.TMax - self.TMin, 0.0)

            # empirical constant in windspeed formula
            # if DeltaT is less than 12 degrees, BU=0.54
            # BU = operations.max(0.54 + 0.35 * ((DeltaT - 12) / 4), 0.54)
            BU = maximum(0.54 + 0.35 * ((DeltaT - 12) / 4), 0.54)

            # Vapour pressure deficit [mbar]
            VapPressDef = maximum(ESat - self.EAct, 0.0)

            # evaporative demand of reference vegetation canopy [mm/d]
            EA = 0.26 * VapPressDef * (self.FactorCanopy + BU * Windspeed2)

            # evaporative demand of bare soil surface [mm/d]
            EASoil = 0.26 * VapPressDef * (self.FactorSoil + BU * Windspeed2)

            # evaporative demand of water surface [mm/d]
            EAWater = 0.26 * VapPressDef * (self.FactorWater + BU * Windspeed2)

            # ************************************************************
            # ***** ANGOT RADIATION **************************************
            # ************************************************************

            # solar declination [degrees]
            declin = -23.45 * cos((360. * (self.calendar_day + 10)) / 365.)

            # solar constant at top of the atmosphere [J/m2/s]
            solar_constant = self.AvSolarConst * (1 + (0.033 * cos(360. * self.calendar_day / 365.)))

            tmp1 = ((-sin(self.PD / 180.)) + sin(declin) * sin(self.Lat))/(cos(declin) * cos(self.Lat))
            tmp2 = ifthenelse(tmp1 < 0, scalar(asin(tmp1))-360., scalar(asin(tmp1)))

            # abs(tmp1) > 1. corrects the day length at higher altitudes to 24h
            day_length = ifthenelse(abs(tmp1) > 1., scalar(24.), 12. + (24. / 180.) * tmp2)
            # daylength [hour]

            day_length = cover(day_length, 0.0)
            # Daylength equation can produce MV at high latitudes,
            # this statements sets day length to 0 in that case  

            # abs(tmp1) > 1. allows correcting the integral of solar height at higher altitudes (north pole)
            int_solar_height = ifthenelse(abs(tmp1) > 1., self.int_solar_height_north_pole(day_length, declin), self.int_solar_height_main(day_length, declin))

            int_solar_height = maximum(int_solar_height, 0.0)
            # Integral of solar height cannot be negative,
            # so truncate at 0
            int_solar_height = cover(int_solar_height, 0.0)

            RadiationAngot = int_solar_height * solar_constant
            # daily extra-terrestrial radiation (Angot radiation) [J/m2/d]

            # ************************************************************
            # ***** NET ABSORBED RADIATION *******************************
            # ************************************************************

            # Delta = ((238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2))
            # slope of saturated vapour pressure curve [mbar/deg C]
            LatHeatVap = 2.501 - 0.002361 * self.TAvg
            # latent heat of vaporization [MJ/kg]
            # TAvg in Celsius
            # Note: Mega Joule (10^6)
            # source: FAO

            # Net absorbed radiation is calculated for three reference surfaces:
            #
            # 1. Reference vegetation canopy
            # 2. Bare soil surface
            # 3. Open water surface

            # Rnl (Maidment, 1993)
            # Rnl = f * sigma * epsilon
            # Rnl = AdjCC *stefBoltz*EmNet
            
            EmNet = (0.56 - 0.079 * sqrt(self.EAct))
            Rgd = self.Rgd
            Rso = RadiationAngot * (0.75 + (2 * 10**-5 * self.Dem))
            TransAtm_Allen = Rgd / Rso
            TransAtm_Allen = cover(TransAtm_Allen, 0)
            AdjCC = 1.8 * TransAtm_Allen - 0.35
            AdjCC = ifthenelse(AdjCC < 0, 0.05, AdjCC)
            AdjCC = ifthenelse(AdjCC > 1, 1, AdjCC)

            # Net emissivity
            RN = self.StefBolt * ((self.TAvg + 273)**4) * EmNet * AdjCC

            # RNA = operations.max(((1 - self.AlbedoCanopy) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)
            # # net absorbed radiation of reference vegetation canopy [mm/d]
            # RNASoil = operations.max(((1 - self.AlbedoSoil) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)
            # # net absorbed radiation of bare soil surface
            # RNAWater = operations.max(((1 - self.AlbedoWater) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)
            RNA = maximum(((1 - self.AlbedoCanopy) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of reference vegetation canopy [mm/d]
            RNASoil = maximum(((1 - self.AlbedoSoil) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of bare soil surface
            RNAWater = maximum(((1 - self.AlbedoWater) * Rgd - RN) / (1E6 * LatHeatVap), 0.0)

            # net absorbed radiation of water surface
            # Qnet (NetRadiation), in MJm-2d-1
            # G (SoilHeat Flux), in MJm-2d-1
            # we assume: RNA = Qnet - G
            Psychro0 = 0.00163 * (self.Press0 / LatHeatVap)
            # psychrometric constant at sea level [mbar/deg C]
            # Corrected constant, was wrong originally
            # Psychro0 should be around 0.67 mbar/ deg C

            Psychro = Psychro0 * ((293 - 0.0065 * self.Dem) / 293) ** 5.26
            # Correction for altitude (FAO, http://www.fao.org/docrep/X0490E/x0490e00.htm )
            # Note that previously some equation from Supit et al was used,
            # but this produced complete rubbish!

            Delta = ((238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2))

            # slope of saturated vapour pressure curve [mbar/deg C]
        elif settings.get_option('GLOFAS'):
            EAct = 6.10588 * exp((17.32491 * self.Tdew) / (self.Tdew + 238.102))
            # the formula above returns value in pascal, not mbar
            # Goudriaan equation (1977)
            # saturated vapour pressure [mbar]
            # TAvg [deg Celsius]
            # exp is correct (e-power) (Van Der Goot, pers. comm 1999)
            ESat = 6.10588 * exp((17.32491 * self.TAvg) / (self.TAvg + 238.102))

            # difference between daily maximum and minimum temperature [deg C]
            DeltaT = 0
            # empirical constant in windspeed formula
            # if DeltaT is less than 12 degrees, BU=0.54
            # BU = operations.max(0.54 + 0.35 * ((DeltaT - 12) / 4), 0.54)
            BU = 0.54

            # Vapour pressure deficit [mbar]
            VapPressDef = maximum(ESat - EAct, 0.0)

            # evaporative demand of reference vegetation canopy [mm/d]
            EA = 0.26 * VapPressDef * (self.FactorCanopy + BU * self.Wind)

            # evaporative demand of bare soil surface [mm/d]
            EASoil = 0.26 * VapPressDef * (self.FactorSoil + BU * self.Wind)

            # evaporative demand of water surface [mm/d]
            EAWater = 0.26 * VapPressDef * (self.FactorWater + BU * self.Wind)

            LatHeatVap = 2.501 - 0.002361 * self.TAvg
            # latent heat of vaporization [MJ/kg]
            # TAvg in Celsius
            # Note: Mega Joule (10^6)
            # source: FAO

            RNA = maximum(((1 - self.AlbedoCanopy) * self.Rgd - self.Rnl) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of reference vegetation canopy [mm/d]
            RNASoil = maximum(((1 - self.AlbedoSoil) * self.Rgd - self.Rnl) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of bare soil surface
            RNAWater = maximum(((1 - self.AlbedoWater) * self.Rgd - self.Rnl) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of water surface
            # Qnet (NetRadiation), in MJm-2d-1
            # G (SoilHeat Flux), in MJm-2d-1
            # we assume: RNA = Qnet - G
            Psychro0 = 0.00163 * (self.Press0 / LatHeatVap)
            # psychrometric constant at sea level [mbar/deg C]
            # Corrected constant, was wrong originally
            # Psychro0 should be around 0.67 mbar/ deg C

            Psychro = Psychro0 * ((293 - 0.0065 * self.Dem) / 293) ** 5.26
            # Correction for altitude (FAO, http://www.fao.org/docrep/X0490E/x0490e00.htm )
            # Note that previously some equation from Supit et al was used,
            # but this produced complete rubbish!

            Delta = ((238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2))

            # slope of saturated vapour pressure curve [mbar/deg C]

        elif settings.get_option('CORDEX'):

            Windspeed2 = self.Wind  # already multiplied by 0.749 in module readmeteo

            DeltaT = maximum(self.TMax - self.TMin, 0.0)
            # difference between daily maximum and minimum temperature [deg C]

            BU = maximum(0.54 + 0.35 * ((DeltaT - 12) / 4), 0.54)
            # empirical constant in windspeed formula
            # if DeltaT is less than 12 degrees, BU=0.54

            ESat = 6.10588 * exp((17.32491 * self.TAvg) / (self.TAvg + 238.102))
            # Goudriaan equation (1977)
            # saturated vapour pressure [mbar]
            # TAvg [deg Celsius]
            # exp is correct (e-power) (Van Der Goot, pers. comm 1999)

            VapPressDef = maximum(ESat - self.EAct, 0.0)
            # Vapour pressure deficit [mbar]

            # Evaporative demand is calculated for three reference surfaces:
            #
            # 1. Reference vegetation canopy
            # 2. Bare soil surface
            # 3. Open water surface
            EA = 0.26 * VapPressDef * (self.FactorCanopy + BU * Windspeed2)
            # evaporative demand of reference vegetation canopy [mm/d]
            EASoil = 0.26 * VapPressDef * (self.FactorSoil + BU * Windspeed2)
            # evaporative demand of bare soil surface [mm/d]
            EAWater = 0.26 * VapPressDef * (self.FactorWater + BU * Windspeed2)
            # evaporative demand of water surface [mm/d]

            LatHeatVap = 2.501 - 0.002361 * self.TAvg
            # latent heat of vaporization [MJ/kg]

            Psychro0 = 0.00163 * (self.Press0 / LatHeatVap)
            # psychrometric constant at sea level [mbar/deg C]
            # Corrected constant, was wrong originally
            # Psychro0 should be around 0.67 mbar/ deg C

            Psychro = Psychro0 * ((293 - 0.0065 * self.Dem) / 293) ** 5.26
            # Correction for altitude (FAO, http://www.fao.org/docrep/X0490E/x0490e00.htm )
            # Note that previously some equation from Supit et al was used,
            # but this produced complete rubbish!

            Delta = (238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2)
            # slope of saturated vapour pressure curve [mbar/deg C]

            # ************************************************************
            # ***** ANGOT RADIATION **************************************
            # ************************************************************

            Declin = -23.45 * cos((360. * (self.calendar_day + 10)) / 365.)
            # solar declination [degrees]

            SolarConstant = self.AvSolarConst * (1 + (0.033 * cos(360. * self.calendar_day / 365.)))
            # solar constant at top of the atmosphere [J/m2/s]

            tmp1 = ((-sin(self.PD / 180.)) + sin(Declin) * sin(self.Lat)) / (cos(Declin) * cos(self.Lat))
            tmp2 = ifthenelse(tmp1 < 0, scalar(asin(tmp1)) - 360., scalar(asin(tmp1)))

            # abs(tmp1) > 1. corrects the day length at higher altitudes to 24h
            DayLength = ifthenelse(abs(tmp1) > 1., scalar(24.), 12. + (24. / 180.) * tmp2)
            # daylength [hour]

            DayLength = cover(DayLength, 0.0)
            # Daylength equation can produce MV at high latitudes,
            # this statements sets day length to 0 in that case

            # abs(tmp1) > 1. allows correcting the integral of solar height at higher altitudes (north pole)
            IntSolarHeight = ifthenelse(abs(tmp1) > 1., self.int_solar_height_north_pole(DayLength, Declin), self.int_solar_height_main(DayLength, Declin))
            # integral of solar height [s] over the day

            IntSolarHeight = maximum(IntSolarHeight, 0.0)
            # Integral of solar height cannot be negative,
            # so truncate at 0
            IntSolarHeight = cover(IntSolarHeight, 0.0)

            RadiationAngot = IntSolarHeight * SolarConstant
            # daily extra-terrestrial radiation (Angot radiation) [J/m2/d]

            # ************************************************************
            # ***** NET ABSORBED RADIATION *******************************
            # ************************************************************

            # equation Allen et al. 1994
            # using the digital elevation model
            # from:  An Update for the Definition of Reference Evapotranspiration  Allen et al. 1994

            Rds = self.Rds
            Rso = RadiationAngot * (0.75 + (2 * 10 ** -5 * self.Dem))
            TransAtm_Allen = Rds/Rso
            TransAtm_Allen = cover(TransAtm_Allen, 0)
            AdjCC = 1.8 * TransAtm_Allen - 0.35
            AdjCC = ifthenelse(AdjCC < 0, 0.05, AdjCC)
            AdjCC = ifthenelse(AdjCC > 1, 1, AdjCC)

            EmNet = (0.56 - 0.079 * sqrt(self.EAct))
            # Net emissivity
            RN = self.StefBolt * ((self.TAvg + 273) ** 4) * EmNet * AdjCC
            # net  longwave radiation [J/m2/day]

            RNA = maximum(((1 - self.AlbedoCanopy) * Rds - RN) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of reference vegetation canopy [mm/d]
            RNASoil = maximum(((1 - self.AlbedoSoil) * Rds - RN) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of bare soil surface
            RNAWater = maximum(((1 - self.AlbedoWater) * Rds - RN) / (1E6 * LatHeatVap), 0.0)
            # net absorbed radiation of water surface

        # ************************************************************
        # ***** EA: EVAPORATIVE DEMAND *******************************
        # ************************************************************
        # Evaporative demand is calculated for three reference surfaces:
        # 1. Reference vegetation canopy
        # 2. Bare soil surface
        # 3. Open water surface
        self.ETRef = ((Delta * RNA) + (Psychro * EA)) / (Delta + Psychro)
        # potential reference evapotranspiration rate [mm/day]
        self.ESRef = ((Delta * RNASoil) + (Psychro * EASoil)) / (Delta + Psychro)
        # potential evaporation rate from a bare soil surface [mm/day]
        self.EWRef = ((Delta * RNAWater) + (Psychro * EAWater)) / (Delta + Psychro)
        # potential evaporation rate from water surface [mm/day]

        # ************************************************************
        # ***** WRITING RESULTS: TIME SERIES AND MAPS ****************
        # ************************************************************
        self.output_module.dynamic()

        tp.timemeasure('All')  # 10 timing after all
