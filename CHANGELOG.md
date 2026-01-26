
# Change Log

All notable changes to this project will be documented in this file.



## v1.4.0 (2026-01-23)
--------------------------------------------------------------------------------
- Remove pcraster from the code
- Validation of the units in the input files configured in the settings file
- Introduction of variable Relative Humidity to calculate Vapor Pressure
- Define in the settings file conversion factors for the input files meteo units.
- Add test for RelHumidity and 360_Cal
- Add timestep validation in the unit tests
- Correct RG readmeteo and arcsin and unit conversion
- Remove of tss files processing
- Remove Python2 support
- Convert start/end dates to the same as the input calendar type
- Correct vulnerability in futures lib
- Add git actions and update requirements
- Correction and update of the docker container.
- Switched from Git LFS to regular Git files

## v1.3.1 (2024-10-09)
--------------------------------------------------------------------------------
- Allow reading files from the middle of the dataset

## v1.3.0 (2024-03-19)
--------------------------------------------------------------------------------
- New feature that allows run with subdaily grids
- Updated docker file
- Correct output files splitting
- Fixed usecase copy issue in Docker

## v1.2.9 (2024-01-22)
--------------------------------------------------------------------------------
- Missing pyproj in install requirements

## v1.2.8 (2024-01-22)
--------------------------------------------------------------------------------
- Enforce limit of PD Values
- Add settings file verification rule
- Allow output monthly files

## v1.2.7 (2023-05-16)
--------------------------------------------------------------------------------
- Allow reading netCDF variables in any order

## v1.2.6 (2023-03-16)
--------------------------------------------------------------------------------
- Correct solar radiation NaN value

## v1.2.5 (2022-07-27)
--------------------------------------------------------------------------------
- Refactor formulas selection
- Change variables to a more suitable name that exists in the documentation

## v1.2.0 (2022-07-20)
--------------------------------------------------------------------------------
- Solar Constant inside Angot Radiation calculation uses radians instead of degrees
- Fixed low evapotranspiration "stripe" in north pole during summer days (EFCC-2823)

## v1.1.0 (2022-07-14)
--------------------------------------------------------------------------------
- Remove STOWA reference
- Use only the FAO formula (JRC-5431)

## v1.0.6 (2022-07-14)
--------------------------------------------------------------------------------
- Solar Constant inside Angot Radiation calculation uses radians instead of degrees (JRC-5439)
- Correct validate settings not to test existence of EAct for CORDEX
- Set some default values to correspond to the documentation.
- Change the reference maps in tests to reflect the usage of the FAO formula in EFAS setup.
- Update the default settings.
- Change LatHeatVap to use only the FAO formula in all setups EFAS, GLOFAS, CORDEX.
- Automatic validation of the settings file.
- Create functions for reading temperatures, windspeed and vapor pressure
- Correct BU constant in windspeed formula
- Create a python function for latent heat of vaporization
- Code review to allow the users to choose different input file configurations and not be
  limited by the options EFAS, GLOFAS and CORDEX.

## v1.0.5 (2022-06-22)
--------------------------------------------------------------------------------
- Settings options case insensitive.
- Correct 6h output time units and some settings variables
- Docker image build update

## v1.0.4 (2021-07-26)
--------------------------------------------------------------------------------
- Improved calendar management
- Corrected calendar management tests
- Solved 365_day calendar in Lisvap issue

## v1.0.2 (2021-05-21)
--------------------------------------------------------------------------------
- Fix setup
- Correct versioning for pip

## v1.0.1 (2021-05-21)
--------------------------------------------------------------------------------
- Correct setup.py
- Correct version for pip install.

## v1.0.0 (2021-03-11)
--------------------------------------------------------------------------------
- Allow generating output by year (EFCC-2317)
- Create test case for yearly IO.
- Rewrite write netcdf.
- Add test settings file for efas 1arcmin
- Add gitignore file to the efas_1arcmin output folder

## v0.5.0 (2021-01-28)
--------------------------------------------------------------------------------
- New 1arcmin support
- Correct the 1 arcmin output (EFCC-1872) and also output 6 hourly maps (EFCC-2316)
- Avoid error when projection doesn't have spatial_ref.
- Set esri_pe_string from proj only if projection is defined.
- Add another common projection variable name.
- Setting variable grid_mapping only if projection exists
- Correct rounding issue.
- Correct indexes calculation on input files.
- Make lisvap process and generate 1 arc min maps

## v0.4.4 (2020-03-27)
--------------------------------------------------------------------------------
- fix generation of mv(no data) when rn -9999
- fix to setup.py

## v0.4.3 (2020-02-17)
--------------------------------------------------------------------------------
- Method to find variable inside a netcdf
- Dockerfile python 3.7 based
- docker image with tests; if tests fail the build does not complete

## v0.4.2 (2019-08-23)
--------------------------------------------------------------------------------
- Replaced pathlib with pathlib2 in Python2

## v0.4.1 (2019-08-23)
--------------------------------------------------------------------------------
- Use pathlib for handling paths
- Fixed missing tag in XML settings template

## v0.4.0 (2019-08-19)
--------------------------------------------------------------------------------
- Remove large files to avoid GH001
- Using less days for glofas tests because of github file size limits
- moving operators to a module to facilitate migration to numpy operations
- fixed bug in MaskMapMetadata class preventing to correctly change clone map


## v0.3.6 (2019-06-18)
--------------------------------------------------------------------------------
- Refactored tests
- Refactored tests structure
- Using formula for RN instead of forcing maps
- Add forcings for glofas
- Adding test for glofas
- Added CORDEX forcing entries in settings_tpl.xml
- Corrected units of solar radiation maps in settings file


## v0.3.5 (2019-05-24)
--------------------------------------------------------------------------------
- Bumped version 0.3.5
- Bugfix FillValue AttributeError


## v0.3.4 (2019-05-24)
--------------------------------------------------------------------------------
- Add bin script lisvap
- Setup upload command
- Docker image with python3.5
- Tox tests for py27,35,36,37


## v0.3.3 (2019-04-24)
--------------------------------------------------------------------------------
- pip package description
- Removed unused options InitLisflood and IinitLisfloodWithoutSplit
- Minor edits
- Updated requirements


## v0.3.2 (2019-04-19)
--------------------------------------------------------------------------------
- New working test
- New docker available

## v0.0.1 (2019-02-18)
--------------------------------------------------------------------------------
- Inital release of open source Lisvap
