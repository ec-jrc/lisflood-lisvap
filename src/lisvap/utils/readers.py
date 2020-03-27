from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.utils import listitems
from nine import str

import datetime
import os
import time
import warnings

import numpy as np
import pcraster
from netCDF4 import Dataset, num2date, date2num
from pcraster import numpy_operations, Boolean, Nominal, Scalar

try:
    from pcraster.multicore import _operations as operations
except ImportError:
    from pcraster import operations

from . import LisSettings, LisfloodError, MaskMapMetadata, CutMap
from .tools import take_closest, calendar, checkmap


def loadsetclone(name):
    """ Load 'MaskMap' and set as clone

    :param name: name of the key in Settings.xml containing path and name of mask map as string
    :return: map: mask map (False=include in modelling; True=exclude from modelling) as pcraster
    """
    settings = LisSettings.instance()
    filename = settings.binding[name]
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
            msg = 'Maskmap: [{} {} {} {}] are not valid coordinates (col row cellsize xupleft yupleft)'.format(*coord)
            raise LisfloodError(msg)
        mapnp = np.ones((int(coord[1]), int(coord[0])))
        res = numpy_operations.numpy2pcr(Boolean, mapnp, -9999)
    elif len(coord) == 1:
        # CM: read information on clone map from map (pcraster or netcdf)
        try:
            # try to read a pcraster map
            iter_setclone_pcraster(filename)
            res = operations.boolean(iter_read_pcraster(filename))
            flagmap = True
        except:
            # try to read a netcdf file
            filename = '{}.{}'.format(os.path.splitext(settings.binding[name])[0], 'nc')
            nf1 = iter_open_netcdf(filename, 'r')
            value = listitems(nf1.variables)[-1][0]  # get the last variable name

            if 'lon' in nf1.variables.keys():
                x1 = nf1.variables['lon'][0]
                x2 = nf1.variables['lon'][1]
                y1 = nf1.variables['lat'][0]
                xlast = nf1.variables['lon'][-1]
                ylast = nf1.variables['lat'][-1]
            else:
                x1 = nf1.variables['x'][0]
                x2 = nf1.variables['x'][1]
                y1 = nf1.variables['y'][0]
                xlast = nf1.variables['x'][-1]
                ylast = nf1.variables['y'][-1]

            cellSize = round(np.abs(x2 - x1), 5)
            nrRows = int(0.5 + np.abs(ylast - y1) / cellSize + 1)
            nrCols = int(0.5 + np.abs(xlast - x1) / cellSize + 1)
            x = x1 - cellSize / 2  # Coordinate of west side of raster
            y = y1 + cellSize / 2  # Coordinate of north side of raster
            mapnp = np.array(nf1.variables[value][0:nrRows, 0:nrCols])
            nf1.close()
            # setclone  row col cellsize xupleft yupleft
            pcraster.setclone(nrRows, nrCols, cellSize, x, y)
            res = numpy_operations.numpy2pcr(Boolean, mapnp, 0)
            flagmap = True
        if settings.flags['checkfiles']:
            checkmap(name, filename, res, flagmap, 0)
    else:
        msg = 'Maskmap: {} is not a valid mask map nor valid coordinates'.format(name)
        raise LisfloodError(msg)

    # Definition of cellsize, coordinates of the meteomaps and maskmap
    # Get the current PCRaster clone map and it save metadata
    MaskMapMetadata.register(filename)
    return res


def loadmap(name):
    """
    :param name: Variable name as defined in XML settings or a filename of a netCDF or PCRaster map
    load a static map either value or pcraster map or netcdf
    """
    settings = LisSettings.instance()
    value = settings.binding[name]
    filename = value

    res = None
    flagmap = False

    # Try first to load the value from settings
    try:
        res = float(value)
        flagmap = False
        load = True
    except ValueError:
        try:
            # try to read a pcraster map
            res = pcraster.readmap(value)
            flagmap = True
            load = True
        except:
            load = False

    if not load:
        # read a netcdf (single one not a stack)
        filename = '{}.{}'.format(os.path.splitext(value)[0], 'nc')

        # get mapextend of netcdf map
        # and calculate the cutting
        cut0, cut1, cut2, cut3 = CutMap.get_cuts(filename)

        # load netcdf map but only the rectangle needed
        nf1 = Dataset(filename, 'r')
        value = listitems(nf1.variables)[-1][0]  # get the last variable name
        mapnp = nf1.variables[value][cut2:cut3, cut0:cut1]
        nf1.close()

        # check if integer map (like outlets, lakes etc)
        checkint = str(mapnp.dtype)
        if checkint == "int16" or checkint == "int32":
            mapnp[mapnp.mask] = -9999
            res = numpy_operations.numpy2pcr(Nominal, mapnp, -9999)
        elif checkint == "int8":
            res = numpy_operations.numpy2pcr(Nominal, mapnp, 0)
        else:
            mapnp[np.isnan(mapnp)] = -9999
            res = numpy_operations.numpy2pcr(Scalar, mapnp, -9999)

        # if the map is a ldd
        if value.split('.')[0][-3:] == 'ldd':
            # FIXME weak...filename must contain 'ldd' string
            res = operations.ldd(operations.nominal(res))
        flagmap = True

    if settings.flags['checkfiles']:
        checkmap(name, filename, res, flagmap, 0)
    return res


def readnetcdf(name, timestep, timestampflag='closest', averageyearflag=False, variable_name=None):
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
    :param timestep: current simulation timestep of the model as integer number (referred to CalendarStartDay)
    :param timestampflag: look for exact time stamp in netcdf file ('exact') or for the closest (left) time stamp available ('closest')
    :param averageyearflag: if True, use "average year" netcdf file over the entire model simulation period
    :param variable_name: if given, will select the variable from netcdf instead of guessing
    :returns: content of netCDF map for timestep "time" (mapC)
    :except: if current simulation timestep is not stored in the stack, it stops with error message (if timestampflag='exact')
    """

    filename = '{}.nc'.format(name) if not name.endswith('nc') else name
    nf1 = iter_open_netcdf(filename, 'r')
    # read information from netCDF file
    # original code
    # Attempt at checking if input files are not in the format we expect
    if not variable_name:
        # variables = listitems(nf1.variables)
        # get the variable with 3 dimensions (variable order not relevant)
        targets = [k for k in nf1.variables if len(nf1.variables[k].dimensions) == 3]
        if len(targets) > 1:
            warnings.warn('Wrong number of variables found in netCDF file {}}'.format(filename))
        elif not targets:
            raise LisfloodError('No 3 dimensions variable was found in mapstack {}'.format(filename))
        variable_name = targets[0]
    
    current_ncdf_index = netcdf_step(averageyearflag, nf1, timestampflag, timestep)

    cutmaps = CutMap.instance().slices
    mapnp = nf1.variables[variable_name][current_ncdf_index, cutmaps[0], cutmaps[1]]
    nf1.close()
    if variable_name=='rn':
        mapnp[np.isnan(mapnp)] = -9999999
        mapnp = numpy_operations.numpy2pcr(Scalar, mapnp, -9999999)
    else:
        mapnp[np.isnan(mapnp)] = -9999
        mapnp = numpy_operations.numpy2pcr(Scalar, mapnp, -9999)
    timename = os.path.basename(name) + str(timestep)
    settings = LisSettings.instance()
    if settings.flags['checkfiles']:
        checkmap(timename, filename, mapnp, True, 1)
    return mapnp


def netcdf_step(averageyearflag, nf1, timestampflag, timestep):
    """
    Get netcdf step index based on timestep
    :param averageyearflag:
    :param nf1: netcdf file handler
    :type nf1: netcdf.Dataset
    :param timestampflag:
    :param timestep: current timestep
    :type timestep: int
    :return: current_ncdf_index
    :rtype: int
    """
    t_steps = nf1.variables['time'][:]  # get values for timesteps ([  0.,  24.,  48.,  72.,  96.])
    t_unit = nf1.variables['time'].units  # get unit (u'hours since 2015-01-01 06:00:00')
    try:
        t_cal = nf1.variables['time'].calendar  # get calendar from netCDF file
    except AttributeError:  # Attribute does not exist
        t_cal = u'gregorian'  # Use standard calendar
    settings = LisSettings.instance()
    begin = calendar(settings.binding['CalendarDayStart'])
    DtSec = float(settings.binding['DtSec'])
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)
    # get date of current simulation step
    current_date = calendar(timestep)
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
            msg = "Date " + str(current_date) + " not stored in input map"
            raise LisfloodError(msg)
        elif timestampflag == 'closest':
            # CM: get the closest value
            current_ncdf_step_new = take_closest(t_steps, current_ncdf_step)
            # CM: set current_ncdf_step to the closest available time step in netCDF file
            current_ncdf_step = current_ncdf_step_new
    # get index of timestep in netCDF file corresponding to current simulation date
    current_ncdf_index = np.where(t_steps == current_ncdf_step)[0][0]
    return current_ncdf_index


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

    filename = '{}.nc'.format(name) if not name.endswith('nc') else name
    nf1 = iter_open_netcdf(filename, 'r')

    # read information from netCDF file
    t_steps = nf1.variables['time'][:]  # get values for timesteps ([  0.,  24.,  48.,  72.,  96.])
    t_unit = nf1.variables['time'].units  # get unit (u'hours since 2015-01-01 06:00:00')
    try:
        t_cal = nf1.variables['time'].calendar  # get calendar from netCDF file
    except AttributeError:  # Attribute does not exist
        t_cal = u'gregorian'  # Use standard calendar

    # get date of first available timestep in netcdf file
    date_first_step_in_ncdf = num2date(t_steps[0], units=t_unit, calendar=t_cal)
    # get date of last available timestep in netcdf file
    date_last_step_in_ncdf = num2date(t_steps[-1], units=t_unit, calendar=t_cal)

    nf1.close()
    settings = LisSettings.instance()
    # CM: calendar date start (CalendarDayStart)
    begin = calendar(settings.binding['CalendarDayStart'])
    DtSec = float(settings.binding['DtSec'])
    DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    date_first_sim_step = calendar(start)
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

    date_last_sim_step = calendar(end)
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


def iter_open_netcdf(file_path, mode, **kwargs):
    """Wrapper around netCDF4.Dataset function exploiting the iterAccess class to access file_path according to the specified mode"""
    def access_function(path):
        return Dataset(path, mode, **kwargs)
    return remote_input_access(access_function, file_path)


def iter_read_pcraster(file_path):
    """Wrapper around pcraster.readmap function exploiting the iterAccess class to open file_path."""
    return remote_input_access(pcraster.readmap, file_path)


def iter_setclone_pcraster(file_path):
    """Wrapper around pcraster.setclone function exploiting the iterAccess class to access file_path."""
    return remote_input_access(pcraster.pcraster.setclone, file_path)


def remote_input_access(function, file_path):
    """
    Wrapper around the provided file access function.
    It allows re-trying the open/read operation if network is temporarily down.
    Arguments:
        function: function to be called to read/open the file.
        file_path: path of the file to be read/open.
    """
    num_trials = 1
    bad_sep = "\\"
    file_path = file_path.replace(bad_sep, os.path.sep)
    root = os.path.sep.join(file_path.split(os.path.sep)[:4])
    while num_trials <= 10:
        try:
            obj = function(file_path)
        except IOError:
            if os.path.exists(root) and not os.path.exists(file_path):
                raise LisfloodError(file_path)
            elif num_trials >= 10:
                raise Exception("Cannot access file {0}!\nNetwork down for too long OR bad root directory {1}!".format(file_path, root))
            else:
                num_trials += 1
                print("Trying to access file {0}: attempt n. {1}".format(file_path, num_trials))
                time.sleep(5)
        else:
            return obj
