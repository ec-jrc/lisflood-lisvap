## LISVAP output

This Table lists all the outputs that can be produced by LISVAP:  

**Table:** *LISVAP output.*

| Name                                                    | Default prefix | Description                                         |
| ------------------------------------------------------- | -------------- | --------------------------------------------------- |
| **MAPS**                                                |                |                                                     |
| TAvgMaps                                                | ta             | Average temperature [°C] (average of tmin and tmax) |
| ET0Maps                                                 | et             | Potential reference evapotranspiration [mm day^-^1] |
| E0Maps                                                  | e              | Potential open water evaporation [mm day^-^1]       |
| ES0Maps                                                 | es             | Potential bare-soil soil evaporation [mm day^-^1]   |
| **TIME SERIES** (averaged over area defined on MaskMap) |                |                                                     |
| TAvgTS                                                  | tAvg.tss       | Average temperature [°C]                            |
| ET0TS                                                   | et0.tss        | Potential reference evapotranspiration [mm day^-^1] |
| E0TS                                                    | e0.tss         | Potential open water evaporation [mm day^-^1]       |
| ES0TS                                                   | es0.tss        | Potential bare-soil soil evaporation [mm day^-^1]   |


Note that reporting of these map stacks can be switched on or off by the user adding/changing [options](/lisflood-lisvap/3_2_LISVAP_settingsfile#options) in the LISVAP settings file.
