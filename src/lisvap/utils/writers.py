
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

import numpy as np
from netCDF4 import Dataset
import pcraster
from pcraster import numpy_operations
from decimal import *

from . import CutMap, NetcdfMetadata, LisSettings
# from scprep.run.splatter import SplatSimulate
# from audioop import reverse

if IS_PYTHON2:
    from pathlib2 import Path
else:
    from pathlib import Path

# from pprint import pprint
# from memory_profiler import profile

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


# @profile
def writenet(flag, inputmap, netfile, timestep, value_standard_name, value_long_name, value_unit, fillval, startdate, flag_time=True,
             nan_value=-9999, scale_factor=0.1, add_offset=0.0, value_min=0, value_max=-9999):
    """
    write a netcdf stack
    flag: integer. If 0 it means write a NEW file (!) FIXME omg
    inputmap: a PCRaster 2D array
    netfile: output netcdf filename
    timestep:
    """
    p = Path(netfile)
    netfile = Path(p.parent) / Path('{}.nc'.format(p.name) if not p.name.endswith('.nc') else p.name)
    prefix = os.path.splitext(netfile.name)[0]

    cutmap = CutMap.instance()
    nrows = np.abs(cutmap.cuts[3] - cutmap.cuts[2])
    ncols = np.abs(cutmap.cuts[1] - cutmap.cuts[0])

    settings = LisSettings.instance()

    time_variable = 'time'
    output6hourly = settings.options['output6hourly']

    # Used to pack variables into short
    if flag == 0:
        nf1 = Dataset(netfile, 'w', format='NETCDF4_CLASSIC')

        # general Attributes
        nf1.history = 'Created ' + xtime.ctime(xtime.time())
        nf1.Conventions = 'CF-1.6'
        nf1.Source_Software = 'Lisvap'
        nf1.source = 'Lisvap output maps'

        metadata_ncdf = NetcdfMetadata.instance()

        # Dimension
        spatial_dims = tuple([c for c in ('x', 'lon', 'y', 'lat') if c in metadata_ncdf])
        for dim_name, dim_size in zip(spatial_dims, [ncols, nrows]):
            nf1.createDimension(dim_name, dim_size)

        variable_dims = spatial_dims
        if flag_time:
            nf1.createDimension(time_variable, None)
            dims = list(variable_dims)
            dims.append(time_variable)
            dims.reverse()
            variable_dims = tuple(dims)
            time = nf1.createVariable(time_variable, 'f4', (time_variable, ))
            time.standard_name = time_variable
            if output6hourly:
                time.units = 'hours since %s' % startdate.strftime('%Y-%m-%d %H:%M:%S.0')
                time.frequency = 6
            else:
                time.units = 'days since %s' % startdate.strftime('%Y-%m-%d %H:%M:%S.0')
                time.frequency = 1
            time.calendar = 'proleptic_gregorian'

        reverse_spatial_dims = list(spatial_dims)
        reverse_spatial_dims.reverse()
        for dim_name in reverse_spatial_dims:
            coord = nf1.createVariable(dim_name, 'f8', (dim_name, ))
            for i in metadata_ncdf[dim_name]:
                if i != '_FillValue':
                    # to avoid AttributeError ("_FillValue attribute must be set when variable is created") when writing output nc attributes
                    setattr(coord, i, metadata_ncdf[dim_name][i])

        # projection
        proj = None
        metadata_ncdf_projections = {
            'laea' : 'laea',
            'lambert_azimuthal_equal_area' : 'laea',
             'wgs_1984' : 'wgs_1984',
             'crs' : 'crs'
        }
        selected_proj_key = ''
        for proj_key in metadata_ncdf_projections:
            if proj_key in metadata_ncdf:
                selected_proj_key = proj_key
                variable_name = metadata_ncdf_projections[proj_key]
                proj = nf1.createVariable(variable_name, 'i4')
                # Copy all other attributes
                for i in metadata_ncdf[proj_key]:
                    setattr(proj, i, metadata_ncdf[proj_key][i])

        value = nf1.createVariable(prefix, fillval, variable_dims, zlib=True, complevel=4, fill_value=nan_value)

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

        # Fill variables
        try:
            int_lons = settings.binding['internal.lons']
            int_lats = settings.binding['internal.lats']
            x1 = Decimal(__DECIMAL_FORMAT.format(int_lons[0]))
            x2 = Decimal(__DECIMAL_FORMAT.format(int_lons[1]))
            y1 = Decimal(__DECIMAL_FORMAT.format(int_lats[0]))
            y2 = Decimal(__DECIMAL_FORMAT.format(int_lats[1]))
            cellSizeX = abs(x2 - x1)
            cellSizeY = abs(y2 - y1)
            lats = coordinates_range_from_array(int_lats)
            lons = coordinates_range_from_array(int_lons)
        except:
            cellSize = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().cellSize()))
            half_cell = cellSize * Decimal(0.5)
            xl = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().west())) + half_cell
            xr = xl + ncols * cellSize - half_cell
            yu = Decimal(__DECIMAL_FORMAT.format(pcraster.clone().north())) - half_cell
            yd = yu - nrows * cellSize + half_cell
            lats = coordinates_range(yu, nrows, -cellSize)
            lons = coordinates_range(xl, ncols, cellSize)
        nf1.variables[spatial_dims[1]][:] = lats
        nf1.variables[spatial_dims[0]][:] = lons

        if 'pr' in metadata_ncdf and 'esri_pe_string' in metadata_ncdf['pr']:
            value.esri_pe_string = metadata_ncdf['pr']['esri_pe_string']

    else:
        nf1 = Dataset(netfile, 'a')

    mapnp = numpy_operations.pcr2numpy(inputmap, np.nan)
    # Pack NAN values into short
    mapnp[np.isnan(mapnp)] = (nan_value - add_offset) * scale_factor
    if flag_time:
        # In case output6hourly==True, replicate four daily maps to get the 6 hourly output (EFCC-2316)
        # The timestep need to increase by 4
        if output6hourly:
            time_frequency = 6
            for i in range(4):
                map_idx = flag * 4 + i
                nf1.variables[time_variable][map_idx] = (timestep * 4 - 4 + i) * time_frequency
                nf1.variables[prefix][map_idx, :, :] = mapnp
        else:  # Generate daily output
            nf1.variables[time_variable][flag] = timestep - 1
            nf1.variables[prefix][flag, :, :] = mapnp
    else:
        nf1.variables[prefix][:, :] = mapnp
    nf1.close()
