# LISVAP input files

All input to LISVAP is provided as maps (grid files in PCRaster format) and tables. This chapter describes all the data that are required to run the application.

## Input maps

The following Table lists all needed input **(base) maps**. 


**Table:** *LISVAP base maps*

| Map                      | Default name | Description                                       |
| ------------------------ | ------------ | ------------------------------------------------- |
| **GENERAL**              |              |                                                   |
| MaskMap                  | area.map     | Boolean map that defines model boundaries         |
| **TOPOGRAPHY**           |              |                                                   |
| Dem                      | dem.map      | Elevation, in [m] above sea level                 |
| Lat                      | lat.map      | Latitude [decimal degrees]                        |
| **ANGSTROM CONSTANTS**   |              |                                                   |
| Aa                       | angstr_a.map | Angstrom regression coefficient [-]               |
| Ba                       | angstr_b.map | Angstrom regression coefficient [-]               |
| **SUPIT CONSTANTS**      |              |                                                   |
| As                       | supit_a.map  | Supit model regression coefficient [°C-0.5]       |
| Bs                       | supit_b.map  | Supit model regression coefficient [-]            |
| Cs                       | supit_c.map  | Supit model regression coefficient [MJ m-2 day-1] |
| **HARGREAVES CONSTANTS** |              |                                                   |
| Ah                       | hargrv_a.map | Hargreaves formula constant [°C-0.5]              |
| Bh                       | hargrv_b.map | Hargreaves formula constant [MJ m-2 day-1]        |



The Table below lists all **meteorological input variables** (note that not all of them are compulsory).


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


## Organisation of input and output data

It is up to the user how the input data are organised. However, it is advised to keep the base maps and meteorological input maps separated (i.e. store them in separate directories). For practical reasons the following input structure is suggested: 

- all meteorological input maps are in one directory (e.g. ‘meteoIn’)
- all base maps are in one directory (e.g. ‘mapsIn’)
- all output goes into one directory (e.g. ‘out’)
 

The following Figure illustrates this:

  

![img](../media/figure3.jpg)

 

**Figure:** *Suggested file structure for LISVAP*.

 

## Generating input base maps

At the time of writing this document, complete sets of LISVAP base maps covering the whole of Europe have been compiled at 1- and 5-km pixel resolution. 
A number of automated procedures have been written that allow you to generate sub-sets of these for pre-defined areas (using either existing mask maps or co-ordinates of catchment outlets). 
These procedures (which are specific to the data server setup at the Floods Action, IES, JRC, Ispra) are documented in a separate document on ‘LISFLOOD and LISVAP map extraction’. 
If you are an external user of LISFLOOD, please contact the Floods Action to extract the data for you.