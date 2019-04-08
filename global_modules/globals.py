# -------------------------------------------------------------------------
# Name:        globals
# Purpose:
#
# Author:      burekpe
#
# Created:     26/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

# global binding, option, ReportSteps
global MMaskMap, maskmapAttr, bigmapAttr, cutmap, metadataNCDF

# binding = {}
# option = {}

# reportTimeSerieAct = {}
# reportMapsAll = {}
# reportMapsSteps = {}
# reportMapsEnd = {}

MMaskMap = 0
# ReportSteps = {}

maskmapAttr = {}
bigmapAttr = {}
cutmap = [0, 1, 0, 1]
cdfFlag = [0, 0, 0]  # flag for netcdf output for all, steps and end
metadataNCDF = {}

global timeMes, TimeMesString, timeMesSum
global modelSteps  # CM: list of start and end time step for the model (modelSteps[0] = start; modelSteps[1] = end)
timeMes = []
timeMesString = []  # name of the time measure - filled in dynamic
timeMesSum = []  # time measure of hydrological modules
modelSteps = []
# ----------------------------------
