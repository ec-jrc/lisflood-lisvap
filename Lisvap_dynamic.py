# -------------------------------------------------------------------------
# Name:       Lisvap Model Dynamic
# Purpose:
#
# Author:      burekpe
#
# Created:     27/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------


from global_modules.add1 import *

class LisvapModel_dyn(DynamicModel):

    # =========== DYNAMIC ====================================================

    def dynamic(self):
        """ Dynamic part of LISFLOOD
            calls the dynamic part of the hydrological modules
        """
        #del timeMes[:]
        #timemeasure("Start")

        #self.CalendarDate = self.CalendarDayStart + \
        #    datetime.timedelta(days=self.currentTimeStep() * self.DtDay)
        #self.CalendarDay = int(self.CalendarDate.strftime("%j"))
        # correct method to calculate the day of the year

        del timeMes[:]
        # CM: get time for operation "Start dynamic"
        timemeasure("Start dynamic")
        #pdb.set_trace()
        # CM: date corresponding to the model time step (yyyy-mm-dd hh:mm:ss)
        self.CalendarDate = self.CalendarDayStart + datetime.timedelta(days=(self.currentTimeStep()-1) * self.DtDay)
        # CM: day of the year corresponding to the model time step
        self.CalendarDay = int(self.CalendarDate.strftime("%j"))
        #correct method to calculate the day of the year

        # CM: model time step

        # Current calendar day (days [1...366], 1st of January = 1 , and so on)
      #  self.CalendarDay2 = self.currentTimeStep() * self.DtDay
        # Current calendar day (days [1...366], 1st of January = 1 , and so on)
      #  self.CalendarDay2 -= math.floor(self.CalendarDay2 / 365.25) * 365.25
        # self.CalendarDay=int(round(self.CalendarDay-math.floor(self.CalendarDay/365.25)*365.25))
        # correction such that daynumber 366 is regarded as day 1 again etc.
        # Takes into account leap years by setting year length to 365.25 days
        # Produces non-integer values but this is no problem here...

        i = self.currentTimeStep()
        self.TimeSinceStart = self.currentTimeStep() - self.firstTimeStep() + 1

        if Flags['loud']:
            print "%-6i %10s" %(self.currentTimeStep(),self.CalendarDate.strftime("%d/%m/%Y")) ,
        else:
            if not(Flags['check']):
                if (Flags['quiet']) and (not(Flags['veryquiet'])):
                    sys.stdout.write(".")
                if (not(Flags['quiet'])) and (not(Flags['veryquiet'])):
                    sys.stdout.write("\r%d" % i)
                    sys.stdout.flush()

        # ************************************************************
        """ up to here it was fun, now the real stuff starts
        """
        self.readmeteo_module.dynamic()
        timemeasure("Read meteo") # 1. timing after read input maps

        if Flags['check']: return  # if check than finish here

        """ Here it starts with meteorological modules:
        """

        if option['EFAS']:
            ESat = 6.10588 * exp((17.32491 * self.TAvg) / (self.TAvg + 238.102))
            # ESat=.0610588*exp((17.32491*self.TAvg)/(self.TAvg+238.102))
            # #the formula above returns value in pascal, not mbar
            # Goudriaan equation (1977)
            # saturated vapour pressure [mbar]
            # TAvg [deg Celsius]
            # exp is correct (e-power) (Van Der Goot, pers. comm 1999)
            # Windspeed2 = self.Wind*0.749
            Windspeed2 = self.Wind  # already multiplied by 0.749 in module readmeteo

            DeltaT = pcraster.max(self.TMax - self.TMin, 0.0)
            # difference between daily maximum and minimum temperature [deg C]

            BU = pcraster.max(0.54 + 0.35 * ((DeltaT - 12) / 4), 0.54)
            # empirical constant in windspeed formula
            # if DeltaT is less than 12 degrees, BU=0.54
            VapPressDef = pcraster.max(ESat - self.EAct, 0.0)
            # Vapour pressure deficit [mbar]

            EA = 0.26 * VapPressDef * (self.FactorCanopy + BU * Windspeed2)
            # evaporative demand of reference vegetation canopy [mm/d]
            EASoil = 0.26 * VapPressDef * (self.FactorSoil + BU * Windspeed2)
            # evaporative demand of bare soil surface [mm/d]
            EAWater = 0.26 * VapPressDef * (self.FactorWater + BU * Windspeed2)
            # evaporative demand of water surface [mm/d]

            # ************************************************************
            # ***** ANGOT RADIATION **************************************
            # ************************************************************

            sin = pcraster.sin
            cos = pcraster.cos
            tan = pcraster.tan
            asin = pcraster.asin
            scalar = pcraster.scalar

            Declin=-23.45*cos((360.*(self.CalendarDay+10))/(365.));
            # solar declination [degrees]
        
            SolarConstant=self.AvSolarConst*(1+(0.033*np.cos(2*self.Pi*self.CalendarDay/365.)));
            # solar constant at top of the atmosphere [J/m2/s]
            self.PD=-2.65 #correction constant 
            tmp1=((-sin(self.PD/self.Pi))+sin(Declin)*sin(self.Lat))/((cos(Declin)*cos(self.Lat))); 
            tmp2=pcraster.ifthenelse(tmp1 < 0,pcraster.scalar(asin(tmp1))-360.,pcraster.scalar(asin(tmp1)))
            DayLength=12.+(24./180.)*tmp2;
            # daylength [hour]

            DayLength=pcraster.cover(DayLength,0.0);
            # Daylength equation can produce MV at high latitudes,
            # this statements sets day length to 0 in that case  
 
            IntSolarHeight=3600.*(DayLength*sin(Declin)*sin(self.Lat)+
                       (24./self.Pi)*cos(Declin)*cos(self.Lat)*pcraster.sqrt(1-pcraster.sqr(tan(Declin)*tan(self.Lat))));
            # integral of solar height [s] over the day

            IntSolarHeight=pcraster.max(IntSolarHeight,0.0);
            # Integral of solar height cannot be negative,
            # so truncate at 0
            IntSolarHeight=pcraster.cover(IntSolarHeight,0.0)

            RadiationAngot=IntSolarHeight*SolarConstant; 
            # daily extra-terrestrial radiation (Angot radiation) [J/m2/d]


            # ************************************************************
            # ***** NET ABSORBED RADIATION *******************************
            # ************************************************************

            #Delta = ((238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2))
            # slope of saturated vapour pressure curve [mbar/deg C]
            LatHeatVap = (2501 - 2.375 * self.TAvg) / 1000
            report(LatHeatVap,'LatHeatVap')
            # latent heat of vaporization [MJ/kg]
            # TAvg in Celsius
            # Note: Mega Joule (10^6)
            # source: STOWA 2010-37 p.9 eq 5.

            #VapPressDef = pcraster.max(ESat - self.EAct, scalar(0.0))


            #Delta = (7.5 * 237.3 * 2.302585 * ESat) / ((self.TAvg + 237.3) ** 2)
            # slope of the saturated vapour pressure curve (kPaC-1)
            # ln10=2.302585
            # 7.5*237.3*2.302585=4098
            # Tavg in Celsius
            # source: STOWA 2010-37 p.11 eq 11.

            # Net absorbed radiation is calculated for three reference surfaces:
            #
            # 1. Reference vegetation canopy
            # 2. Bare soil surface
            # 3. Open water surface

            #Rnl (Maidment, 1993)
            #Rnl = f * sigma * epsilon
            #Rnl = AdjCC *stefBoltz*EmNet 
            
            EmNet=(0.56-0.079*pcraster.sqrt(self.EAct))
            Rgd=self.Rgd
            Rso=RadiationAngot*(0.75+(2*10**-5*self.Dem))
            TransAtm_Allen=Rgd/Rso;
            TransAtm_Allen=pcraster.cover(TransAtm_Allen,0)
            AdjCC=1.8*TransAtm_Allen-0.35;
            AdjCC=pcraster.ifthenelse(AdjCC < 0, 0.05, AdjCC);
            AdjCC=pcraster.ifthenelse(AdjCC > 1, 1, AdjCC);


            
            # Net emissivity
            RN = self.StefBolt*((self.TAvg+273)**4)*EmNet*AdjCC
        
            RNA=pcraster.max(((1-self.AlbedoCanopy)*Rgd-RN)/(1E6*LatHeatVap),0.0);
            # net absorbed radiation of reference vegetation canopy [mm/d]
            RNASoil=pcraster.max(((1-self.AlbedoSoil)*Rgd-RN)/(1E6*LatHeatVap),0.0);
            # net absorbed radiation of bare soil surface
            RNAWater=pcraster.max(((1-self.AlbedoWater)*Rgd-RN)/(1E6*LatHeatVap),0.0);
            
            
            
            
            
            # net absorbed radiation of water surface
            # Qnet (NetRadiation), in MJm-2d-1
            # G (SoilHeat Flux), in MJm-2d-1
            # we assume: RNA = Qnet - G
            Psychro0 = 0.00163 * (self.Press0 / LatHeatVap)
            report(Psychro0,'psy0')
            # psychrometric constant at sea level [mbar/deg C]
            # Corrected constant, was wrong originally
            # Psychro0 should be around 0.67 mbar/ deg C

            Psychro = Psychro0 * ((293 - 0.0065 * self.Dem) / 293) ** 5.26
            report(Psychro,'psy')
            # Correction for altitude (FAO, http://www.fao.org/docrep/X0490E/x0490e00.htm )
            # Note that previously some equation from Supit et al was used,
            # but this produced complete rubbish!

            Delta = ((238.102 * 17.32491 * ESat) / ((self.TAvg + 238.102) ** 2))
            report(Delta,'dt')
            
            # slope of saturated vapour pressure curve [mbar/deg C]

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

            timemeasure("All")  # 10 timing after all
            for i in xrange(len(timeMes)):
                if self.currentTimeStep() == self.firstTimeStep():
                    timeMesSum.append(timeMes[i] - timeMes[0])
                else:
                    timeMesSum[i] += timeMes[i] - timeMes[0]

            # report(self.map2,'mapx.map')
            # self.Tss['UZTS'].sample(Precipitation)
            # self.report(self.Precipitation,binding['TaMaps'])
