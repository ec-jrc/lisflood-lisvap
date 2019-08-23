
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


from . import CutMap, NetcdfMetadata

if IS_PYTHON2:
    from pathlib2 import Path
else:
    from pathlib import Path


def writenet(flag, inputmap, netfile, timestep, value_standard_name, value_long_name, value_unit, fillval, startdate, flag_time=True):
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
    row = np.abs(cutmap.cuts[3] - cutmap.cuts[2])
    col = np.abs(cutmap.cuts[1] - cutmap.cuts[0])
    if flag == 0:
        nf1 = Dataset(netfile, 'w', format='NETCDF4_CLASSIC')

        # general Attributes
        nf1.history = 'Created ' + xtime.ctime(xtime.time())
        nf1.Conventions = 'CF-1.4'
        nf1.Source_Software = 'Lisvap'
        nf1.source = 'Lisvap output maps'

        metadata_ncdf = NetcdfMetadata.instance()

        # Dimension
        spatial_dims = tuple([c for c in ('y', 'lat', 'x', 'lon') if c in metadata_ncdf])
        for dim_name, dim_size in zip(spatial_dims, [row, col]):
            nf1.createDimension(dim_name, dim_size)
            coord = nf1.createVariable(dim_name, 'f8', (dim_name, ))
            for i in metadata_ncdf[dim_name]:
                if i != '_FillValue':
                    # to avoid AttributeError ("_FillValue attribute must be set when variable is created") when writing output nc attributes
                    setattr(coord, i, metadata_ncdf[dim_name][i])

        if flag_time:
            nf1.createDimension('time', None)
            time = nf1.createVariable('time', 'f8', ('time',))
            time.standard_name = 'time'
            time.units = 'days since %s' % startdate.strftime('%Y-%m-%d %H:%M:%S.0')
            time.calendar = 'gregorian'
            value = nf1.createVariable(prefix, fillval, ('time', ) + spatial_dims, zlib=True)
        else:
            value = nf1.createVariable(prefix, fillval, spatial_dims, zlib=True)

        value.standard_name = value_standard_name
        value.long_name = value_long_name
        value.units = value_unit
        # value.esri_pe_string='PROJCS["ETRS_1989_LAEA",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["false_easting",4321000.0],PARAMETER["false_northing",3210000.0],PARAMETER["central_meridian",10.0],PARAMETER["latitude_of_origin",52.0],UNIT["Meter",1.0]]'
        # projection
        if 'laea' in metadata_ncdf:
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

        if 'lambert_azimuthal_equal_area' in metadata_ncdf:
            proj = nf1.createVariable('laea', 'i4')
            for i in metadata_ncdf['lambert_azimuthal_equal_area']:
                setattr(proj, i, metadata_ncdf['lambert_azimuthal_equal_area'][i])

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

        nf1.variables[spatial_dims[0]][:] = lats
        nf1.variables[spatial_dims[1]][:] = lons

        if 'pr' in metadata_ncdf and 'esri_pe_string' in metadata_ncdf['pr']:
            value.esri_pe_string = metadata_ncdf['pr']['esri_pe_string']

    else:
        nf1 = Dataset(netfile, 'a')

    mapnp = numpy_operations.pcr2numpy(inputmap, np.nan)
    if flag_time:
        nf1.variables['time'][flag] = timestep - 1
        nf1.variables[prefix][flag, :, :] = mapnp
    else:
        nf1.variables[prefix][:, :] = mapnp
    nf1.close()
