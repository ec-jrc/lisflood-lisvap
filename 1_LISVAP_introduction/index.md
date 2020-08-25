# Introduction

LISVAP is a model developed to provide potential reference evapotranspiration ($ET_0$), potential evaporation from bare soil ($ES_0$) and open water ($EW_0$) to LISFLOOD.

## About LISFLOOD

The LISFLOOD model is a hydrological rainfall-runoff and channel routing model that has been developed by the Floods group of the Natural Hazards project of Joint Research Centre (JRC) of the European Commission (van der Knijff & de Roo, 2008). The model is used for the modelling of hydrological processes for large (and often trans-national) catchments, and its main fields of application are flood forecasting, the assessment of river regulation measures, the assessment of the effects of land-use change, and the assessment of the effects of climate change. 

Evaporation and water uptake and subsequent transpiration by vegetation are important components of the water balance. The simulation of these processes in LISFLOOD involves a number of steps as visualized in the following figure:

![](..\media\figure1.jpg)

**Figure:** *Main steps in the calculation of actual transpiration and actual soil evaporation rates in LISFLOOD. Yellow ovals indicate the main variables and parameters that are needed to go from one step to the next one. Note that LISFLOOD also computes the actual open water evaporation – which is not shown in this figure but used for evaporation of intercepted rainfall as detailed [here](https://ec-jrc.github.io/lisflood-model/2_03_stdLISFLOOD_evaporation-intercepted-water/) *  


**Step 1: Potential reference evapotranspiration ($ET0$), potential evaporation from bare soil ($ES0$), potential evaporation from water surface ($EW0$)**
<br> First, $ET0$, $ES0$ and $EW0$ are calculated. The ‘potential reference’ evapotranspiration rate, $ET0$ is the evapotranspiration rate from a hypothetical reference vegetation with specific characteristics and unlimited availability of water (Allen *et al*., 1998). Note that $ET0$, $ES0$ and $EW0$  are strictly climatic variables; they are not influenced by any land use or soil properties. $EW0$ is used to compute surface water evaporation from open water bodies such as [lakes](https://ec-jrc.github.io/lisflood-model/3_02_optLISFLOOD_lakes/).

**Step 2: Potential evapotranspiration**
In reality, the potential evapotranspiration can be either higher or lower than $ET0$ due to differences in vegetation characteristics, aerodynamic resistance and surface reflectivity (albedo). Although models that explicitly account for these factors exist, they are generally too data demanding to use in large-scale applications. Instead, $ET0$ is simply multiplied by an empirical ‘crop coefficient’, $[k_{crop}](https://ec-jrc.github.io/lisflood-model/2_07_stdLISFLOOD_plant-water-uptake/)$, that lumps these differences into one factor, yielding a potential crop evapotranspiration rate ($ET_{crop}$). Tabulated values of $k_{crop}$ for different vegetation types are given in e.g. Allen *et al*. (1998).

**Step 3: Maximum transpiration ($T_{max}$) and evaporation from soil ($ES_{max}$)**
It is important to note here that the value of $ET_{crop}$ includes two different processes:  
- Transpiration (e.g. water uptake and subsequent evaporation by plants)
- Direct evaporation from the soil surface

The relative importance of either process depends on the vegetation cover of the soil surface: for densely vegetated surfaces the transpiration component will be dominant, whereas direct evaporation from the soil surface will be most important for scarcely vegetated areas.  Both processes are treated separately within the LISFLOOD model, and the relative contribution of each is a function of Leaf Area Index ($LAI$):

$$ T_{max}=ET_{crop} \cdot [1-exp(-k_{gb} \cdot LAI)] $$
$$ ES_{max}= ES0 \cdot exp(-k_{gb} \cdot LAI)$$

where $[T_{max}](https://ec-jrc.github.io/lisflood-model/2_07_stdLISFLOOD_plant-water-uptake/)$ and $[ES_{max}](https://ec-jrc.github.io/lisflood-model/2_08_stdLISFLOOD_soil-evaporation/)$ are the maximum rates of transpiration and evaporation from the soil, respectively, and $к_{gb}$ is the extinction coefficient for global solar radiation (≈ 0.54). The reason why $ES_{max}$ is based on $ES0$ (and not $ET_{crop}$) is that the calculation of $ES0$ and $ET0$ includes two factors related to surface roughness and reflectivity (albedo), which are quite different for vegetated surfaces and bare soils.  

**Step 4: Actual rates of transpiration and evaporation**
As a final step, the *actual* rates of transpiration and evaporation are calculated, which are limited by the availability of water in the soil. 
The steps necessary to go from ‘potential reference’ evapo(transpi)ration to [actual transpiration](https://ec-jrc.github.io/lisflood-model/2_07_stdLISFLOOD_plant-water-uptake/) and [actual evaporation](https://ec-jrc.github.io/lisflood-model/2_08_stdLISFLOOD_soil-evaporation/) are explained in detail in the [LISFLOOD Model Documentation](https://ec-jrc.github.io/lisflood-model/). 

> **LISVAP has been developed to perform the first step: calculating the potential reference evapotranspiration and evaporation ($ET0$, $ES0$ and $EW0$) from standard (gridded) meteorological observations.**


## About LISVAP

Hence, LISVAP is a a pre-processor that calculates potential evapo(transpi)ration grids that can be used as input to LISFLOOD. 
The approach is based on the Penman-Monteith equation, and the procedure followed is mostly based on earlier work described by Supit *et al*. (1994) and Supit & Van Der Goot (2003). 
The calculation of potential evapo(transpi)ration is complicated somewhat by the fact that the different datasets that are available are quite heterogeneous. 
For instance, incoming solar radiation can be estimated from sunshine duration or cloud cover data. 
Some data suppliers do not offer this kind of information, but provide pre-calculated grids of components of the radiation balance instead. 
Wind speed is sometimes provided in the form of *U* and *V* components. Vapour pressure is sometimes substituted by dew point temperature. 
LISVAP has been designed to handle this heterogeneity in a straightforward way. 
It contains various options that allow the user to select which data to use, and combinations of different data sources (e.g. vapour pressure and dew point temperature) can be used within one LISVAP run. 
LISVAP is implemented in Python and uses PCRaster python framework for model running (Wesseling *et al*., 1996). It will run on any operating system for which Python and PCRaster are available. 
Currently these include 64-bits Windows and Linux distributions. A docker image with all dependencies and requirements is also publicly available. 

## About this User Manual

This User Manual replaces any earlier documentation of LISVAP. It provides a [detailed description of the procedure](https://ec-jrc.github.io/lisflood-lisvap/2_LISVAP_evaporation/) that is used by LISVAP to calculate $ET0$, $ES0$ and $EW0$.  Most of the equations are taken directly from Supit *et al.* (2003), although some are presented in a slightly altered form here. This applies especially to the goniometrical functions in the solar radiation part, which were all re-written in degrees (in Supit *et al*. some of the equations assume degrees, and other radians, which can be confusing). All the remaining sections cover all practical aspects of using LISVAP, such as the [installation of the software](https://ec-jrc.github.io/lisflood-lisvap/3_LISVAP_installation/), the preparation of the [input](https://ec-jrc.github.io/lisflood-lisvap/4_LISVAP_input/) and [settings file](https://ec-jrc.github.io/lisflood-lisvap/5_LISVAP_settingsfile/) as well as a description of the [output files](https://ec-jrc.github.io/lisflood-lisvap/6_LISVAP_output/).
