# -------------------------------------------------------------------------
# Name:        addmodule1
# Purpose:
#
# Author:      burekpe
#
# Created:     26/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------

import warnings
import datetime
import time as xtime
import os
from bisect import bisect_left

import numpy as np
from pcraster import pcraster, numpy_operations, Nominal, Boolean, Scalar, operations
from netCDF4 import num2date, date2num, Dataset

from .zusatz import LisfloodError, iterOpenNetcdf, iterSetClonePCR, iterReadPCRasterMap, checkmap, Calendar
from .globals import binding, metadataNCDF, maskmapAttr, Flags, cutmap


def defsoil(name1, name2=None, name3=None):
    """ loads 3 array in a list
    """
    try:
        in1 = loadmap(name1)
    except:
        in1 = name1
    if name2 is None:
        in2 = in1
    else:
        try:
            in2 = loadmap(name2)
        except:
            in2 = name2
    if name3 is None:
        in3 = in1
    else:
        try:
            in3 = loadmap(name3)
        except:
            in3 = name3
    return [in1, in2, in3]


def valuecell(mask, coordx, coordstr):
    """
    to put a value into a pcraster map -> invert of cellvalue
    pcraster map is converted into a numpy array first
    """
    coord = []
    for xy in coordx:
        try:
            coord.append(float(xy))
        except ValueError:
            msg = 'Gauges: {} in {} is not a coordinate'.format(xy, coordstr)
            raise LisfloodError(msg)

    null = np.zeros((pcraster.clone().nrRows(), pcraster.clone().nrCols()))
    null[null == 0] = -9999

    for i in xrange(int(len(coord) / 2)):
        col = int((coord[i * 2] - pcraster.clone().west()) / pcraster.clone().cellSize())
        row = int((pcraster.clone().north() - coord[i * 2 + 1]) / pcraster.clone().cellSize())
        if 0 <= col < pcraster.clone().nrCols() and 0 <= row < pcraster.clone().nrRows():
            null[row, col] = i + 1
        else:
            msg = 'Coordinates: {}, {} to put value in is outside mask map - col,row: {}, {}'.format(coord[i * 2], coord[i * 2 + 1], col, row)
            raise LisfloodError(msg)

    return numpy_operations.numpy2pcr(Nominal, null, -9999)


def metaNetCDF(name):
    """
    get the map metadata from netcdf
    """
    filename = name.split('.')[0] + '.nc'
    if not (os.path.isfile(filename)):
        msg = "Checking netcdf map extend \n" + filename + " does not exists"
        raise LisfloodError(msg)
    nf1 = Dataset(filename, 'r')
    for var in nf1.variables:
        metadataNCDF[var] = nf1.variables[var].__dict__
    nf1.close()


def mapattrNetCDF(name):
    """
    get the map attributes like col, row etc from a ntcdf map
    and define the rectangular of the mask map inside the netcdf map
    """
    filename = os.path.splitext(name)[0] + '.nc'
    nf1 = iterOpenNetcdf(filename, "Checking netcdf map \n", 'r')
    # original code
    # x1, x2, y1, y2 = [round(nf1.variables.values()[var_ix][j], 5) for var_ix in range(2) for j in range(2)]
    # new safer code that doesn't rely on a specific variable order in netCDF file (R.COUGHLAN & D.DECREMER)
    if 'lon' in nf1.variables.keys():
        x1 = nf1.variables['lon'][0]
        x2 = nf1.variables['lon'][1]
        y1 = nf1.variables['lat'][0]
        y2 = nf1.variables['lat'][1]
    else:
        x1 = nf1.variables['x'][0]
        x2 = nf1.variables['x'][1]
        y1 = nf1.variables['y'][0]
        y2 = nf1.variables['y'][1]
    nf1.close()
    if maskmapAttr['cell'] != round(np.abs(x2 - x1), 5) or maskmapAttr['cell'] != round(np.abs(y2 - y1), 5):
        raise LisfloodError("Cell size different in maskmap {} and {}".format(binding['MaskMap'], filename))
    half_cell = maskmapAttr['cell'] / 2
    x = x1 - half_cell  # |
    y = y1 + half_cell  # | coordinates of the upper left corner of the input file upper left pixel
    cut0 = int(round(np.abs(maskmapAttr['x'] - x) / maskmapAttr['cell']))
    cut1 = cut0 + maskmapAttr['col']
    cut2 = int(round(np.abs(maskmapAttr['y'] - y) / maskmapAttr['cell']))
    cut3 = cut2 + maskmapAttr['row']
    return cut0, cut1, cut2, cut3  # input data will be sliced using [cut0:cut1,cut2:cut3]


def loadsetclone(name):
    """ Load 'MaskMap' and set as clone
        
    :param name: name of the key in Settings.xml containing path and name of mask map as string
    :return: map: mask map (False=include in modelling; True=exclude from modelling) as pcraster
    """
    filename = binding[name]
    coord = filename.split()  # CM: returns a list of all the words in the string
    if len(coord) == 5:
        # CM: read information on clone map from Settings.xml
        # changed order of x, y i- in setclone y is first in Lisflood
        # settings x is first
        # CM: coord[0]=col
        # CM: coord[1]=row
        # CM: coord[2]=cellsize
        # CM: coord[3]=xupleft
        # CM: coord[4]=yupleft
        # setclone row col cellsize xupleft yupleft
        try:
            pcraster.setclone(int(coord[1]), int(coord[0]), float(coord[2]), float(coord[3]), float(coord[4]))  # CM: pcraster
        except:
            rem = "[" + str(coord[0]) + " " + str(coord[1]) + " " + str(coord[2]) + " " + str(coord[3]) + " " + str(coord[4]) + "]"
            msg = "Maskmap: " + rem + " are not valid coordinates (col row cellsize xupleft yupleft)"
            raise LisfloodError(msg)
        mapnp = np.ones((int(coord[1]), int(coord[0])))
        # mapnp[mapnp == 0] = 1
        map = numpy_operations.numpy2pcr(Boolean, mapnp, -9999)
    elif len(coord) == 1:
        # CM: read information on clone map from map (pcraster or netcdf)
        try:
            # try to read a pcraster map
            iterSetClonePCR(filename)
            map = operations.boolean(iterReadPCRasterMap(filename))
            flagmap = True
            # mapnp = numpy_operations.pcr2numpy(map, np.nan)
        except:
            # try to read a netcdf file
            filename = os.path.splitext(binding[name])[0] + '.nc'
            nf1 = iterOpenNetcdf(filename, "", "r")
            value = nf1.variables.items()[-1][0]  # get the last variable name
            # original code
            # x1 = nf1.variables.values()[0][0]
            # x2 = nf1.variables.values()[0][1]
            # xlast = nf1.variables.values()[0][-1]
            # y1 = nf1.variables.values()[1][0]
            # ylast = nf1.variables.values()[1][-1]
            # new safer code that doesn't rely on a specific variable order in netCDF file (R.COUGHLAN & D.DECREMER)
            if 'lon' in nf1.variables.keys():
                x1 = nf1.variables['lon'][0]
                x2 = nf1.variables['lon'][1]
                y1 = nf1.variables['lat'][0]
                # y2 = nf1.variables['lat'][1]
                xlast = nf1.variables['lon'][-1]
                ylast = nf1.variables['lat'][-1]
            else:
                x1 = nf1.variables['x'][0]
                x2 = nf1.variables['x'][1]
                y1 = nf1.variables['y'][0]
                # y2 = nf1.variables['y'][1]
                xlast = nf1.variables['x'][-1]
                ylast = nf1.variables['y'][-1]

            cellSize = round(np.abs(x2 - x1), 4)
            nrRows = int(0.5 + np.abs(ylast - y1) / cellSize + 1)
            nrCols = int(0.5 + np.abs(xlast - x1) / cellSize + 1)
            x = x1 - cellSize / 2
            y = y1 + cellSize / 2
            mapnp = np.array(nf1.variables[value][0:nrRows, 0:nrCols])
            nf1.close()
            # setclone  row col cellsize xupleft yupleft
            pcraster.setclone(nrRows, nrCols, cellSize, x, y)
            map = numpy_operations.numpy2pcr(Boolean, mapnp, 0)
            # map = boolean(map)
            flagmap = True
        if Flags['check']:
            checkmap(name, filename, map, flagmap, 0)
    else:
        msg = "Maskmap: {} is not a valid mask map nor valid coordinates".format(name)
        raise LisfloodError(msg)

    # Definition of cellsize, coordinates of the meteomaps and maskmap
    # need some love for error handling
    maskmapAttr['x'] = pcraster.clone().west()  # CM: mask map West bound
    maskmapAttr['y'] = pcraster.clone().north()  # CM: mask map North bound
    maskmapAttr['col'] = pcraster.clone().nrCols()  # CM: mask map number of columns
    maskmapAttr['row'] = pcraster.clone().nrRows()  # CM: mask map number of rows
    maskmapAttr['cell'] = pcraster.clone().cellSize()  # CM: mask map cell size

    return map


# def decompress(map):
#     # dmap=np.ma.masked_all(maskinfo['shapeflat'], dtype=map.dtype)
#     dmap = maskinfo['maskall'].copy()
#     dmap[~maskinfo['maskflat']] = map[:]
#     dmap = dmap.reshape(maskinfo['shape'])
#     # check if integer map (like outlets, lakes etc
#     try:
#         checkint = str(map.dtype)
#     except:
#         checkint = "x"
#     if checkint in ["int16", "int32", "int64"]:
#         dmap[dmap.mask] = -9999
#         map = numpy_operations.numpy2pcr(Nominal, dmap, -9999)
#     elif checkint == "int8":
#         dmap[dmap < 0] = -9999
#         map = numpy_operations.numpy2pcr(Nominal, dmap, -9999)
#     else:
#         dmap[dmap.mask] = -9999
#         map = numpy_operations.numpy2pcr(Scalar, dmap, -9999)
#     return map


# def makenumpy(map):
#     if not ('numpy.ndarray' in str(type(map))):
#         out = np.empty(maskinfo['mapC'])
#         out.fill(map)
#         return out
#     else:
#         return map


def loadmap(name):
    """
    :param name: Variable name as defined in XML settings or a filename of a netCDF or PCRaster map
    load a static map either value or pcraster map or netcdf
    """
    value = binding[name]
    filename = value

    map = None
    flagmap = False

    # Try first to load the value from settings
    try:
        map = float(value)
        flagmap = False
        load = True
    except ValueError:
        try:
            # try to read a pcraster map
            map = pcraster.readmap(value)
            flagmap = True
            load = True
        except:
            load = False

    if not load:
        # read a netcdf  (single one not a stack)
        filename = value.split('.')[0] + '.nc'

        # get mapextend of netcdf map
        # and calculate the cutting
        cut0, cut1, cut2, cut3 = mapattrNetCDF(filename)

        # load netcdf map but only the rectangle needed
        nf1 = Dataset(filename, 'r')
        value = nf1.variables.items()[-1][0]  # get the last variable name
        mapnp = nf1.variables[value][cut2:cut3, cut0:cut1]
        nf1.close()

        # check if integer map (like outlets, lakes etc)
        checkint = str(mapnp.dtype)
        if checkint == "int16" or checkint == "int32":
            mapnp[mapnp.mask] = -9999
            map = numpy_operations.numpy2pcr(Nominal, mapnp, -9999)
        elif checkint == "int8":
            map = numpy_operations.numpy2pcr(Nominal, mapnp, 0)
        else:
            mapnp[np.isnan(mapnp)] = -9999
            map = numpy_operations.numpy2pcr(Scalar, mapnp, -9999)

        # if the map is a ldd
        if value.split('.')[0][-3:] == 'ldd':
            # FIXME weak...filename must contain 'ldd' string
            map = operations.ldd(operations.nominal(map))
        flagmap = True

    if Flags['check']:
        checkmap(name, filename, map, flagmap, 0)
    return map


def take_closest(a_list, a_number):
    """ Returns the closest left value to myNumber in myList
    
    Assumes myList is sorted. Returns closest left value to myNumber.
    If myList is sorted in raising order, it returns the closest smallest value.
    https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
    
    :param a_list: list of ordered values
    :param a_number: number to be searche in a_list
    :return: closest left number to a_number in a_list
    """
    pos = bisect_left(a_list, a_number)
    if pos == 0:
        return a_list[0]
    if pos == len(a_list):
        return a_list[-1]
    before = a_list[pos - 1]
    return before


def readnetcdf(name, time, timestampflag='closest', averageyearflag=False, variable_name=None):
    """ Read maps from netCDF stacks (forcings, fractions, water demand)

    Read maps from netCDF stacks (forcings, fractions, water demand).
    Maps are read by date, so stacks can start at every date also different from CalendarDayStart.
    Units for stacks can be different from model timestep.
    It can read sub-daily steps.
    timestampflag indicates whether to load data with the exact time stamp ('exact'), or the data with the closest time
    stamp when the exact one is not available ('closest').
    averageyearflag indicates whether to load data from a netcdf file containing one single "average" year (it's used for
    water demand and landuse changes in time).

    :param name: string containing path and name of netCDF file to be read
    :param time: current simulation timestep of the model as integer number (referred to CalendarStartDay)
    :param timestampflag: look for exact time stamp in netcdf file ('exact') or for the closest (left) time stamp available ('closest')
    :param averageyearflag: if True, use "average year" netcdf file over the entire model simulation period
    :param variable_name: if given, will select the variable from netcdf instead of guessing
    :returns: content of netCDF map for timestep "time" (mapC)
    :except: if current simulation timestep is not stored in the stack, it stops with error message (if timestampflag='exact')
    """

    filename = name + ".nc" if not name.endswith('nc') else name
    nf1 = iterOpenNetcdf(filename, "Netcdf map stacks: \n", "r")

    # read information from netCDF file
    # original code 
    # Attempt at checking if input files are not in the format we expect
    if not variable_name:
        varNames = [nf1.variables.items()[it][0] for it in xrange(len(nf1.variables.items()))]
        # targets = list()
        skip_names = ('x', 'y', 'laea', 'lambert_azimuthal_equal_area', 'time', 'lat', 'lon')
        targets = [it for it in varNames if it not in skip_names]
        # Return warning if we have more than 1 non-coordinate-related variable
        # (i.e. x, y, laea, time) OR if the last variable in the netCDF file is not the variable to get data for
        if len(targets) > 1 or not str(nf1.variables.items()[-1]).find(targets[0]) > -1:
            warnings.warn("Wrong number of variables found in netCDF file %s" % filename)
        else:
            variable_name = targets[0]

    t_steps = nf1.variables['time'][:]  # get values for timesteps ([  0.,  24.,  48.,  72.,  96.])
    t_unit = nf1.variables['time'].units  # get unit (u'hours since 2015-01-01 06:00:00')
    try:
        t_cal = nf1.variables['time'].calendar  # get calendar from netCDF file
    except AttributeError:  # Attribute does not exist
        t_cal = u"gregorian"  # Use standard calendar

    begin = Calendar(binding['CalendarDayStart'])
    DtSec = float(binding['DtSec'])
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    # get date of current simulation step
    current_date = Calendar(time)

    if not isinstance(current_date, datetime.datetime):
        current_date = begin + datetime.timedelta(days=(current_date - 1) * DtDay)

    # if reading from an average year NetCDF stack, ignore the year in current simulation date and change it to the netCDF time unit year
    if averageyearflag:
        # CM: get year from time unit in case average year is used
        # CM: get date of the first step in netCDF file containing average year values
        first_date = num2date(t_steps[0], t_unit, t_cal)
        # CM: get year of the first step in netCDF file containing average year values
        t_ref_year = first_date.year
        try:
            current_date = current_date.replace(year=t_ref_year)
        except ValueError:
            # CM: if simulation year is leap and average year is not, switch 29/2 with 28/2
            current_date = current_date.replace(day=28)
            current_date = current_date.replace(year=t_ref_year)

    # get timestep in netCDF file corresponding to current simulation date
    current_ncdf_step = date2num(current_date, units=t_unit, calendar=t_cal)

    # read netCDF map
    if current_ncdf_step not in t_steps:
        if timestampflag == 'exact':
            # look for exact time stamp when loading data
            msg = "Date " + str(current_date) + " not stored in " + filename
            raise LisfloodError(msg)
        elif timestampflag == 'closest':
            # CM: get the closest value
            current_ncdf_step_new = take_closest(t_steps, current_ncdf_step)
            # CM: set current_ncdf_step to the closest available time step in netCDF file
            current_ncdf_step = current_ncdf_step_new

    # get index of timestep in netCDF file corresponding to current simulation date
    current_ncdf_index = np.where(t_steps == current_ncdf_step)[0][0]
    # mapnp = nf1.variables[variable_name][time - 1, cutmap[2]:cutmap[3], cutmap[0]:cutmap[1]]
    mapnp = nf1.variables[variable_name][current_ncdf_index, cutmap[2]:cutmap[3], cutmap[0]:cutmap[1]]

    nf1.close()
    # return mapnp
    mapnp[np.isnan(mapnp)] = -9999
    map = numpy_operations.numpy2pcr(Scalar, mapnp, -9999)
    timename = os.path.basename(name) + str(time)
    if Flags['check']:
        checkmap(timename, filename, map, True, 1)
    return map


def checknetcdf(name, start, end):
    """ Check available time steps in netCDF input file
    
    Check available timesteps in netCDF file. Get first and last available timestep in netCDF file and compare with
    first and last computation timestep of the model.
    It can use sub-daily steps.
    
    :param name: string containing path and name of netCDF file
    :param start: initial date or step number of model simulation
    :param end: final date or step of model simulation  
    :return: none
    :raises Exception: stop if netCDF maps do not cover simulation time period
    """

    filename = name + '.nc' if not name.endswith('.nc') else name
    nf1 = iterOpenNetcdf(filename, "Netcdf map stacks: \n", "r")

    # read information from netCDF file
    t_steps = nf1.variables['time'][:]  # get values for timesteps ([  0.,  24.,  48.,  72.,  96.])
    t_unit = nf1.variables['time'].units  # get unit (u'hours since 2015-01-01 06:00:00')
    try:
        t_cal = nf1.variables['time'].calendar  # get calendar from netCDF file
    except AttributeError:  # Attribute does not exist
        t_cal = u"gregorian"  # Use standard calendar

    # get date of first available timestep in netcdf file
    date_first_step_in_ncdf = num2date(t_steps[0], units=t_unit, calendar=t_cal)
    # get date of last available timestep in netcdf file
    date_last_step_in_ncdf = num2date(t_steps[-1], units=t_unit, calendar=t_cal)

    nf1.close()

    # CM: calendar date start (CalendarDayStart)
    begin = Calendar(binding['CalendarDayStart'])
    DtSec = float(binding['DtSec'])
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    date_first_sim_step = Calendar(start)
    if not isinstance(date_first_sim_step, datetime.datetime):
        date_first_sim_step = begin + datetime.timedelta(days=(date_first_sim_step - 1) * DtDay)
    if date_first_sim_step < date_first_step_in_ncdf:
        msg = """
        First simulation time step is before first time step in netCDF input data file 
        File name: {}
        netCDF start date: {}
        simulation start date: {}
        """.format(filename, date_first_step_in_ncdf.strftime('%d/%m/%Y %H:%M'), date_first_sim_step.strftime('%d/%m/%Y %H:%M'))
        raise LisfloodError(msg)

    date_last_sim_step = Calendar(end)
    if not isinstance(date_last_sim_step, datetime.datetime):
        date_last_sim_step = begin + datetime.timedelta(days=(date_last_sim_step - 1) * DtDay)
    if date_last_sim_step > date_last_step_in_ncdf:
        msg = """
        Last simulation time step is after last time step in netCDF input data file 
        File name: {}
        netCDF last date: {}
        simulation last date: {}
        """.format(filename, date_last_step_in_ncdf.strftime('%d/%m/%Y %H:%M'), date_last_sim_step.strftime('%d/%m/%Y %H:%M'))
        raise LisfloodError(msg)

    return

#
# def generateName(name, time):
#     """Returns a filename based on the name and time step passed in.
#     The resulting name obeys the 8.3 DOS style format. The time step
#     will be added to the end of the filename and be prepended by 0's if
#     needed.
#     The time step normally ranges from [1, nrTimeSteps].
#     The length of the name should be max 8 characters to leave room for
#     the time step.
#     The name passed in may contain a directory name.
#     See also: generateNameS(), generateNameST()
#     """
#     head, tail = os.path.split(name)
#     if re.search("\.", tail):
#         msg = "File extension given in '" + name + "' not allowed"
#         raise LisfloodError(msg)
#     if len(tail) == 0:
#         msg = "No filename specified"
#         raise LisfloodError(msg)
#     if len(tail) > 8:
#         msg = "Filename '" + name + "' must be shorter than 8 characters"
#         raise LisfloodError(msg)
#     if time < 0:
#         msg = "Timestep must be larger than 0"
#         raise LisfloodError(msg)
#
#     nr = "%d" % (time)
#     space = 11 - (len(tail) + len(nr))
#     assert space >= 0
#     result = "%s%s%s" % (tail, space * "0", nr)
#     result = "%s.%s" % (result[:8], result[8:])
#     assert len(result) == 12
#     return os.path.join(head, result)


def writenet(flag, inputmap, netfile, timestep, value_standard_name, value_long_name, value_unit, fillval, startdate, flagTime=True):
    """
    write a netcdf stack
    """
    prefix = netfile.split('/')[-1].split('\\')[-1].split('.')[0]
    netfile = netfile.split('.')[0] + '.nc'
    row = np.abs(cutmap[3] - cutmap[2])
    col = np.abs(cutmap[1] - cutmap[0])
    if flag == 0:
        # print 'filewrite',netfile
        nf1 = Dataset(netfile, 'w', format='NETCDF4_CLASSIC')

        # general Attributes
        nf1.history = 'Created ' + xtime.ctime(xtime.time())
        nf1.Conventions = 'CF-1.4'
        nf1.Source_Software = 'Python netCDF4'
        nf1.source = 'Lisvap output maps'

        # Dimension
        if 'y' in metadataNCDF.keys():
            nf1.createDimension('y', row)  # x 950
            latitude = nf1.createVariable('y', 'f8', ('y',))
            for i in metadataNCDF['y']:
                exec '%s="%s"' % ("latitude." + i, metadataNCDF['y'][i])

        if 'lat' in metadataNCDF.keys():
            nf1.createDimension('lat', row)  # x 950
            latitude = nf1.createVariable('lat', 'f8', ('lat',))
            for i in metadataNCDF['lat']:
                exec '%s="%s"' % ("latitude." + i, metadataNCDF['lat'][i])
        if 'x' in metadataNCDF.keys():
            nf1.createDimension('x', col)  # x 1000
            longitude = nf1.createVariable('x', 'f8', ('x',))
            for i in metadataNCDF['x']:
                exec '%s="%s"' % ("longitude." + i, metadataNCDF['x'][i])

        if 'lon' in metadataNCDF.keys():
            nf1.createDimension('lon', col)
            longitude = nf1.createVariable('lon', 'f8', ('lon',))
            for i in metadataNCDF['lon']:
                exec '%s="%s"' % ("longitude." + i, metadataNCDF['lon'][i])

        if flagTime:
            nf1.createDimension('time', None)
            time = nf1.createVariable('time', 'f8', ('time',))
            time.standard_name = 'time'
            time.units = 'days since %s' % startdate.strftime("%Y-%m-%d %H:%M:%S.0")
            time.calendar = 'gregorian'
            value = nf1.createVariable(prefix, fillval, ('time', 'y', 'x'), zlib=True)
        else:
            value = nf1.createVariable(prefix, fillval, ('y', 'x'), zlib=True)

        value.standard_name = value_standard_name
        value.long_name = value_long_name
        value.units = value_unit
        # value.esri_pe_string='PROJCS["ETRS_1989_LAEA",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["false_easting",4321000.0],PARAMETER["false_northing",3210000.0],PARAMETER["central_meridian",10.0],PARAMETER["latitude_of_origin",52.0],UNIT["Meter",1.0]]'
        # projection
        if 'laea' in metadataNCDF.keys():
            proj = nf1.createVariable('laea', 'i4')
            proj.grid_mapping_name = 'lambert_azimuthal_equal_area'
            # FIXME magic numbers
            proj.false_easting = 4321000.0
            proj.false_northing = 3210000.0
            proj.longitude_of_projection_origin = 10.0
            proj.latitude_of_projection_origin = 52.0
            proj.semi_major_axis = 6378137.0
            proj.inverse_flattening = 298.257223563
            proj.proj4_params = "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs"
            proj.EPSG_code = "EPSG:3035"

        if 'lambert_azimuthal_equal_area' in metadataNCDF.keys():
            proj = nf1.createVariable('laea', 'i4')
            for i in metadataNCDF['lambert_azimuthal_equal_area']:
                exec '%s="%s"' % ("proj." + i, metadataNCDF['lambert_azimuthal_equal_area'][i])

        """
        EUROPE
        proj.grid_mapping_name='lambert_azimuthal_equal_area'
        proj.false_easting=4321000.0
        proj.false_northing=3210000.0
        proj.longitude_of_projection_origin = 10.0
        proj.latitude_of_projection_origin = 52.0
        proj.semi_major_axis = 6378137.0
        proj.inverse_flattening = 298.257223563
        proj.proj4_params = "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs"
        proj.EPSG_code = "EPSG:3035"
        """

        # Fill variables

        cell = pcraster.clone().cellSize()
        xl = pcraster.clone().west() + cell / 2
        xr = xl + col * cell
        yu = pcraster.clone().north() - cell / 2
        yd = yu - row * cell
        lats = np.arange(yu, yd, -cell)
        lons = np.arange(xl, xr, cell)

        latitude[:] = lats
        longitude[:] = lons

        if 'pr' in metadataNCDF.keys():
            if "esri_pe_string" in metadataNCDF['pr'].keys():
                value.esri_pe_string = metadataNCDF['pr']['esri_pe_string']

    else:
        nf1 = Dataset(netfile, 'a')

    mapnp = numpy_operations.pcr2numpy(inputmap, np.nan)
    if flagTime:
        nf1.variables['time'][flag] = timestep - 1

    if flagTime:
        nf1.variables[prefix][flag, :, :] = mapnp
    else:
        # without timeflag
        nf1.variables[prefix][:, :] = mapnp
    nf1.close()


# def dumpObject(name, var, num):
#     path1 = os.path.join(str(num), 'stateVar', name)
#     file_object1 = open(path1, 'w')
#     pickle.dump(var, file_object1)
#     file_object1.close()
#
#
# def loadObject(name, num):
#     path1 = os.path.join(str(num), 'stateVar', name)
#     filehandler1 = open(path1, 'r')
#     # CM: read a string from the open file object file and interpret it as a pickle data stream, rec
#     var = pickle.load(filehandler1)
#     filehandler1.close()
#     return var
#
# #
# # def dumpPCRaster(name, var, num):
# #     path1 = os.path.join(str(num), 'stateVar', name)
# #     report(var, path1)
#
#
# def loadPCRaster(name, num):
#     path1 = os.path.join(str(num), 'stateVar', name)
#     var = iterReadPCRasterMap(path1)
#     return var
#
#
# def perturbState(var, method="normal", minVal=0, maxVal=1, mu=0, sigma=1, spatial=True, single=True):
#     if method not in ('normal', 'uniform'):
#         raise ValueError('Method {} not allowed'.format(method))
#     try:
#         numVals = len(var)
#     except:
#         numVals = 1
#
#     if method == "normal":
#         if spatial:
#             domain = len(var[0])
#             out = var
#             for i in range(numVals):
#                 out[i] = np.minimum(np.maximum(np.random.normal(mu, sigma, domain), minVal), maxVal)
#         else:
#             if single:
#                 out = np.minimum(np.maximum(np.random.normal(mu, sigma, numVals), minVal), maxVal)
#             else:
#                 out = list(np.minimum(np.maximum(np.random.normal(mu, sigma, numVals), minVal), maxVal))
#         return out
#     elif method == "uniform":
#         if spatial:
#             domain = len(var[0])
#             out = var
#             for i in range(numVals):
#                 out[i] = np.random.uniform(minVal, maxVal, domain)
#         else:
#             if single:
#                 out = np.random.uniform(minVal, maxVal, numVals)
#             else:
#                 out = list(np.random.uniform(minVal, maxVal, numVals))
#         return out
