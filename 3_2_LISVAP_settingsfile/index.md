# The LISVAP settings file

## Introduction

In LISVAP, all file and parameter specifications are defined in a XML settings file. 
The purpose of the settings file is to link variables and parameters in the model to in- and output files (maps, time series) and numerical values. 
In addition, the settings file can be used to specify several *options*. 
Since the XML structure is identical to the one used for LISFLOOD settings files, please have a look at Chapter 5 of the LISFLOOD User Manual (van der Knijff & de Roo, 2008) for a detailed description of the format.
 

Instead of writing the settings file completely from scratch, we suggest to use the example settings file that is provided with LISVAP as a starting point.  In order to use the example, you should make sure the following requirements are met:
 
- All input maps are named according to default file names
- All base maps are in one directory or in its subfolders
- All meteo input is in one directory or in its subfolders
- An (empty) directory where all output data can be written exists
 
If this is all true, the settings file can be prepared very quickly by editing the items in the `lfuser` element. The following is a detailed description of the different sections of the ‘lfuser’ element. 

## Time-related constants

The ‘lfuser’ section starts with a number of constants that are related to the simulation period and the time interval used. 

 ```xml
<lfsettings>
  <lfuser>
    <group>
      <comment>
**************************************************************
TIME-RELATED CONSTANTS
**************************************************************
      </comment>

      <textvar name="CalendarDayStart" value="01/01/1981 00:00">
        <comment>
        Calendar day of 1st day in model run
        </comment>
      </textvar>

      <textvar name="DtSec" value="86400">
        <comment>
time step [seconds] ALWAYS USE 86400!!
        </comment>
      </textvar>

      <textvar name="StepStart" value="01/01/1981 00:00">
        <comment>
            Date of first time step in simulation
        </comment>
      </textvar>

      <textvar name="StepEnd" value="15/01/1981 00:00">
        <comment>
            Date of last time step
        </comment>
      </textvar>

      <textvar name="ReportSteps" value="1..15">
      </textvar>
    </group>

<!-- ... other settings ....-->

  </lfuser>
</lfsettings>
 ```

-  ***CalendarDayStart*** is the calendar day of the first time step in the model run; format is DD/MM/YYYY HH:MI
-  ***DtSec*** is the simulation time interval in seconds. It has a value of 86400  for a daily time interval. Some of the simplifying assumptions made in LISVAP related to the radiation balance are not valid at time steps smaller than days. Therefore, it is advised to use LISVAP for daily time intervals only (i.e. *DtSec* should always be 86400)
-  ***StepStart*** Date of first time step; format is DD/MM/YYYY HH:MI
-  ***StepEnd*** Date of the last time step; format is DD/MM/YYYY HH:MI
-  ***ReportSteps*** Interval of steps to be reported in output maps and tss; format is a..b, with a,b >= 1 and a, b integers.


## File paths

Here you can specify paths of all in- and output.

 ```xml
<group>

    <comment>
        **************************************************************
        FILE PATHS
        **************************************************************
    </comment>

    <textvar name="PathOut" value="/DATA/lisvap/output">
        <comment>
            Output path
        </comment>
    </textvar>

    <textvar name="PathBaseMapsIn" value="$(ProjectPath)/basemaps">
        <comment>
            Path to input base maps
        </comment>
    </textvar>

    <textvar name="PathMeteoIn" value="/DATA/lisvap/input">
        <comment>
            Path to input raw meteo maps
            E:/lisflood_test/LisvapWorld/meteo/raster
        </comment>
    </textvar>
</group>
 ```

-  ***PathOut*** is the path where all output is written
-  ***PathBaseMapsIn*** is the path where all input base maps (Table 4.1) are located
-  ***PathMeteoIn*** is the path where all meteo input (Table 4.2) is stored

**Note:** To refer to the folder where LISVAP project is running, you may use $(ProjectPath), or its alias $(ProjectDir). 


## Prefixes of input meteo variables and output variables

Each variable is read as a stack of maps. 

### Using PCRaster format

For PCRaster maps, the name of each map starts with prefix, and ends with the number of the time step. All characters in between are filled with zeroes.
 The name of each map is made up of a total of 11 characters: 8 characters, a dot and a 3-character suffix. For instance, using a prefix ‘tx’ we get:

   tx000000.007		at time step 7

   tx000035.260		at time step 35260


To avoid unexpected behaviour, **never** use numbers in the prefix! For example:

​    PrefixTMax=tx10

For the first time step this yields the following file name: tx100000.001
But this is actually interpreted as time step 100,000,001! **Therefore, do not use numbers in the prefix!**

### Using netCDF mapstacks

Name of each map is made up of its prefix followed by .nc extension. 

The corresponding part of the settings file is pretty self-explanatory (note that you will never need *all* these variables together in one LISVAP run): 

 ```xml
<group>
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
</group>
 ```

-  ***PrefixTMax*** prefix of the maximum temperature maps
-  ***PrefixTMin*** prefix of the minimum temperature maps
-  ***PrefixTDew*** prefix of the dew point temperature maps
-  ***PrefixEAct*** prefix of the actual vapour pressure maps
-  ***PrefixWind*** prefix of the wind speed maps
-  ***PrefixWindU*** prefix of the wind speed U-component maps
-  ***PrefixWindV*** prefix of the wind speed V-component maps
-  ***PrefixSun*** prefix of the sunshine duration maps
-  ***PrefixCloud*** prefix of the cloud cover maps
-  ***PrefixRgd*** prefix of the incoming solar radiation maps
-  ***PrefixRN*** prefix of the net long-wave radiation maps


Here you can define the prefix that is used for each meteorological output variable.

 ```xml
 <group>
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
</group>
 ```

-  ***PrefixTAvg*** prefix of the average temperature maps 
-  ***PrefixE0*** prefix of the potential open-water evaporation maps 
-  ***PrefixES0*** prefix of the potential bare-soil evaporation maps
-  ***PrefixET0*** prefix of the potential (reference) evapotranspiration maps


## LISVAP input options

LISVAP has several options, which can be set in the settings file’s ‘lfoptions’ element. Most options in LISVAP are related to the input data used. Since different providers of meteorological data often provide slightly different variables, LISVAP has been designed to offer some flexibility in this respect. 

Table 5.1 below lists all currently implemented input options and their respective defaults. These options all act as switches (1= on,  0=off).  Note that each option generally requires additional items in the settings file. For instance, using the dew point temperature option requires that the corresponding map stack is defined in the settings file. The template settings file that is provided with LISVAP always contains file definitions for all implemented options. 

 **Table:** *LISVAP input options.*	

| Option                    | Description                                                                        | Default |
| ------------------------- | ---------------------------------------------------------------------------------- | ------- |
| TemperatureInKelvinFlag   | Temperature in Kelvin                                                              | False   |
| readNetcdfStack           | Input variables as netCDF mapstacks                                                | False   |
| writeNetcdfStack          | Output variables as netCDF mapstacks                                               | False   |
| writeNetcdf               | Output variables as netCDF maps                                                    | False   |
| repAvTimeseries           | Write output TSS                                                                   | False   |
| repE0Maps                 | Write output variable $E_0$ map                                                    | True    |
| repET0Maps                | Write output variable $ET_0$ map                                                   | True    |
| repES0Maps                | Write output variable $ES_0$ map                                                   | True    |
| repTAvgMaps               | Write output variable $T_{avg}$ map                                                | True    |
| useTavg                   | Use $T_{avg}$ input map. If false, will be computed out of $T_{max}$ and $T_{min}$ | False   |
| InitLisflood              |                                                                                    | False   |
| InitLisfloodwithoutSplit  |                                                                                    | False   |
| EFAS                      | Use *EFAS* setup                                                                   | True    |
| CORDEX[^1]                | Use *CORDEX* setup                                                                 | False   |

[^1]: Keep in mind that EFAS and CORDEX are two mutually-exclusive flags. If both are true, EFAS flag has precedence.
