# 2. Potential reference evapo(trans)piration

## Penman-Monteith equation

Reference values for **potential evapotranspiration and evaporation** are estimated using the Penman-Monteith equation (Supit *et al*., 1994, Supit & Van Der Goot, 2003):

$$
ET0 = \frac{\Delta R_{na} + \gamma EA}{\Delta + \gamma}
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$ET0$:&nbsp;&nbsp; Potential evapotranspiration rate from a closed vegetation canopy (reference crop) $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{na}$:&nbsp;&nbsp;	Net absorbed radiation $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EA$:&nbsp;&nbsp;	Evaporative demand of the atmosphere $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\Delta$:&nbsp;&nbsp;		Slope of the saturation vapour pressure curve $[\frac{mbar}{^\circ C}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\gamma$:&nbsp;&nbsp;		Psychrometric constant $[\frac{mbar}{^\circ C}]$

The same equation is also used to estimate potential evaporation from a water surface and the evaporation from a (wet) bare soil surface (by using different values for the absorbed radiation term, $R_{na}$). 

**potential evaporation rate from a bare soil surface [mm/day]** 

$$
ES = \frac{\Delta R_{nasoil} + \gamma EA_{soil}}{\Delta + \gamma}
$$

**potential evaporation rate from water surface [mm/day]**

$$
EW = \frac{\Delta R_{nawater} + \gamma EA_{water}}{\Delta + \gamma}
$$


The procedure to calculate potential evapo(transpi)ration is summarised in the following Figure.

 

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

The **daily extra-terrestrial radiation** is the product of the solar constant at the top of the atmosphere and the integral of the solar height over the day:

$$
R_{a,d} = S_{c, d} \int sin \ \beta \ dt_h
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{a,d}$:&nbsp;&nbsp;		Daily extra-terrestrial radiation $[{\frac{J}{m^2 \ day}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$S_{c,d}$:&nbsp;&nbsp;		Solar constant   at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\int sin \ \beta \ dt_h$:&nbsp;&nbsp;	Integral of the solar height over the day $[s]$
 

<br/> The **solar constant** on a given day is calculated as:

$$
S_{c, d} = S_c(1 + 0.033 \cos[\frac{360 \ t_d}{365}])
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$S_c$:&nbsp;&nbsp;		 Average solar radiation at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$ (= 1370 ${\frac{J}{m^2 \ s}}$)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$S_{c,d}$:&nbsp;&nbsp;	Solar constant at the top of the atmosphere $[{\frac{J}{m^2 \ s}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$t_d$:&nbsp;&nbsp;		Calendar day number (1st of January is 1, etcetera) $[-]$
 

<br/> The calendar day number is always a number between 1 and 365.25 (taking into account leap years, a year has on average 365.25 days). 

 

<br/> The **integral of the solar height** equals:

$$
\int sin \beta \ dt_h = 3600(L_d \cdot sin \ \delta \cdot sin \ \lambda + \frac{24}{\pi} \cdot cos \ \delta \cdot cos \ \lambda \cdot \sqrt{1-(tan \ \delta \cdot tan \ \lambda)^2})
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$L_d$:&nbsp;&nbsp;	Astronomical day length $[h]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\delta$:&nbsp;&nbsp;		Solar declination $[^\circ]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\lambda$:&nbsp;&nbsp;		Latitude $[^\circ]$


<br/> The **solar declination** is a simple function of the calendar day number (*td*):

$$
\delta = -23.45 \cdot cos[\frac{360(t_d + 10)}{365}]
$$

**Day length** is given by:

 $$  \begin{cases} L_d = 12+ \frac{24}{180} \alpha sin(B_{ld})   &[B_{ld} \ge 0]\\ L_d = 12+ \frac{24}{180} [\alpha sin(B_{ld}) - 360] & [B_{ld} < 0]\end{cases} $$ 

 
with:

$$
B_{ld} = \frac{-sin (\frac{PD}{\pi})+sin \ \delta \cdot sin \ \lambda}{cos \ \delta \cdot \ \lambda}
$$

where *PD* is a correction constant (-2.65).

### Step 2: Incoming solar radiation

Depending on the availability of input data, three equations are available to calculate the incoming solar radiation. *If the number of sunshine hours on a particular day is known*, the Ångström equation is used:

$$
R_{g,d} = R_{a,d}(A_a + B_a \frac{n}{L_d})
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{g,d}$:&nbsp;&nbsp;		 Incoming daily global solar radiation $[{\frac{J}{m^2 \ day}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{a,d}$:&nbsp;&nbsp;		Daily extra-terrestrial radiation (Angot radiation) $[{\frac{J}{m^2 \ day}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$n$:&nbsp;&nbsp;			Number of bright sunshine hours per day $[h]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$L_d$:&nbsp;&nbsp;		Astronomical day length $[h]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$A_a, B_a$:&nbsp;&nbsp;		Empirical constants $[-]$

In the absence of any observed information on the number of sunshine hours, the following equation is used if cloud cover observations are available (Supit, 1994; Supit & Van Kappel, 1998):

$$
R_{g,d}= R_{a,d}(A_s \sqrt{(T_{max}-T_{min})} + B_h \sqrt{(1-\frac{CC}{8})}+C_s)
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$T_{max}$:&nbsp;&nbsp;		Maximum temperature $[^\circ C]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$T_{min}$:&nbsp;&nbsp;		Minimum temperature $[^\circ C]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$CC$:&nbsp;&nbsp;		Mean total cloud cover during the day $[octas]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$L_d$:&nbsp;&nbsp;		Astronomical day length $[h]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$A_s$:&nbsp;&nbsp;		Empirical constant $[^\circ C - 0.5]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$B_s$:&nbsp;&nbsp;		Empirical constant $[-]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$C_s$:&nbsp;&nbsp;		Empirical constant $[{\frac{J}{m^2 \ day}}]$


*If neither sunshine duration nor cloud cover observations are available*, the Hargreaves equation is used instead:

$$
R_{g,d}= R_{a,d} \cdot A_h \sqrt{(T_{max}-T_{min})}+B_h
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$A_h$:&nbsp;&nbsp;		Empirical constant $[^\circ C - 0.5]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$B_h$:&nbsp;&nbsp;		Empirical constant $[{\frac{J}{m^2 \ day}}]$
 

### Step 3: Net long-wave radiation 

The following equation is used to calculate the **net long-wave radiation**[[1\]](#_ftn1) (Maidment, 1993):

$$
R_{nl}= f \epsilon' \sigma (T_{av}+273)^4
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{nl}$:&nbsp;&nbsp;		Net long-wave radiation $[{\frac{J}{m^2 \ day}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\sigma$:&nbsp;&nbsp;			Stefan Boltzmann constant:  $4.9 \cdot 10^{-3}[{\frac{J}{m^2 \ K^4 \ day}}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$f$:&nbsp;&nbsp;			Adjustment factor for cloud cover<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\epsilon'$:&nbsp;&nbsp;			Net emissivity between the atmosphere and the ground


The **net emissivity** is calculated as:

$$
\epsilon = 0.56 - 0.079 \sqrt{e_a}
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$e_a$:&nbsp;&nbsp;			Actual vapour pressure $[mbar]$


Synoptic weather stations often do not supply vapour pressure data, but provided dew point temperature instead. In that case the **actual vapour pressure** *ea* can be calculated using the following equation by Goudriaan (1977):

$$
e_a = 6.10588 \cdot e^{\frac{17.32491 \cdot T_{dew}}{T_{dew}+238.102}}
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$T_{dew}$:&nbsp;&nbsp;		dew point temperature $[^\circ C]$
 

The equation of Brunt (1932) is used to estimate the **cloud cover factor**:

$$
f= (B_e + B_f \frac{n}{L_d})
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$B_e, B_f$:&nbsp;&nbsp;	Constants according to Brunt (1932) (depend on latitude) [-]
 

*If no information on the number of bright sunshine hours is available*, the **relative sunshine duration term** is estimated using the Ångström equation:

$$
\frac{n}{L_d}= \frac{(\frac{R_{g,d}}{R_{a,d}})-A_a}{B_a}
$$

where *Aa* and *Ba* are the empirical Ångström constants.

### Step 4: Net absorbed radiation 

Finally, the **net absorbed radiation** [mm day-1] is calculated as:

$$
R_{na}=\frac{(1- \alpha)R_{gd}-R_{nl}}{L}
$$

where *α* is the albedo (reflection coefficient) of the surface, and *L* is the latent heat of vaporization $[\frac{MJ}{kg}]$:&nbsp;&nbsp;

$$
L=2.501-2.361 \cdot 10^{-3} \cdot T_{av}
$$

The net absorbed radiation is calculated for three cases: for a reference vegetation canopy (using $\alpha=0.23$), a bare soil surface ($\alpha=0.15$), and an open water surface ($\alpha=0.05$)


## Evaporative demand of the atmosphere

The **evaporative demand** of the atmosphere is calculated as:

$$
EA= 0.26(e_s-e_a)(f_c+BU \cdot u(2))
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EA$:&nbsp;&nbsp;		Evaporative demand $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$e_s$:&nbsp;&nbsp;			Saturated vapour pressure $[mbar]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$e_a$:&nbsp;&nbsp;			Actual vapour pressure $[mbar]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$f_c$:&nbsp;&nbsp;			Empirical   constant $[-]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$BU$:&nbsp;&nbsp;		Coefficient in wind function $[-]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$u(2)$:&nbsp;&nbsp;		Mean wind speed at 2 m height $[\frac{m}{s}]$


**Saturated vapour pressure** is calculated as a function of mean daily air temperature:

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

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\gamma_0$:&nbsp;&nbsp;			Psychrometric   constant at sea level (about 0.67) $[\frac{mbar}{^\circ C}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$P_0$:&nbsp;&nbsp;		Atmospheric   pressure at sea level $[mbar]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$L$:&nbsp;&nbsp;			Latent heat of   vaporization $[\frac{MJ}{kg}]$
 

Since the barometric pressure changes with altitude, so does the psychrometric constant. The following altitude correction is applied (Allen *et al*., 1998):

$$
\gamma(z)= \gamma_0(\frac{293-0.0065 \cdot z}{293})^{5.26}
$$

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\gamma(z)$:&nbsp;&nbsp;		Psychrometric constant at altitude *z* $[\frac{mbar}{^\circ C}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$z$:&nbsp;&nbsp;			Altitude above sea level $[m]$

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

where<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$ET0$:&nbsp;&nbsp;		Potential evapotranspiration for reference crop $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$ES0$:&nbsp;&nbsp;		Potential evaporation for bare soil surface $[\frac{mm}{day}]​$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EW0$:&nbsp;&nbsp;		Potential evaporation for open water surface $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{na}$:&nbsp;&nbsp;		Net absorbed radiation, reference crop $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_{na,s}$:&nbsp;&nbsp;		Net absorbed radiation, bare soil surface $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$R_na,w$:&nbsp;&nbsp;	Net absorbed radiation, open water surface $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EA$:&nbsp;&nbsp;		Evaporative demand, reference crop $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EA_s$:&nbsp;&nbsp;		Evaporative demand, bare soil surface $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$EA_w$:&nbsp;&nbsp;		Evaporative demand, open water surface $[\frac{mm}{day}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\Delta$:&nbsp;&nbsp;			Slope of the saturation vapour pressure curve $[\frac{mbar}{^\circ C}]$<br/>
&nbsp;&nbsp;&nbsp;&nbsp;$\gamma$:&nbsp;&nbsp;			Psychrometric constant $[\frac{mbar}{^\circ C}]$



------

[[1\]](#_ftnref1) Note that this term is mistakenly called ‘net outgoing longwave radiation’ in the WODOST/CGMS documentation (Supit et. al.,2003), whereas it is in fact the net longwave radiation
