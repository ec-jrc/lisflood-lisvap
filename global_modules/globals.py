"""

Copyright 2018 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

"""

global cutmap

cutmap = [0, 1, 0, 1]
cdfFlag = [0, 0, 0]  # flag for netcdf output for all, steps and end

global timeMes, TimeMesString, timeMesSum
# global modelSteps  # CM: list of start and end time step for the model (modelSteps[0] = start; modelSteps[1] = end)
timeMes = []
timeMesString = []  # name of the time measure - filled in dynamic
timeMesSum = []  # time measure of hydrological modules
# ----------------------------------
