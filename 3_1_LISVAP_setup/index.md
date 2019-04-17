## Prepare the environment

Before to run LISVAP, you need to:

1. Prepare base maps
2. Prepare input dataset
3. [Prepare the XML settings file](/lisflood-lisvap/3_2_LISVAP_settingsfile)

All input to LISVAP is provided as maps (grid files in PCRaster format or maps in netCDF format). 

### Base maps

LISVAP needs some base maps representing areas of simulation. These basemaps must be coherent with input dataset, which means having same area (or containing it), and projection.


The following Table lists all types of input **base maps**. 


**Table:** *LISVAP base maps*

| Map name in settings file     | Default name           | Description                                       |
| ----------------------------- | ---------------------- | ------------------------------------------------- |
| **GENERAL**                   |                        |                                                   |
| MaskMap                       | area.map or area.nc    | Boolean map that defines model boundaries         |
| **TOPOGRAPHY**                |                        |                                                   |
| Dem                           | dem.map                | Elevation, in [m] above sea level                 |
| Lat                           | lat.map                | Latitude [decimal degrees]                        |
| Lon                           | lon.map                | Longitude [decimal degrees]                       |
| **ANGSTROM CONSTANTS**[^1]    |                        |                                                   |
| Aa                            | angstr_a.map           | Angstrom regression coefficient [-]               |
| Ba                            | angstr_b.map           | Angstrom regression coefficient [-]               |
| **SUPIT CONSTANTS**           |                        |                                                   |
| As                            | supit_a.map            | Supit model regression coefficient [°C-0.5]       |
| Bs                            | supit_b.map            | Supit model regression coefficient [-]            |
| Cs                            | supit_c.map            | Supit model regression coefficient [MJ m-2 day-1] |
| **HARGREAVES CONSTANTS**      |                        |                                                   |
| Ah                            | hargrv_a.map           | Hargreaves formula constant [°C-0.5]              |
| Bh                            | hargrv_b.map           | Hargreaves formula constant [MJ m-2 day-1]        |

[^1]: Constants can be set as a single value in settings file instead of using a map.



#### Generating input base maps

On the repository, you can find some [base maps](https://github.com/ec-jrc/lisflood-lisvap/tree/master/basemaps) for the test case.

It is recommended to generate the input base maps depending on the specific use case, takeing into account the spatial resolution required and the coordinate system. In the future, a more detailed documentation assisting in the generation of input base maps will be made available.  


### Input dataset

LISVAP model inputs are meteo variables, provided as netCDF mapstacks (timeseries of 2D georeferenced variables).
Depending on available meteo variables, you can setup LISVAP to run using two different datasets of meteorological input variables. To facilitate the use of LISVAP two specific use cases, derived from the EFAS and CORDEX set up are available for demonstration purposes.  [^2].  

[^2]: [CORDEX](https://www.cordex.org/)

#### EFAS


   **Table:** *Input variables for the "EFAS run"*

| Variable name                     |  Description                             |
| --------------------------------- | ---------------------------------------- |
| PD                                | Actual vapour pressure \[mbar\]          |
| RG                                | rgd - calculated solar radiation \[W/m2\]|
| TN                                | Minimum daily temperature \[deg C\]      |
| TX                                | Maximum daily temperature \[deg C\]      |
| WS                                | Wind speed at 10 m from surface \[m/s\]  |


#### CORDEX


   **Table:** *Input variables for CORDEX run*


| Variable name                     |  Description                                    |
| --------------------------------- | ----------------------------------------------- |
| PS                                | Instantaneous sea level pressur \[Pa\]          |
| HUSS                              | 2 m instantaneous specific humidity \[kg/kg\]   |
| TN                                | Minimum daily temperature \[K\]                 |
| TX                                | Maximum daily temperature \[K\]                 |
| WS                                | Wind speed at 10 m from surface \[m/s\]         |
| RDS                               | Downward short wave radiation \[W/m2\]          |
| RDL                               | Down long wave radiation \[W/m2\]               |
| RUS                               | Up short wave radiation \[W/m2\]                |
| RUL                               | Up long wave radiation \[W/m2\]                 |


The Table below lists all **meteorological input variables**.
 

**Table:** *LISVAP meteorological input variables*

| Map stack           | Default prefix | Description                                        |
| ------------------- | -------------- | -------------------------------------------------- |
| **TEMPERATURE**     |                |                                                    |
| TMaxMaps            | tx             | Maximum daily temperature [°C or K]                |
| TMinMaps            | tn             | Minimum daily temperature [°C or K]                |
| **VAPOUR PRESSURE** |                |                                                    |
| TDewMaps            | td             | Average daily dew point temperature [°C or K]      |
| EActMaps            | pd             | Actual vapour pressure [mbar]                      |
| **WIND SPEED**      |                |                                                    |
| WindMaps            | ws             | Wind speed at 10 m height [m s-1]                  |
| WindUMaps           | wu             | Wind speed at 10 m height, U-component [m s-1]     |
| WindVMaps           | wv             | Wind speed at 10 m height, V-component [m s-1]     |
| **SUNSHINE**        |                |                                                    |
| SunMaps             | s              | Sunshine duration [hours]                          |
| CloudMaps           | c              | Cloud cover [octas]                                |
| **RADIATION**       |                |                                                    |
| RgdMaps             | rg             | Downward  surface solar radiation [J m-2 d]        |
| RNMaps              | rn             | Net thermal radiation [J m-2 d] (always negative!) |


## Organisation of input data

It is up to the user how the input data are organised. However, it is advised to keep the base maps and meteorological input maps separated (i.e. store them in separate directories). For practical reasons the following input structure is suggested: 

- all meteorological input maps are in one directory (e.g. ‘meteoIn’)
- all base maps are in one directory (e.g. ‘mapsIn’)
- all tables are in one directory (e.g. ‘tables’)
- all output goes into one directory (e.g. ‘out’)


The following Figure illustrates this:
  

![img](../media/figure3.jpg)
 

**Figure:** *Suggested file structure for LISVAP*.
