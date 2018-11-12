# 2. Potential reference evapotranspiration and evaporation

## Penman-Monteith equation

Reference values for potential evapotranspiration and evaporation are estimated using the Penman-Monteith equation (Supit *et al*., 1994, Supit & Van Der Goot, 2003):

​    $ET0 = \frac{\Delta R_{na} + \gamma EA}{\Delta + \gamma}$



where:

   $ET0$	Potential evapotranspiration rate from a closed vegetation canopy (reference crop) $[\frac{mm}{day}]$

   $R_{na}$	Net absorbed radiation $[\frac{mm}{day}]$

   $EA$	Evaporative demand of the atmosphere $[\frac{mm}{day}]$

   $\Delta$		Slope of the saturation vapour pressure curve $[\frac{mbar}{^\circ C}]$

   $\gamma$		Psychrometric constant $[\frac{mbar}{^\circ C}]$	

 

The same equation is also used to estimate potential evaporation from a water surface and the evaporation from a (wet) bare soil surface (by using different values for the absorbed radiation term, $R_{na}$). The procedure to calculate potential evapo(transpi)ration is summarised in the following Figure. 

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image004.jpg)

**Figure:** *Overview of procedure to calculate potential reference evapo(transpi)ration. Terms with an asterisk (\*) are calculated separately for a reference vegetation canopy, a bare soil surface and an open water surface, respectively.*

 

The table below lists the properties of the reference surfaces that are used in the computation of $ET0$, $ES0$ and $EW0$, respectively. 

   **Table:** *Properties of reference surfaces for* $ET0$, $ES0$ and $EW0$ 

|         |                          |                                                              |
| ------- | ------------------------ | ------------------------------------------------------------ |
|         | **α** *(surface albedo)* | **fc**   *(empirical constant in evaporative demand equation)* |
| **ET0** | 0.23                     | 1                                                            |
| **ES0** | 0.15                     | 0.75                                                         |
| **EW0** | 0.05                     | 0.5                                                          |

 

## Calculating net absorbed radiation

Calculating the net absorbed radiation term involves the following steps:

 

1. Calculate the daily extra-terrestrial radiation (Angot radiation)
2. From the Angot radiation, calculate the daily incoming solar radiation (using information on the daily number of sunshine hours or cloud cover, if available)
3. Calculate the daily net long-wave radiation (based on meteorological conditions)
4. Calculate the net absorbed radiation

 

Some data sets (e.g. ERA5) provide pre-calculated values for both incoming solar radiation and net long-wave radiation. Because of this, LISVAP offers the possibility to use these values directly, in which case all radiation balance calculations (except for the Angot radiation) are bypassed.  

### Angot radiation

The daily extra-terrestrial radiation is the product of the solar constant at the top of the atmosphere and the integral of the solar height over the day:

​    $R_{a,d} = S_{c, d} \int sin \ \beta \ dt_h$

 

where:

​    $R_{a,d}$		Daily extra-terrestrial radiation $[{\frac{J}{m^2 \ day}}]$

   $S_{c,d}$		Solar constant   at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$

   $\int sin \ \beta \ dt_h$	Integral of the solar height over the day $[s]$

 

The solar constant on a given day is calculated as:

   $S_{c, d} = S_c(1 + 0.033 \cos[\frac{360 \ t_d}{365}])$



where:

   $S_c$		 Average solar radiation at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$ (= 1370 ${\frac{J}{m^2 \ s}}$)

   $S_{c,d}$	Solar constant at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$

   $t_d$		Calendar day number (1st of January is 1, etcetera) $[-]$

 

The calendar day number is always a number between 1 and 365.25 (taking into account leap years, a year has on average 365.25 days). 

 

The integral of the solar height equals:

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image012.gif)   (2-4)

 

where:

 

| *Ld* | : Astronomical   day length [h] |
| ---- | ------------------------------- |
| *δ*  | : Solar   declination [°]       |
| *λ*  | : Latitude [°]                  |

 

The solar declination is a simple function of the calendar day number (*td*):

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image014.gif)                                                                       (2-5)

 

Day length is given by:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image016.gif)                                         (2-6)

 

with:

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image018.gif)                                                                     (2-7)

 

where *PD* is a correction constant (-2.65).

### Incoming solar radiation

Depending on the availability of input data, three equations are available to calculate the incoming solar radiation. If the number of sunshine hours on a particular day is known, the Ångström equation is used:

 

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image020.gif)                                                                                  (2-8)

where:

 

| *Rg,d*   | : Incoming daily   global solar radiation [J m-2 day-1]      |
| -------- | ------------------------------------------------------------ |
| *Ra,d*   | : Daily   extra-terrestrial radiation (Angot radiation) [J m-2 day-1] |
| *n*      | : Number of   bright sunshine hours per day [h]              |
| *Ld*     | : Astronomical   day length [h]                              |
| *Aa, Ba* | : Empirical   constants [-]                                  |

 

In the absence of any observed information on the number of sunshine hours, the following equation is used if cloud cover observations are available (Supit, 1994; Supit & Van Kappel, 1998):

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image022.gif)                                      (2-9)

 

where:

 

| *Tmax* | : Maximum   temperature [°C]                      |
| ------ | ------------------------------------------------- |
| *Tmin* | : Minimum   temperature [°C]                      |
| *CC*   | : Mean total   cloud cover during the day [octas] |
| *Ld*   | : Astronomical   day length [h]                   |
| *As*   | : Empirical   constant [°C-0.5]                   |
| *Bs*   | : Empirical   constant [-]                        |
| *Cs*   | : Empirical constant [J m-2 d-1]                  |

 

If neither sunshine duration nor cloud cover observations are available, the Hargreaves equation is used instead:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image024.gif)                                                                     (2-10)

 

where:

 

| *Ah* | : Empirical   constant [°C-0.5]  |
| ---- | -------------------------------- |
| *Bh* | : Empirical constant [J m-2 d-1] |

 

Net long-wave radiation 

The following equation is used to calculate the net long-wave radiation[[1\]](#_ftn1) (Maidment, 1993):

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image026.gif)                                                                                   (2-11)

 

where:

 

| *Rnl* | : Net long-wave   radiation [J m-2 day-1]                    |
| ----- | ------------------------------------------------------------ |
| *σ*   | : Stefan   Boltzmann constant (4.90x10-3)    [J m-2 K-4 day-1] |
| *f*   | : Adjustment   factor for cloud cover                        |
| *ε’*  | : Net emissivity   between the atmosphere and the ground     |

 

The net emissivity is calculated as:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image028.gif)                                                                                       (2-12)

 

with: 

 

| *ea* | : Actual vapour   pressure [mbar] |
| ---- | --------------------------------- |
|      |                                   |

 

Synoptic weather stations often do not supply vapour pressure data, but provided dew point temperature instead. In that case *ea* can be calculated using the following equation by Goudriaan (1977):

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image030.gif)                                                                                 (2-13)

 

with:

 

| *Tdew* | : dew point   temperature [°C] |
| ------ | ------------------------------ |
|        |                                |

 

The equation of Brunt (1932) is used to estimate the cloud cover factor:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image032.gif)                                                                                            (2-14)

 

where:

 

| *ea*        | : Actual vapour   pressure [mbar]                            |
| ----------- | ------------------------------------------------------------ |
| *Be* , *Bf* | : Constants   according to Brunt (1932) (depend on latitude) [-] |

 

If no information on the number of bright sunshine hours is available, the relative sunshine duration term is estimated using the Ångström equation:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image034.gif)                                                                                    (2-15)

 

where *Aa* and *Ba* are the empirical Ångström constants.

### Net absorbed radiation 

Finally, the net absorbed radiation [mm day-1] is calculated as:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image036.gif)                                                                                    (2-16)

 

where *α* is the albedo (reflection coefficient) of the surface, and *L* is the latent heat of vaporization [MJ kg-1]:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image038.gif)                                                                             (2-17)

 

The net absorbed radiation is calculated for three cases: for a reference vegetation canopy (using *α*=0.23), a bare soil surface (*α*=0.15), and an open water surface (*α*=0.05)

 

## Evaporative demand of the atmosphere

The evaporative demand of the atmosphere is calculated as:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image040.gif)                                                                (2-18)

 

where:

 

| *EA*   | : Evaporative   demand [mm day-1]         |
| ------ | ----------------------------------------- |
| *es*   | : Saturated   vapour pressure [mbar]      |
| *ea*   | : Actual vapour   pressure [mbar]         |
| *fc*   | : Empirical   constant [-]                |
| *BU*   | : Coefficient in   wind function [-]      |
| *u(2)* | : Mean wind speed   at 2 m height [m s-1] |

 

Saturated vapour pressure is calculated as a function of mean daily air temperature:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image042.gif)                                                                                  (2-19)

 

The coefficient in the wind function, *BU*, is also temperature dependent:

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image044.gif)                                                           (2-20)

 

Here, *Δt* is the difference between the daily maximum and minimum temperature. The equation implies that *BU* has a fixed value of 0.54 if *Δt* is less than 12°C.

 

Since wind speed is usually measured at a height of 10 m, the following correction is made (Maidment (1993), p. 4.36):

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image046.gif)                                                                                        (2-21)

 

where *u(10)* is  the measured wind speed at 10 m height [m s-1].

 

Similar to the calculation of the net absorbed radiation, the evaporative demand is calculated for three cases: for a reference vegetation canopy (using *fc* =1.0), a bare soil surface (*fc* =0.75), and an open water surface (*fc* =0.5).  

## Psychrometric constant

The psychrometric constant at sea level can be calculated as:

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image048.gif)                                                                                              (2-22)

 

where:

 

| *γ0* | : Psychrometric   constant at sea level (about 0.67) [mbar °C-1] |
| ---- | ------------------------------------------------------------ |
| *P0* | : Atmospheric   pressure at sea level [mbar]                 |
| *L*  | : Latent heat of   vaporization [MJ kg-1]                    |

 

Since the barometric pressure changes with altitude, so does the psychrometric constant. The following altitude correction is applied (Allen *et al*., 1998):

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image050.gif)                                                                       (2-23)

 

where:

 

| *γ(z)* | : Psychrometric   constant at altitude *z* [mbar °C-1] |
| ------ | ------------------------------------------------------ |
| *z*    | : Altitude above   sea level [m]                       |

## Slope of the saturation vapour pressure curve

The slope of the saturation vapour pressure curve is calculated as follows:

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image052.gif)                                                                             (2-24)

 

where *Δ* is in [mbar °C-1].

## Potential evapo(transpi)ration

As explained before, potential evapo(transpi)ration is calculated for three reference surfaces:

1. A closed canopy of some reference crop      (*ET0*)
2. A bare      soil surface (*ES0*)
3. An open water surface (*EW0*)

 

These quantities are all calculated using Equation 1, using different values for the net absorbed radiation (*Rna*) and evaporative demand (*EA*): 

 

![img](file:///C:\Users\thiemve\AppData\Local\Temp\msohtmlclip1\01\clip_image054.gif)                                                                                    (2-25)  

 

where:

 

| *ET0*   | : Potential   evapotranspiration for reference crop [mm day-1] |
| ------- | ------------------------------------------------------------ |
| *ES0*   | : Potential   evaporation for bare soil surface [mm day-1]   |
| *EW0*   | : Potential   evaporation for open water surface [mm day-1]  |
| *Rna*   | : Net absorbed   radiation, reference crop [mm day-1]        |
| *Rna,s* | : Net absorbed   radiation, bare soil surface [mm day-1]     |
| *Rna,w* | : Net absorbed   radiation, open water surface [mm day-1]    |
| *EA*    | : Evaporative   demand, reference crop [mm day-1]            |
| *EAs*   | : Evaporative   demand, bare soil surface [mm day-1]         |
| *EAw*   | : Evaporative   demand, open water surface [mm day-1]        |
| *Δ*     | : Slope of the   saturation vapour pressure curve [mbar °C-1] |
| *γ*     | : Psychrometric   constant [mbar °C-1]                       |

 

 

 

 

------

[[1\]](#_ftnref1) Note that this term is mistakenly called ‘net outgoing longwave radiation’ in the WODOST/CGMS documentation (Supit et. al.,2003), whereas it is in fact the net longwave radiation