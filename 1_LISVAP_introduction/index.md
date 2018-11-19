# Introduction

Before telling you about LISVAP, I first have to introduce you shortly to its big brother "LISFLOOD"...

## About LISFLOOD

The LISFLOOD model is a hydrological rainfall-runoff and channel routing model that has been developed by the Floods group of the Natural Hazards project of Joint Research Centre (JRC) of the European Commission (van der Knijff & de Roo, 2008). The model is used for the modelling of hydrological processes for large (and often trans-national) catchments, and its main fields of application are flood forecasting, the assessment of river regulation measures, the assessment of the effects of land-use change, and the assessment of the effects of climate change. 

Evaporation and water uptake and subsequent transpiration by vegetation are important components of the water balance. The simulation of these processes in LISFLOOD involves four steps as visualized in the following figure:

![img](..\media\figure1.jpg)

**Figure:** *Main steps in the calculation of actual transpiration and evaporation rates in LISFLOOD (open water evaporation –which is used for evaporation of intercepted rainfall- not shown in this figure).Yellow ovals indicate the main variables and parameters that are needed to go from one step to the next one.*  


**Step 1: Potential reference evapotranspiration ($ET0$)**
<br> First, a ‘potential reference’ evapotranspiration rate, $ET0$ is calculated. This is the evapotranspiration rate from a hypothetical reference vegetation with specific characteristics with unlimited availability of water (Allen *et al*., 1998). 

**Step 2: Potential evapotranspiration from soil ($ES0$) and open water ($EW0$)**
Similarly, a potential soil evaporation rate, $ES0$ and the potential evaporation of an open water surface, $EW0$, are calculated. Note that $ET0$, $ES0$ and $EW0$ are strictly climatic variables; they are not influenced by any land use or soil properties. In reality, the potential evapotranspiration can be either higher or lower than $ET0$ due to differences in vegetation characteristics, aerodynamic resistance and surface reflectivity (albedo). Although models that explicitly account for these factors exist, they are generally too data demanding to use in large-scale applications. Instead, $ET0$ is simply multiplied by an empirical ‘crop coefficient’, $k_{crop}$, that lumps these differences into one factor, yielding a potential crop evapotranspiration rate ($ET_{crop}$). Tabulated values of $k_{crop}$ for different vegetation types are given in e.g. Allen *et al*. (1998).

**Step 3: Maximum transpiration ($T_{max}$) and evaporation from soil ($ES_{max}$)**
It is important to note here that the value of $ET_{crop}$ includes two different processes:  
- Transpiration (e.g. water uptake and subsequent evaporation by plants)
- Direct evaporation from the soil surface

The relative importance of either process depends on the vegetation cover of the soil surface: for densely vegetated surfaces the transpiration component will be dominant, whereas direct evaporation from the soil surface will be most important for scarcely vegetated areas.  Both processes are treated separately within the LISFLOOD model, and the relative contribution of each is a function of Leaf Area Index ($LAI$):

$$ T_{max}=ET_{crop} \cdot [1-exp(-k_{gb} \cdot LAI)] $$
$$ ES_{max}= ES0 \cdot exp(-k_{gb} \cdot LAI)$$

where $T_{max}$ and $ES_{max}$ are the maximum rates of transpiration and evaporation from the soil, respectively, and $к_{gb}$ is the extinction coefficient for global solar radiation (≈ 0.54). The reason why $ES_{max}$ is based on $ES0$ (and not $ET_{crop}$) is that the calculation of $ES0$ and $ET0$ includes two factors related to surface roughness and reflectivity (albedo), which are quite different for vegetated surfaces and bare soils.  

**Step 4: Actual rates of transpiration and evaporation**
As a fourth and final step, the *actual* rates of transpiration and evaporation are calculated, which are limited by the availability of water in the soil. 

The steps necessary to go from ‘potential reference’ evapo(transpi)ration to actual evaporation and transpiration are explained in detail in the [LISFLOOD Model Documentation](https://ec-jrc.github.io/lisflood-model/). 

> **LISVAP has been developed to perform the first step: calculating the potential reference evapotranspiration and evaporation from standard (gridded) meteorological observations.**


## About LISVAP

LISVAP is a a pre-processor that calculates potential evapo(transpi)ration grids that can be used as input to LISFLOOD. The approach is based on the Penman-Monteith equation, and the procedure followed is mostly based on earlier work described by Supit *et al*. (1994) and Supit & Van Der Goot (2003). The calculation of potential evapo(transpi)ration is complicated somewhat by the fact that the different datasets that are available are quite heterogeneous. For instance, incoming solar radiation can be estimated from sunshine duration or cloud cover data. Some data suppliers do not offer this kind of information, but provide pre-calculated grids of components of the radiation balance instead. Wind speed is sometimes provided in the form of *U* and *V* components. Vapour pressure is sometimes substituted by dew point temperature. LISVAP has been designed to handle this heterogeneity in a straightforward way. It contains various options that allow the user to select which data to use, and combinations of different data sources (e.g. vapour pressure and dew point temperature) can be combined within one LISVAP run. Just like LISFLOOD, LISVAP is implemented in the PCRaster Environmental Modelling language (Wesseling *et al*., 1996), wrapped in a Python based interface. It will run on any operating for which Python and PCRaster are available. Currently these include 64-bits Windows (e.g. Windows XP, Vista) and a number of Linux distributions.

## About this User Manual

This revised User Manual replaces the earlier documentation of LISVAP (van der Knijff, 2006). Chapter 2 provides a detailed description of the procedure that is used by LISVAP to calculate *ET0*, *ES0* and *EW0*.  Most of the equations are taken directly from Supit *et al.* (2003), although some are presented in a slightly altered form here. This applies especially to the goniometrical functions in the solar radiation part, which were all re-written in degrees (in Supit *et al*. some of the equations assume degrees, and other radians, which can be confusing). Chapters 3, 4, and 5 cover all practical aspects of using LISVAP. 
