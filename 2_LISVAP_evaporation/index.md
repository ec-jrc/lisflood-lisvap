# 2. Potential reference evapotranspiration and evaporation

## Penman-Monteith equation

Reference values for potential evapotranspiration and evaporation are estimated using the Penman-Monteith equation (Supit *et al*., 1994, Supit & Van Der Goot, 2003):

$$
ET0 = \frac{\Delta R_{na} + \gamma EA}{\Delta + \gamma}
$$

where:
<br/>   $ET0$	Potential evapotranspiration rate from a closed vegetation canopy (reference crop) $[\frac{mm}{day}]$
<br/>   $R_{na}$	Net absorbed radiation $[\frac{mm}{day}]$
<br/>   $EA$	Evaporative demand of the atmosphere $[\frac{mm}{day}]$
<br/>   $\Delta$		Slope of the saturation vapour pressure curve $[\frac{mbar}{^\circ C}]$
<br/>   $\gamma$		Psychrometric constant $[\frac{mbar}{^\circ C}]$	

 

The same equation is also used to estimate potential evaporation from a water surface and the evaporation from a (wet) bare soil surface (by using different values for the absorbed radiation term, $R_{na}$). The procedure to calculate potential evapo(transpi)ration is summarised in the following Figure. 

 

![img](..\media\figure1.jpg)

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

Calculating the net absorbed radiation term involves the following four steps:

1. Calculate the daily extra-terrestrial radiation (Angot radiation)
2. From the Angot radiation, calculate the daily incoming solar radiation (using information on the daily number of sunshine hours or cloud cover, if available)
3. Calculate the daily net long-wave radiation (based on meteorological conditions)
4. Calculate the net absorbed radiation

 

Some data sets (e.g. ERA5) provide pre-calculated values for both incoming solar radiation and net long-wave radiation. Because of this, LISVAP offers the possibility to use these values directly, in which case all radiation balance calculations (except for the Angot radiation) are bypassed.  

### Step 1: Angot radiation

The daily extra-terrestrial radiation is the product of the solar constant at the top of the atmosphere and the integral of the solar height over the day:

$$
R_{a,d} = S_{c, d} \int sin \ \beta \ dt_h
$$

where:
<br/>   $R_{a,d}$		Daily extra-terrestrial radiation $[{\frac{J}{m^2 \ day}}]$
<br/>   $S_{c,d}$		Solar constant   at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$
<br/>   $\int sin \ \beta \ dt_h$	Integral of the solar height over the day $[s]$
 

The solar constant on a given day is calculated as:

$$
S_{c, d} = S_c(1 + 0.033 \cos[\frac{360 \ t_d}{365}])
$$

where:
<br/>   $S_c$		 Average solar radiation at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$ (= 1370 ${\frac{J}{m^2 \ s}}$)
<br/>   $S_{c,d}$	Solar constant at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$
<br/>   $t_d$		Calendar day number (1st of January is 1, etcetera) $[-]$
 

The calendar day number is always a number between 1 and 365.25 (taking into account leap years, a year has on average 365.25 days). 

 

The integral of the solar height equals:

$$
\int sin \beta \ dt_h = 3600(L_d \cdot sin \ \delta \cdot sin \ \lambda + \frac{24}{\pi} \cdot cos \ \delta \cdot cos \ \lambda \cdot \sqrt{1-(tan \ \delta \cdot tan \ \lambda)^2})
$$

where:
<br/>   $L_d$	Astronomical day length $[h]$
<br/>   $\delta$		Solar declination $[^\circ]$
<br/>   $\lambda$		Latitude $[^\circ]$


The solar declination is a simple function of the calendar day number (*td*):

$$
\delta = -23.45 \cdot cos[\frac{360(t_d + 10)}{365}]
$$

Day length is given by:

 $$  \begin{cases} L_d = 12+ \frac{24}{180} \alpha sin(B_{ld})   &[B_{ld} \ge 0]\ L_d = 12+ \frac{24}{180} [\alpha sin(B_{ld}) - 360] & [B_{ld} < 0]\end{cases} $$ 

 
with:

$$
B_{ld} = \frac{-sin (\frac{PD}{\pi})+sin \ \delta \cdot sin \ \lambda}{cos \ \delta \cdot \ \lambda}
$$

where *PD* is a correction constant (-2.65).

### Step 2: Incoming solar radiation

Depending on the availability of input data, three equations are available to calculate the incoming solar radiation. If the number of sunshine hours on a particular day is known, the Ångström equation is used:

$$
R_{g,d} = R_{a,d}(A_a + B_a \frac{n}{L_d})
$$

where:
<br/>   $R_{g,d}$		 Incoming daily global solar radiation $[{\frac{J}{m^2 \ day}}]$
<br/>   $R_{a,d}$		Daily extra-terrestrial radiation (Angot radiation) $[{\frac{J}{m^2 \ day}}]$
<br/>   $n$			Number of bright sunshine hours per day $[h]$
<br/>   $L_d$		Astronomical day length $[h]$
<br/>   $A_a, B_a$		Empirical constants $[-]$

In the absence of any observed information on the number of sunshine hours, the following equation is used if cloud cover observations are available (Supit, 1994; Supit & Van Kappel, 1998):

$$
R_{g,d}= R_{a,d}(A_s \sqrt{(T_{max}-T_{min})} + B_h \sqrt{(1-\frac{CC}{8})}+C_s)
$$

where:
<br/>   $T_{max}$		Maximum temperature $[^\circ C]$
<br/>   $T_{min}$		Minimum temperature $[^\circ C]$
<br/>   $CC$		Mean total cloud cover during the day $[octas]$
<br/>   $L_d$		Astronomical day length $[h]$
<br/>   $A_s$		Empirical constant $[^\circ C - 0.5]$
<br/>   $B_s$		Empirical constant $[-]$
<br/>   $C_s$		Empirical constant $[{\frac{J}{m^2 \ day}}]$


If neither sunshine duration nor cloud cover observations are available, the Hargreaves equation is used instead:

$$
R_{g,d}= R_{a,d} \cdot A_h \sqrt{(T_{max}-T_{min})}+B_h
$$

where:
<br/>   $A_h$		Empirical constant $[^\circ C - 0.5]$
<br/>   $B_h$		Empirical constant $[{\frac{J}{m^2 \ day}}]$
 

### Step 3: Net long-wave radiation 

The following equation is used to calculate the net long-wave radiation[[1\]](#_ftn1) (Maidment, 1993):

$$
R_{nl}= f \epsilon' \sigma (T_{av}+273)^4
$$

where:
<br/>   $R_{nl}$		Net long-wave radiation $[{\frac{J}{m^2 \ day}}]$
<br/>   $\sigma$			Stefan Boltzmann constant:  $4.9 \cdot 10^{-3}[{\frac{J}{m^2 \ K^4 \ day}}]$
<br/>   $f$			Adjustment factor for cloud cover
<br/>   $\epsilon'$			Net emissivity between the atmosphere and the ground


The net emissivity is calculated as:

$$
\epsilon = 0.56 - 0.079 \sqrt{e_a}
$$

with: 
<br/>   $e_a$			Actual vapour pressure $[mbar]$


Synoptic weather stations often do not supply vapour pressure data, but provided dew point temperature instead. In that case *ea* can be calculated using the following equation by Goudriaan (1977):

$$
e_a = 6.10588 \cdot e^{\frac{17.32491 \cdot T_{dew}}{T_{dew}+238.102}}
$$

with:
<br/>   $T_{dew}$		dew point temperature $[^\circ C]$
 

The equation of Brunt (1932) is used to estimate the cloud cover factor:

$$
f= (B_e + B_f \frac{n}{L_d})
$$

where:
<br/>   $B_e, B_f$	Constants according to Brunt (1932) (depend on latitude) [-]
 

If no information on the number of bright sunshine hours is available, the relative sunshine duration term is estimated using the Ångström equation:

$$
\frac{n}{L_d}= \frac{(\frac{R_{g,d}}{R_{a,d}})-A_a}{B_a}
$$

where *Aa* and *Ba* are the empirical Ångström constants.

### Step 4: Net absorbed radiation 

Finally, the net absorbed radiation [mm day-1] is calculated as:

$$
R_{na}=\frac{(1- \alpha)R_{gd}-R_{nl}}{L}
$$

where *α* is the albedo (reflection coefficient) of the surface, and *L* is the latent heat of vaporization $[\frac{MJ}{kg}]$:

$$
L=2.501-2.361 \cdot 10^{-3} \cdot T_{av}
$$

The net absorbed radiation is calculated for three cases: for a reference vegetation canopy (using $\alpha=0.23$), a bare soil surface ($\alpha=0.15$), and an open water surface ($\alpha=0.05$)


## Evaporative demand of the atmosphere

The evaporative demand of the atmosphere is calculated as:

$$
EA= 0.26(e_s-e_a)(f_c+BU \cdot u(2))
$$

where:
<br/>   $EA$		Evaporative demand $[\frac{mm}{day}]$
<br/>   $e_s$			Saturated vapour pressure $[mbar]$
<br/>   $e_a$			Actual vapour pressure $[mbar]$
<br/>   $f_c$			Empirical   constant $[-]$
<br/>   $BU$		Coefficient in wind function $[-]$
<br/>   $u(2)$		Mean wind speed at 2 m height $[\frac{m}{s}]$


Saturated vapour pressure is calculated as a function of mean daily air temperature:

$$
e_s= 6.10588 \cdot e^{\frac{17.32491 \cdot T_{av}}{T_{av}+238.102}}
$$

The coefficient in the wind function, $BU$, is also temperature dependent:

$$
BU=max[0.54+0.35 \frac{\Delta T-12}{4}, 0.54]
$$

Here, $\Delta T$ is the difference between the daily maximum and minimum temperature. The equation implies that $BU$ has a fixed value of 0.54 if $\Delta T$ is less than 12°C.


Since wind speed is usually measured at a height of 10 m, the following correction is made (Maidment (1993), p. 4.36):

$$
u(2)=0.749 \cdot u(10)
$$

where $u(10)$ is  the measured wind speed at 10 m height $[\frac{m}{s}]$.
 

Similar to the calculation of the net absorbed radiation, the evaporative demand is calculated for three cases: for a reference vegetation canopy (using $fc =1.0$), a bare soil surface ($fc =0.75$), and an open water surface ($fc =0.5$).  

## Psychrometric constant

The psychrometric constant at sea level can be calculated as:

$$
\gamma_0 = 0.00163 \frac{P_0}{L}
$$

where:
<br/>   $\gamma_0$			Psychrometric   constant at sea level (about 0.67) $[\frac{mbar}{^\circ C}]$
<br/>   $P_0$		Atmospheric   pressure at sea level $[mbar]$
<br/>   $L$			Latent heat of   vaporization $[\frac{MJ}{kg}]$ 
 

Since the barometric pressure changes with altitude, so does the psychrometric constant. The following altitude correction is applied (Allen *et al*., 1998):

$$
\gamma(z)= \gamma_0(\frac{293-0.0065 \cdot z}{293})^{5.26}
$$

where:
<br/>   $\gamma(z)$		Psychrometric constant at altitude *z* $[\frac{mbar}{^\circ C}]$
<br/>   $z$			Altitude above sea level $[m]$

## Slope of the saturation vapour pressure curve

The slope of the saturation vapour pressure curve is calculated as follows:

$$
\Delta=\frac{238.102 \cdot 17.32491 \cdot e_s}{(T+238.102)^2}
$$

where $\Delta$ is in $[\frac{mbar}{^\circ C}]$.

## Potential evapo(transpi)ration

As explained before, potential evapo(transpi)ration is calculated for three reference surfaces:

1. A closed canopy of some reference crop (*ET0*)
2. A bare soil surface (*ES0*)
3. An open water surface (*EW0*)
 

These quantities are all calculated using Equation 1, using different values for the net absorbed radiation (*Rna*) and evaporative demand (*EA*): 
$$
ET0 = \frac{\Delta R_{na}+\gamma EA}{\Delta + \gamma}
$$

$$
ES0 = \frac{\Delta R_{na,s}+\gamma EA_s}{\Delta + \gamma}
$$

$$
EW0 = \frac{\Delta R_{na,w}+\gamma EA_w}{\Delta + \gamma}
$$

where:
<br/>   $ET0$		Potential evapotranspiration for reference crop $[\frac{mm}{day}]$
<br/>   $ES0$		Potential evaporation for bare soil surface $[\frac{mm}{day}]​$
<br/>   $EW0$		Potential evaporation for open water surface $[\frac{mm}{day}]$
<br/>   $R_{na}$		Net absorbed radiation, reference crop $[\frac{mm}{day}]$
<br/>   $R_{na,s}$		Net absorbed radiation, bare soil surface $[\frac{mm}{day}]$
<br/>   $R_na,w$	Net absorbed radiation, open water surface $[\frac{mm}{day}]$
<br/>   $EA$		Evaporative demand, reference crop $[\frac{mm}{day}]$
<br/>   $EA_s$		Evaporative demand, bare soil surface $[\frac{mm}{day}]$
<br/>   $EA_w$		Evaporative demand, open water surface $[\frac{mm}{day}]$
<br/>   $\Delta$			Slope of the saturation vapour pressure curve $[\frac{mbar}{^\circ C}]$
<br/>   $\gamma$			Psychrometric constant $[\frac{mbar}{^\circ C}]$



------

[[1\]](#_ftnref1) Note that this term is mistakenly called ‘net outgoing longwave radiation’ in the WODOST/CGMS documentation (Supit et. al.,2003), whereas it is in fact the net longwave radiation
