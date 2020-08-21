## Prepare the environment

Before you can run LISVAP, you need to:

1. Prepare base maps
2. Prepare input dataset
3. [Prepare the XML settings file](/lisflood-lisvap/3_2_LISVAP_settingsfile/)

All input to LISVAP is provided as maps (grid files in PCRaster format or maps in netCDF format). 

### 1. Base maps

LISVAP needs some base maps representing areas of simulation. These basemaps must be coherent with input dataset, which means having same area (or containing it), and projection.


The following Table lists input **base maps**. 


**Table:** *LISVAP base maps*

| Map name in settings file     | Default name           | Description                                       |
| ----------------------------- | ---------------------- | ------------------------------------------------- |
| **GENERAL**                   |                        |                                                   |
| MaskMap                       | area.nc                | Boolean map that defines model boundaries         |
| **TOPOGRAPHY**                |                        |                                                   |
| Dem                           | dem.nc                 | Elevation, in [m] above sea level                 |
| Lat                           | lat.nc                 | Latitude [decimal degrees]                        |

Some parameters can be set as a single value (constant) in settings file or as a base input map in case they change for different regions of the simulation area.
Check [settings file reference](/lisflood-lisvap/3_2_LISVAP_settingsfile/) for more details.


#### Generating base maps

On the repository, you can find some [base maps](https://github.com/ec-jrc/lisflood-lisvap/tree/master/basemaps) for the test case.

It is recommended to generate the input base maps depending on the specific use case, taking into account the spatial resolution required and the coordinate system. 
In the future, a more detailed documentation assisting in the generation of input base maps will be made available.  


### 2. Meteorological input datasets

LISVAP needs meteorological variables as input. Those should be provided as netCDF mapstacks (timeseries of 2D georeferenced variables).
The Table below lists all **meteorological input variables** that LISVAP can digest. However, not all of these need to be provided as demonstrated by the examples below.
 

**Table:** *LISVAP meteorological input variables*

| Map stack           | Default prefix | Description                                          |
| ------------------- | -------------- | ---------------------------------------------------- |
| **TEMPERATURE**     |                |                                                      |
| TMaxMaps            | tx             | Maximum daily temperature \[°C or K\]                |
| TMinMaps            | tn             | Minimum daily temperature \[°C or K\]                |
| **VAPOUR PRESSURE** |                |                                                      |
| TDewMaps            | td             | Average daily dew point temperature [°C or K]        |
| EActMaps            | pd             | Actual vapour pressure [mbar]                        |
| PSurfMaps           | ps             | Instantaneous sea level pressure [Pa]                |
| **WIND SPEED**      |                |                                                      |
| WindMaps            | ws             | Wind speed at 10 m height [m/s]                    |
| WindUMaps           | wu             | Wind speed at 10 m height, U-component [m/s]       |
| WindVMaps           | wv             | Wind speed at 10 m height, V-component [m/s]       |
| **SUNSHINE**        |                |                                                      |
| SunMaps             | s              | Sunshine duration \[hours\]                          |
| CloudMaps           | c              | Cloud cover \[octas\]                                |
| **RADIATION**       |                |                                                      |
| RgdMaps             | rg             | Downward  surface solar radiation [J/m^2/d]          |
| RNMaps              | rn             | Net thermal radiation \[J/m^2/d\] (always negative!) |
| RdsMaps             | rds            | Downward short wave radiation \[W/m^2\]               |
| RdlMaps             | rdl            | Down long wave radiation \[W/m^2\]                    |
| RusMaps             | rus            | rus - up short wave radiation \[W/m^2\]               |
| RulMaps             | rul            | rul - up long wave radiation \[W/m^2\]                |
| **HUMIDITY**        |                |                                                      |
| QAirMaps            | huss          | 2 m instantaneous specific humidity [kg/kg]           |



The tables below provide two examples of datasets that are used to run LISVAP. The first one is derived from the meteorological data collection from [EFAS](https://www.efas.eu/) (European Flood Awaress System), the second from [CORDEX](https://www.cordex.org/). We use those in the [LISVAP use cases section](https://ec-jrc.github.io/lisflood-lisvap/6_LISVAP_tests/) to demonstrate how to use LISVAP. 


   **Table:** *Meteorological input variables from EFAS data collection*

| Variable name                     |  Description                             |
| --------------------------------- | ---------------------------------------- |
| PD                                | Actual vapour pressure \[mbar\]          |
| RG                                | rgd - calculated solar radiation \[W/m2\]|
| TN                                | Minimum daily temperature \[deg C\]      |
| TX                                | Maximum daily temperature \[deg C\]      |
| WS                                | Wind speed at 10 m from surface \[m/s\]  |




   **Table:** *Meteorological input variables from the CORDEX data collection*


| Variable name                     |  Description                                    |
| --------------------------------- | ----------------------------------------------- |
| PS                                | Instantaneous sea level pressur \[Pa\]          |
| HUSS                              | 2 m instantaneous specific humidity \[kg/kg\]   |
| tmin                              | Minimum daily temperature \[K\]                 |
| tmax                              | Maximum daily temperature \[K\]                 |
| sfcWind                           | Wind speed at 10 m from surface \[m/s\]         |
| RSDS                              | Downward short wave radiation \[W/m^2\]          |
| RLDS                              | Down long wave radiation \[W/m^2\]               |
| RSUS                              | Up short wave radiation \[W/m^2\]                |
| RLUS                              | Up long wave radiation \[W/m^2\]                 |



The [GitHub tests folder](https://github.com/ec-jrc/lisflood-lisvap/tree/master/tests) also contains an example of application of LISVAP to compute $ET0$, $ES0$, and $EW0$ for the implementation of [GloFAS](https://www.globalfloods.eu/) (Global Flood Awareness System).

   **Table:** *Meteorological input variables used in the GLOFAS example*


| Variable name                     |  Description                                         |
| --------------------------------- | ---------------------------------------------------- |
| rg                                | incoming solar radiation \[J/m^2/d\]                  |
| rn                                | net longwave radiation maps \[J/m^2/d\]               |
| ta                                | average temperature \[K\]                            |
| td                                | dew point temperature \[K\]                          |
| wu                                | Wind speed at 10 m from surface, u component \[m/s\] |
| wv                                | Wind speed at 10 m from surface, v component \[m/s\] |



## Organisation of input data

It is up to the user how the input data are organised. However, it is advised to keep the base maps and meteorological input maps separated (i.e. store them in separate directories). 

For practical reasons the following input structure is suggested: 

- all meteorological input maps are in one directory (e.g. ‘meteoIn’)
- all base maps are in one directory (e.g. ‘mapsIn’)
- all output goes into one directory (e.g. ‘out’)


The following Figure illustrates this:
  

![img](../media/FoldersLISVAP.png)
 

**Figure:** *Suggested file structure for LISVAP*.
