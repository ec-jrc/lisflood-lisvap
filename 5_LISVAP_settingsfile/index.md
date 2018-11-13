# The LISVAP settings file

## Introduction

In LISVAP, all file and parameter specifications are defined in a settings file. The purpose of the settings file is to link variables and parameters in the model to in- and output files (maps, time series) and numerical values. In addition, the settings file can be used to specify several *options*. Since the XML structure is identical to the one used for LISFLOOD settings files, please have a look at Chapter 5 of the LISFLOOD User Manual (van der Knijff & de Roo, 2008) for a detailed description of the format. The settings file can be prepared in any text editor (e.g. Notepad, Editpad, Emacs, vi), or alternatively in a dedicated XML editor (e.g. XMLSpy, XXE).

 

Instead of writing the settings file completely from scratch, we suggest to use the example settings file that is provided with LISVAP as a starting point.  In order to use the example, you should make sure the following requirements are met:

 

- All input maps are named according to default file names (see Chapter 4)
- All base maps are in one directory
- All tables are in one directory
- All meteo input is in one directory
- An (empty) directory where all output data can be written exists

 

If this is all true, the settings file can be prepared very quickly by editing the items in the ‘lfuser’ element. The following is a detailed description of the different sections of the ‘lfuser’ element. 

## Time-related constants

The ‘lfuser’ section starts with a number of constants that are related to the simulation period and the time interval used. 

 ```xml
<comment>
**************************************************************
TIME-RELATED CONSTANTS
**************************************************************
</comment>

<textvar name="CalendarDayStart" value="1">
<comment>
Calendar day number of 1st day in model run
e.g. 1st of January: 1; 1st of June: 151 (or 152 in leap year)
</comment>
</textvar>

<textvar name="DtSec" value="86400">
<comment>
time step [seconds] ALWAYS USE 86400!!
</comment>
</textvar>

<textvar name="StepEnd" value="10">
<comment>
Number of last time step
</comment>
</textvar>
 ```

-  ***CalendarDayStart*** is the calendar day number of the first time step in the model run; its value is in the range 1-366
-  ***DtSec*** is the simulation time interval in seconds. It has a value of 86400  for a daily time interval. Some of the simplifying assumptions made in LISVAP related to the radiation balance are not valid at time steps smaller than days. Therefore, it is advised to use LISVAP for daily time intervals only (i.e. *DtSec* should always be 86400)
-  ***StepEnd*** is the number of the last time step



## Special flags and switches

 

 ```xml
<comment>
**************************************************************
SPECIAL FLAGS AND SWITCHES
**************************************************************
</comment>

<textvar name="TemperatureInKelvinFlag" value="0">
<comment>
Flag that is 1 if input temperatures (TMax, TMin, TDew) are in Kelvin,
and 0 if they are in deg C 
</comment>
</textvar>
 ```

- *TemperatureInKelvinFlag* tells LISVAP whether the input values of maximum, minimum and dew point temperature are in °C (0) or K (1).

  

## File paths

Here you can specify the location of all in- and output.

 ```xml
<comment>
**************************************************************
FILE PATHS
**************************************************************
</comment>

<textvar name="PathOut" value="./out">
<comment>
Output path
</comment>
</textvar>

<textvar name="PathBaseMapsIn" value="./mapsIn">
<comment>
Path to input base maps
</comment>
</textvar>

<textvar name="PathTables" value="./tables">
<comment>
Path to tables
</comment>
</textvar>

<textvar name="PathMeteoIn" value="./meteoIn">
<comment>
Path to input raw meteo maps
</comment>
</textvar>
 ```

- ***PathOut*** is the path where all output is written
-  ***PathBaseMapsIn*** is the path where all input base maps (Table 4.1) are located
-  ***PathTables*** is the path where all tables (Table 4.3) are located
-  ***PathMeteoIn*** is the path where all meteo input (Table 4.2) is stored



## Prefixes of input meteo variables

Here you can define the prefix that is used for each meteorological input variable. Each variable is read as a stack of maps. The name of each map starts with prefix, and ends with the number of the time step. All characters in between are filled with zeroes. The name of each map is made up of a total of 11 characters: 8 characters, a dot and a 3-character suffix. For instance, using a prefix ‘tx’ we get:

​    tx000000.007		at time step 7

   tx000035.260		at time step 35260

 

To avoid unexpected behaviour, **never** use numbers in the prefix! For example:

​    PrefixTMax=tx10

 For the first time step this yields the following file name: tx100000.001

 But this is actually interpreted as time step 100,000,001! **Therefore, do not use numbers in the prefix!**

 

The corresponding part of the settings file is pretty self-explanatory (note that you will never need *all* these variables together in one LISVAP run): 

 ```xml
<comment>
**************************************************************
PREFIXES OF INPUT METEO VARIABLES
**************************************************************
</comment>

<textvar name="PrefixTMax" value="tx">
<comment>
prefix maximum temperature maps
</comment>
</textvar>

<textvar name="PrefixTMin" value="tn">
<comment>
prefix minimum temperature maps
</comment>
</textvar>

<textvar name="PrefixTDew" value="td">
<comment>
prefix dew point temperature maps
</comment>
</textvar>

<textvar name="PrefixEAct" value="pd">
<comment>
prefix vapour pressure maps
</comment>
</textvar>

<textvar name="PrefixWind" value="ws">
<comment>
prefix wind speed maps
</comment>
</textvar>

<textvar name="PrefixWindU" value="wu">
<comment>
prefix wind speed U-component maps
</comment>
</textvar>

<textvar name="PrefixWindV" value="wv">
<comment>
prefix wind speed V-component maps
</comment>
</textvar>

<textvar name="PrefixSun" value="s">
<comment>
prefix sunshine duration maps
</comment>
</textvar>

<textvar name="PrefixCloud" value="c">
<comment>
prefix cloud cover maps
</comment>
</textvar>

<textvar name="PrefixRgd" value="rg">
<comment>
prefix incoming solar radiation maps
</comment>
</textvar>

<textvar name="PrefixRN" value="rn">
<comment>
prefix net longwave radiation maps
</comment>
</textvar>
 ```

- ***PrefixTMax*** is the prefix of the maximum temperature maps
-  ***PrefixTMin*** is the prefix of the minimum temperature maps
-  ***PrefixTDew*** is the prefix of the dew point temperature maps
-  ***PrefixEAct*** is the prefix of the actual vapour pressure maps
-  ***PrefixWind*** is the prefix of the wind speed maps
-  ***PrefixWindU*** is the prefix of the wind speed U-component maps
-  ***PrefixWindV*** is the prefix of the wind speed V-component maps
-  ***PrefixSun*** is the prefix of the sunshine duration maps
-  ***PrefixCloud*** is the prefix of the cloud cover maps
-  ***PrefixRgd*** is the prefix of the incoming solar radiation maps
-  ***PrefixRN*** is the prefix of the net long-wave radiation maps



## Prefixes of output meteo variables

Here you can define the prefix that is used for each meteorological output variable.

 ```xml
<comment>
**************************************************************
PREFIXES OF OUTPUT METEO VARIABLES
**************************************************************
</comment>

<textvar name="PrefixTAvg" value="ta">
<comment>
prefix average temperature maps
</comment>
</textvar>

<textvar name="PrefixE0" value="e">
<comment>
prefix E0 maps
</comment>
</textvar>

<textvar name="PrefixES0" value="es">
<comment>
prefix ES0 maps
</comment>
</textvar>

<textvar name="PrefixET0" value="et">
<comment>
prefix ET0 maps
</comment>
</textvar>
 ```

- ***PrefixTAvg*** is the prefix of the average temperature maps 
-  ***PrefixE0*** is the prefix of the potential open-water evaporation maps 
-  ***PrefixES0*** is the prefix of the potential bare-soil evaporation maps
-  ***PrefixET0*** is the prefix of the potential (reference) evapotranspiration maps



## LISVAP input options

LISVAP has several options, which can be set in the settings file’s ‘lfoptions’ element. Most options in LISVAP are related to the input data used. Since different providers of meteorological data often provide slightly different variables, LISVAP has been designed to offer some flexibility in this respect. 

 

Table 5.1 below lists all currently implemented input options and their respective defaults. These options all act as switches (1= on,  0=off).  Note that each option generally requires additional items in the settings file. For instance, using the dew point temperature option requires that the corresponding map stack is defined in the settings file. The template settings file that is provided with LISVAP always contains file definitions for all implemented options. 

 **Table:** *LISVAP input options.*	

| Option        | Description                            | Default |
| ------------- | -------------------------------------- | ------- |
| useEActMaps   | Use actual vapour pressure maps        | 1       |
| useTDewMaps   | Use dew point temperature maps         | 0       |
| useWindMaps   | Use wind speed maps                    | 1       |
| useWindUVMaps | Use wind speed U- and V-component maps | 0       |
| useSunMaps    | Use sunshine duration maps             | 0       |
| useCloudMaps  | Use cloud cover maps                   | 0       |
| useRgdMaps    | Use maps of incoming solar radiation   | 0       |
| useRNMaps     | Use maps of net long-wave radiation    | 0       |



### On combining vapour pressure and dew point temperature maps

In order to calculate the evaporative demand (and the net long-wave radiation), LISVAP needs either vapour pressure or dew point temperature. By default, LISVAP expects only vapour pressure. By activating the “useTDewMaps” option, dew point temperature can be used:

```xml
<setoption name="useTDewMaps" choice="1"></setoption>
```

 

If *only* dew point temperature maps are available, the “useEActMaps” option needs to be disabled as well:

```xml
<setoption name="useEActMaps" choice="0"></setoption>
```

 

If the area for which you want to run LISVAP is partially covered with dew point temperature observations, and partially with vapour pressure, both can be combined within one single LISVAP run. To do so, first prepare the input stacks of dew point temperature and vapour pressure. Areas (pixels) for which no vapour pressure is available should have a missing value (i.e. if you open one of the input maps in Display or Aguila these pixels should appear as transparent/black). Likewise, areas for which dew point temperature is unavailable should have a missing value as well. If a pixel has a valid value (i.e. not a missing value) for *both* vapour pressure *and* dew point temperature, vapour pressure takes precedence in LISVAP. In other words: LISVAP will use vapour pressure and ignore dew point temperature. Pixels that have a missing value for *both* variables will show up as missing in the output maps. Once the input stacks are ready, simply activate *both* the “useEActMaps” and the “useTDewMaps” options.

 

An alternative way to combine vapour pressure and dew point temperature observations is to convert all dew point temperature observations to corresponding vapour pressures using the Goudriaan equation (which is also used by LISVAP):
$$
e_a=610588 \cdot^{\frac{17.32491 \cdot T_{dew}}{T_{dew}+238.102}}
$$
In that case there is no need to use the “useTDewMaps” option.

### On wind speed and wind speed components

Wind speed information is needed to calculate the evaporative demand of the atmosphere. Wind speed data are sometimes provided as U- and V- components (e.g. ERA40). By default, LISVAP expects only “regular” wind speed. By activating the “useWindUVMaps” option, U- and V- components can be used:

 ```xml
<setoption name="useWindUVMaps" choice="1"></setoption>
 ```



If *only* U- and V-components are available, the “useWindMaps” option needs to be disabled as well:

 ```xml
<setoption name="useWindMaps" choice="0"></setoption> 
 ```



If the area for which you want to run LISVAP is partially covered with wind speed observations, and partially with U- and V-components, both can be combined within one single LISVAP run. In that case you have to activate both the “useWindMaps” and the “useWindUVMaps” options. As for preparing the input maps, the same rules apply as with the vapour pressure / dew point temperature maps. If both “regular” wind speed and the U- and V- components are defined for one pixel, the “regular” wind speed takes precedence. If neither “regular” wind speed nor the components are defined, the output of LISVAP will show up as missing in the output maps.

 

Alternatively, U- and V- components may be transformed to “regular” wind speed before running LISVAP using Pythagoras’ rule. In that case there is no need to use the “useWindUVMaps” option.

### On sunshine duration and cloud cover

As explained Chapter 2 of this manual, LISVAP supports 3 different equations for calculating the incoming solar radiation. The most simple equation (Hargreaves, which is also the least accurate) only needs daily maximum and minimum temperature, whereas the more sophisticated ones need sunshine duration and/or clouds cover as well. Because both sunshine duration and cloud cover are often difficult to obtain, LISVAP’s default behaviour is to use only maximum and minimum temperature (which are both required by LISVAP anyway). If sunshine duration and/or cloud cover are available, you should use the “useSunMaps” and/or “useCloudMaps” options, respectively. Again, non-availability of either variable should be indicated using missing values[[1\]](#_ftn1). If the availability of sunshine duration and cloud cover overlaps, LISVAP gives precedence to the “highest quality” available input, ie.:

1. use sunshine duration if available;
2. if not use cloud cover;
3. if cloud cover isn’t available either, use maximum/minimum temperature

 

LISVAP (or more precisely, pcrcalc) will exit with an error message if maximum or minimum temperature is not available.

### On incoming solar radiation and net long-wave radiation

The “useRgdMaps” and “useRNMaps” options allow you to bypass all radiation-balance calculations. Both options are typically used in conjunction with each other (although it is possible to use them individually). Note that LISVAP variable *Rgd* is referred to as “downward surface solar radiation” (*SSRD*) in the ERA40 data set. Likewise, LISVAP’s *RN* variable is known as “net thermal radiation” (*STR*) in ERA40. It is important to note that “RNMaps” always contains *negative* values (as is the case with its ERA40 counterpart *STR*). Annex 1 gives an overview of the steps necessary to prepare ERA40 re-analysis data for use in LISVAP. Also, if you decide to use the “useRgdMaps” and “useRNMaps” options, *RgdMaps* and *RNMaps* must be defined for *every* pixel (i.e. the radiation balance calculations are completely skipped, so any missing values here are *not* covered up!).

### Examples

The number of available input options might look somewhat complicated at first sight. Therefore, Table 5.2 gives some typical examples of how the input options can be used together (of course many other combinations are possible).

 

 **Table:** *Example uses of input options.*	

| Description                     | Options                                                      | Input needed                                                 |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| “Minimum input” setup (default) | none                                                         | maximum temperature, minimum temperature, vapour pressure, wind speed |
| “MARS” setup                    | <setoption name="useSunMaps" choice="1"></setoption> <br/> <setoption name="useCloudMaps" choice="1"></setoption> | maximum temperature, minimum temperature, vapour pressure, wind speed, sunshine duration, cloud cover |
| “ERA40” setup                   | <setoption name="useTDewMaps" choice="1"></setoption> <br/> <setoption name="useWindUVMaps" choice="1"></setoption> <br/> <setoption name="useRgdMaps" choice="1"></setoption> <br/> <setoption name="useRNMaps" choice="1"></setoption> | maximum temperature, minimum temperature, dew point temperature , wind speed U- and V-components, incoming solar radiation, net long-wave radiation |

 

  

------

[[1\]](#_ftnref1) IMPORTANT: The PCRaster scripts that preceded LISVAP used a special value of “-1” to flag missing sunshine duration and wind speed. This is **not** supported anymore in LISVAP, and will in fact give erroneous results! 

[[2\]](#_ftnref2) Since ERA40 provides temperature data in [K], you should also set the “TemperatureInKelvinFlag” flag in the LISVAP settings file to 1 here.