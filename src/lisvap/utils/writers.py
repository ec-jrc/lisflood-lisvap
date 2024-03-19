
"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from nine import IS_PYTHON2

import os
import time as xtime
import datetime

import numpy as np
from netCDF4 import Dataset
import pcraster
from pcraster import numpy_operations
from decimal import *

from . import CutMap, NetcdfMetadata, LisSettings
from pyproj import proj
from ..__init__ import __version__ as lisvap_version
# from scprep.run.splatter import SplatSimulate
# from audioop import reverse

if IS_PYTHON2:
    from pathlib2 import Path
else:
    from pathlib import Path


__DECIMAL_CASES = 20
__DECIMAL_FORMAT = '{:.20f}'
getcontext().prec = __DECIMAL_CASES


def coordinates_range_from_array(coords):
    nelems = len(coords)
    elem_array = [Decimal(0.0)] * nelems
    for i in range(nelems):
        elem_array[i] = Decimal(coords[i])
    return elem_array


def coordinates_range(start=0, nelems=1, step=1):
    elem_array = [Decimal(0.0)] * nelems
    array_step = Decimal(step)
    elem = Decimal(start)
    for i in range(nelems):
        elem_array[i] = elem
        elem = elem + array_step
    return elem_array


def get_output_parameters_monthly(start_date, timestep, time_frequency, timestep_stride, current_output_index):
    output_index = current_output_index
    current_date = start_date + datetime.timedelta(seconds=((timestep - 1) * timestep_stride))
    filename_suffix = current_date.strftime('%Y%m')

    first_date_current_month = start_date.replace(year=current_date.year, month=current_date.month)
    seconds_between = (current_date - first_date_current_month).total_seconds()
    num_steps_done_in_current_month = int(seconds_between / timestep_stride) + 1
    last_date_last_month = first_date_current_month - datetime.timedelta(seconds=timestep_stride)
    day_inside_last_month = last_date_last_month - datetime.timedelta(seconds=timestep_stride)

    if current_date == first_date_current_month:
        output_index = 0
    elif current_date == last_date_last_month:
        filename_suffix = day_inside_last_month.strftime('%Y%m')
        first_date_last_month = day_inside_last_month.replace(day=1) + datetime.timedelta(seconds=(2 * timestep_stride))
        num_steps_done_in_last_month = int((last_date_last_month - first_date_last_month).total_seconds() / timestep_stride) + 1
        output_index = num_steps_done_in_last_month
    elif current_output_index >= num_steps_done_in_current_month:
        output_index = num_steps_done_in_current_month - 1
    return filename_suffix, output_index


def get_output_parameters_yearly(start_date, timestep, time_frequency, timestep_stride, current_output_index):
    output_index = current_output_index
    current_date = start_date + datetime.timedelta(seconds=((timestep - 1) * timestep_stride))
    filename_suffix = current_date.strftime('%Y')

    first_date_current_year = start_date.replace(year=current_date.year)
    seconds_between = (current_date - first_date_current_year).total_seconds()
    num_steps_done_in_current_year = int(seconds_between / timestep_stride) + 1
    last_date_last_year = first_date_current_year - datetime.timedelta(seconds=timestep_stride)
    day_inside_last_year = last_date_last_year - datetime.timedelta(seconds=timestep_stride)

    if current_date == first_date_current_year:
        output_index = 0
    elif current_date == last_date_last_year:
        filename_suffix = day_inside_last_year.strftime('%Y')
        first_date_last_year = first_date_current_year.replace(year=current_date.year - 1)
        num_steps_done_in_last_year = int((last_date_last_year - first_date_last_year).total_seconds() / timestep_stride) + 1
        output_index = num_steps_done_in_last_year - 1
    elif current_output_index >= num_steps_done_in_current_year:
        output_index = num_steps_done_in_current_year - 1
    return filename_suffix, output_index


def get_output_parameters(settings, netcdf_output_file, start_date, timestep, time_frequency, timestep_stride, current_output_index):
    output_index = current_output_index
    p = Path(netcdf_output_file)
    netfile = Path(p.parent) / Path('{}.nc'.format(p.name) if not p.name.endswith('.nc') else p.name)
    prefix = os.path.splitext(netfile.name)[0]
    splitIO = settings.get_option('splitOutput')
    if splitIO:
        monthlyIO = settings.get_option('monthlyOutput')
        if monthlyIO:
            filename_suffix, output_index = get_output_parameters_monthly(start_date, timestep, time_frequency, timestep_stride, current_output_index)
        else:
            filename_suffix, output_index = get_output_parameters_yearly(start_date, timestep, time_frequency, timestep_stride, current_output_index)
        netfile = Path(p.parent) / Path('{}_{}.nc'.format(p.name, filename_suffix) if not p.name.endswith('.nc') else p.name)
    return prefix, netfile, output_index


def set_time_dimension(settings, netcdf_obj, time_variable_name, start_date, variable_dims, output6hourly=False):
    netcdf_obj.createDimension(time_variable_name, None)
    dims = list(variable_dims)
    dims.append(time_variable_name)
    dims.reverse()
    variable_dims = tuple(dims)
    time = netcdf_obj.createVariable(time_variable_name, 'f4', (time_variable_name, ))
    time.standard_name = time_variable_name
    if output6hourly:
        # start date=day2_06:00 ; start_date_6hourly=day1_12:00
        start_date_6hourly = start_date - datetime.timedelta(hours=18)
        time.units = 'hours since %s' % start_date_6hourly.strftime('%Y-%m-%d %H:%M:%S.0')
        time.frequency = 6
    elif 'internal.time.unit' in settings.binding:
        internal_time_units = settings.binding['internal.time.unit']
        # Separate the different parts of time units, ex:
        # "seconds since 1970-01-01 00:00:00"
        # "days since 1970-01-01 00:00:00"
        # "hours since 1970-01-01 00:00:00"
        # "minutes since 1970-01-01 00:00:00"
        time_units_parts = internal_time_units.split(' ')
        time.units = '%s since %s' % (time_units_parts[0], start_date.strftime('%Y-%m-%d %H:%M:%S.0'))
        time.frequency = int(settings.binding['internal.time.frequency'])
    else:
        time.units = 'days since %s' % start_date.strftime('%Y-%m-%d %H:%M:%S.0')
        time.frequency = 1
    if 'internal.time.calendar' in settings.binding:
        time.calendar = settings.binding['internal.time.calendar']
    else:
        time.calendar = 'proleptic_gregorian'
    return variable_dims


def set_dimensions(settings, netcdf_obj, metadata_ncdf, ncols, nrows, time_variable_name,
                   start_date, output6hourly=False, flag_time=True):
    # Dimension
    spatial_dims = tuple([c for c in ('x', 'lon', 'y', 'lat') if c in metadata_ncdf])
    for dim_name, dim_size in zip(spatial_dims, [ncols, nrows]):
        netcdf_obj.createDimension(dim_name, dim_size)

    variable_dims = spatial_dims
    if flag_time:
        variable_dims = set_time_dimension(settings, netcdf_obj, time_variable_name, start_date,
                                           variable_dims, output6hourly)

    reverse_spatial_dims = list(spatial_dims)
    reverse_spatial_dims.reverse()
    for dim_name in reverse_spatial_dims:
        coord = netcdf_obj.createVariable(dim_name, 'f8', (dim_name, ))
        for i in metadata_ncdf[dim_name]:
            # to avoid AttributeError ("_FillValue attribute must be set when variable is created") when writing output nc attributes
            if i != '_FillValue':
                setattr(coord, i, metadata_ncdf[dim_name][i])
    return spatial_dims, variable_dims


def set_projection(netcdf_obj, metadata_ncdf):
    # projection
    proj = None
    metadata_ncdf_projections = {
        'laea': 'laea',
        'lambert_azimuthal_equal_area': 'laea',
        'wgs_1984': 'wgs_1984',
        'crs': 'crs'
    }
    selected_proj_key = ''
    for proj_key in metadata_ncdf_projections:
        if proj_key in metadata_ncdf:
            selected_proj_key = proj_key
            variable_name = metadata_ncdf_projections[proj_key]
            proj = netcdf_obj.createVariable(variable_name, 'i4')
            # Copy all other attributes
            for i in metadata_ncdf[proj_key]:
                setattr(proj, i, metadata_ncdf[proj_key][i])
    return proj, selected_proj_key


def get_coordinate_arrays(settings, ncols, nrows):
    # Fill variables
    try:
        int_lons = settings.binding['internal.lons']
        int_lats = settings.binding['internal.lats']
        # x1 = Decimal(__DECIMAL_FORMAT.format(int_lons[0]))
        # x2 = Decimal(__DECIMAL_FORMAT.format(int_lons[1]))
        # y1 = Decimal(__DECIMAL_FORMAT.format(int_lats[0]))
        # y2 = Decimal(__DECIMAL_FORMAT.format(int_lats[1]))
        # cellSizeX = abs(x2 - x1)
        # cellSizeY = abs(y2 - y1)
        lats = coordinates_range_from_array(int_lats)
        lons = coordinates_range_from_array(int_lons)
    except:
        cellSize = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().cellSize()))
        half_cell = cellSize * Decimal(0.5)
        xl = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().west())) + half_cell
        # xr = xl + ncols * cellSize - half_cell
        yu = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().north())) - half_cell
        # yd = yu - nrows * cellSize + half_cell
        lats = coordinates_range(yu, nrows, -cellSize)
        lons = coordinates_range(xl, ncols, cellSize)
    return lats, lons


def create_new_netcdf(settings, prefix, netfile, ncols, nrows, time_variable, start_date,
                      value_standard_name, value_long_name, value_unit, data_type,
                      scale_factor=0.1, add_offset=0.0, value_min=0, value_max=-9999,
                      output6hourly=False, flag_time=True, nan_value=-9999):
    nf1 = Dataset(netfile, 'w', format='NETCDF4_CLASSIC')
    # general Attributes
    nf1.history = 'Created ' + xtime.ctime(xtime.time())
    nf1.Conventions = 'CF-1.6'
    nf1.Source_Software = 'Lisvap v' + lisvap_version
    nf1.source = 'Lisvap output maps'

    metadata_ncdf = NetcdfMetadata.instance()

    spatial_dims, variable_dims = set_dimensions(settings, nf1, metadata_ncdf, ncols, nrows, time_variable,
                                                 start_date, output6hourly, flag_time)

    proj, selected_proj_key = set_projection(nf1, metadata_ncdf)

    value = nf1.createVariable(prefix, data_type, variable_dims, zlib=True, complevel=4, fill_value=nan_value)

    value.standard_name = value_standard_name
    value.long_name = value_long_name
    value.units = value_unit
    value.valid_min = int(value_min / scale_factor)
    if value_max != nan_value:
        value.valid_max = int(value_max / scale_factor)
    value.scale_factor = scale_factor
    value.add_offset = add_offset
    value.missing_value = nan_value
    value.set_auto_maskandscale(True)

    if proj is not None:
        if 'grid_mapping_name' in metadata_ncdf[selected_proj_key]:
            value.grid_mapping = proj.grid_mapping_name
        if 'spatial_ref' in metadata_ncdf[selected_proj_key]:
            value.esri_pe_string = proj.spatial_ref

    lats, lons = get_coordinate_arrays(settings, ncols, nrows)

    nf1.variables[spatial_dims[1]][:] = lats
    nf1.variables[spatial_dims[0]][:] = lons

    if 'pr' in metadata_ncdf and 'esri_pe_string' in metadata_ncdf['pr']:
        value.esri_pe_string = metadata_ncdf['pr']['esri_pe_string']
    return nf1


def writenet(current_output_index, inputmap, netcdf_output_file, current_timestep, value_standard_name, value_long_name,
             value_unit, data_type, calendar_day_start, flag_time=True, nan_value=-9999, scale_factor=0.1,
             add_offset=0.0, value_min=0, value_max=-9999):
    """
    write a netcdf stack
    output_index: integer. Global index of the map to store in the final file
    inputmap: a PCRaster 2D array
    netfile: output netcdf filename
    timestep:
    """
    settings = LisSettings.instance()

    timestep_stride = int(settings.binding['DtSec'])
    time_frequency = int(settings.binding['internal.time.frequency'])
    start_date = calendar_day_start + datetime.timedelta(seconds=timestep_stride)
    timestep = current_timestep

    cutmap = CutMap.instance()
    nrows = np.abs(cutmap.cuts[3] - cutmap.cuts[2])
    ncols = np.abs(cutmap.cuts[1] - cutmap.cuts[0])

    time_variable = 'time'
    output6hourly = settings.get_option('output6hourly')
    prefix, netfile, output_index = get_output_parameters(settings, netcdf_output_file, start_date, timestep,
                                                          time_frequency, timestep_stride, current_output_index)

    # Create and setup the netcdf file when the first map needs to be stored
    if output_index == 0 or not netfile.exists():
        nf1 = create_new_netcdf(settings, prefix, netfile, ncols, nrows, time_variable, start_date,
                                value_standard_name, value_long_name, value_unit, data_type,
                                scale_factor, add_offset, value_min, value_max,
                                output6hourly, flag_time, nan_value)
    else:
        nf1 = Dataset(netfile, 'a')

    mapnp = numpy_operations.pcr2numpy(inputmap, np.nan)
    # Pack NAN values into short
    mapnp[np.isnan(mapnp)] = (nan_value - add_offset) * scale_factor
    if flag_time:
        # In case output6hourly==True, replicate four daily maps to get the 6 hourly output (EFCC-2316)
        # The timestep needs to increase by 4
        if output6hourly:
            time_frequency = 6
            for i in range(4):
                map_idx = output_index * 4 + i
                nf1.variables[time_variable][map_idx] = (timestep * 4 - 4 + i) * time_frequency
                nf1.variables[prefix][map_idx, :, :] = mapnp
        else:  # Generate daily output
            nf1.variables[time_variable][output_index] = (timestep - 1) * time_frequency  # timestep - time_frequency
            nf1.variables[prefix][output_index, :, :] = mapnp
    else:
        nf1.variables[prefix][:, :] = mapnp
    nf1.close()
