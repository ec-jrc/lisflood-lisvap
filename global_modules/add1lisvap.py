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

from zusatz import *

from netCDF4 import Dataset
import numpy as np
import time as xtime
import pdb

# ------------------------------

def valuecell(mask, coordx, coordstr):
    """
    to put a value into a pcraster map -> invert of cellvalue
    pcraster map is converted into a numpy array first
    """
    coord = []
    for xy in coordx:
        try:
            coord.append(float(xy))
        except:
            msg = "Gauges: " + xy + " in " + coordstr + " is not a coordinate"
            raise LisfloodError(msg)

    null = np.zeros((pcraster.clone().nrCols(), pcraster.clone().nrRows()))
    null[null == 0] = -9999

    for i in xrange(int(len(coord) / 2)):
        col = int(
            (coord[i * 2] - pcraster.clone().west()) / pcraster.clone().cellSize())
        row = int(
            (pcraster.clone().north() - coord[i * 2 + 1]) / pcraster.clone().cellSize())
        #if col >= 0 and row >= 0 and col < pcraster.clone().nrCols() and row < pcraster.clone().nrRows():
        if col >= 0 and row >= 0 and col < pcraster.clone().nrCols() and row < pcraster.clone().nrRows():
            null[row, col] = i + 1
        else:
            msg = "Coordinates: " + str(coord[i * 2]) + ',' + str(
                coord[i * 2 + 1]) + " to put value in is outside mask map - col,row: " + str(col) + ',' + str(row)
            raise LisfloodError(msg)

    map = numpy2pcr(Nominal, null, -9999)
    return map


def metaNetCDF(name):
    """
    get the map metadata from netcdf
    """
    filename = name.split('.')[0] + '.nc'
    if not(os.path.isfile(filename)):
        msg = "Checking netcdf map extend \n" + filename + " does not exists"
        raise LisfloodError(msg)
    nf1 = Dataset(filename, 'r')
    for var in nf1.variables:
        metadataNCDF[var] = nf1.variables[var].__dict__
        print 'dict',metadataNCDF[var]
    nf1.close()


def mapattrNetCDF(name):
    """
    get the map attributes like col, row etc from a ntcdf map
    and define the rectangular of the mask map inside the netcdf map
    """
    filename = name.split('.')[0] + '.nc'
    if not(os.path.isfile(filename)):
        msg = "Checking netcdf map extend \n" + filename + " does not exists"
        raise LisfloodError(msg)
    nf1 = Dataset(filename, 'r')
    x1 = nf1.variables.values()[0][0]
    x2 = nf1.variables.values()[0][1]
    xlast = nf1.variables.values()[0][-1]
    y1 = nf1.variables.values()[1][0]
    ylast = nf1.variables.values()[1][-1]
    if y1 < ylast: y1,ylast = ylast,y1
    cellSize = round(np.abs(x2 - x1),5)
    nrRows = np.abs(ylast - y1) / cellSize + 1
    nrCols = np.abs(xlast - x1) / cellSize + 1
    x = x1 - cellSize / 2
    y = y1 + cellSize / 2
    nf1.close()

    cut0 = int(np.abs(maskmapAttr['x'] - x) / maskmapAttr['cell'])
    cut1 = cut0 + maskmapAttr['col']
    cut2 = int(np.abs(maskmapAttr['y'] - y) / maskmapAttr['cell'])
    cut3 = cut2 + maskmapAttr['row']
    print 'cut',cut0,cut1,cut2,cut3

    if maskmapAttr['cell'] != cellSize:
        msg = "Cell size different in maskmap: " + \
            binding['MaskMap'] + " and: " + filename
        raise LisfloodError(msg)

    return (cut0, cut1, cut2, cut3)

def loadsetclone(name):
    """
    load the maskmap and set as clone
    """
    filename = binding[name]
    coord = filename.split()
    if len(coord) == 5:
        # changed order of x, y i- in setclone y is first in Lisflood
        # settings x is first
        # setclone row col cellsize xupleft yupleft
        setclone(int(coord[1]), int(coord[0]), float(coord[2]), float(coord[3]), float(coord[4]))
        null = np.zeros((int(coord[0]), int(coord[1])))
        null[null == 0] = 1
        map = numpy2pcr(Boolean, null, -9999)

    elif len(coord) == 1:
        try:
         
            # try to read a pcraster map
            print 'filename',filename
            setclone(filename)
            map = boolean(readmap(filename))
            flagmap = True

        except:
            filename = binding[name].split('.')[0] + '.nc'
            nf1 = Dataset(filename, 'r')
            value = nf1.variables.items()[-1][0]  # get the last variable name

            x1 = nf1.variables.values()[0][0]
            x2 = nf1.variables.values()[0][1]
            xlast = nf1.variables.values()[0][-1]
            y1 = nf1.variables.values()[1][0]
            ylast = nf1.variables.values()[1][-1]
            cellSize = np.abs(x2 - x1)
            nrRows = int(np.abs(ylast - y1) / cellSize + 1)
            nrCols = int(np.abs(xlast - x1) / cellSize + 1)
            x = x1 - cellSize / 2
            y = y1 + cellSize / 2

            #mapnp = np.array(nf1.variables[value])
            mapnp = nf1.variables[value][0:nrRows, 0:nrCols]

            nf1.close()

            # setclone  row col cellsize xupleft yupleft
            setclone(nrRows,nrCols, cellSize, x, y)

            map = numpy2pcr(Boolean, mapnp, 0)
            #map = boolean(map)
            flagmap = True

        if Flags['check']:
            checkmap(name, filename, map, flagmap, 0)

    else:
        msg = "Maskmap: " + Mask + \
            " is not a valid mask map nor valid coordinates"
        raise LisfloodError(msg)

    # Definition of cellsize, coordinates of the meteomaps and maskmap
    # need some love for error handling
    print 'mask',maskmapAttr
    maskmapAttr['x'] = pcraster.clone().west()
    maskmapAttr['y'] = pcraster.clone().north()
    maskmapAttr['col'] = pcraster.clone().nrCols()
    maskmapAttr['row'] = pcraster.clone().nrRows()
    maskmapAttr['cell'] = pcraster.clone().cellSize()
    return map

def loadmap(name):
    """
    load a static map either value or pcraster map or netcdf
    """
    value = binding[name]
    filename = value
    try:
        map = float(value)
        flagmap = False
        load = True
    except ValueError:
        try:
            # try to read a pcraster map
            map = readmap(value)
            flagmap = True
            load = True
        except:
            load = False
    if not(load):
        # read a netcdf  (single one not a stack)
        # filename=name+".nc"

        filename = value.split('.')[0] + '.nc'
        # value = os.path.basename(value).split('.')[0]

        # get mapextend of netcdf map
        # and calculate the cutting
        cut0, cut1, cut2, cut3 = mapattrNetCDF(filename)

        # load netcdf map but only the rectangle needed
        nf1 = Dataset(filename, 'r')
        value = nf1.variables.items()[-1][0]  # get the last variable name
        mapnp = nf1.variables[value][cut2:cut3, cut0:cut1]
        nf1.close()

        # check if integer map (like outlets, lakes etc
        checkint=str(mapnp.dtype)
        if checkint=="int16" or checkint=="int32":
            mapnp[mapnp.mask]=-9999
            map = numpy2pcr(Nominal, mapnp, -9999)
        elif checkint=="int8":
            map = numpy2pcr(Nominal, mapnp, 0)
        else:
            mapnp[np.isnan(mapnp)] = -9999
            map = numpy2pcr(Scalar, mapnp, -9999)

        # if the map is a ldd
        if value.split('.')[0][-3:] == 'ldd':
            map = ldd(nominal(map))
        flagmap = True

    if Flags['check']:
        checkmap(name, filename, map, flagmap, 0)
    return map


def loadLAI(value, pcrvalue, i):
    """
    load Leaf are map stacks  or water use maps stacks
    """
    try:
        map = readmap(pcrvalue)
        name = pcrvalue
    except:
        filename = value.split('.')[0] + '.nc'
        # value = os.path.basename(value).split('.')[0]

        # get mapextend of netcdf map
        # and calculate the cutting
        cut0, cut1, cut2, cut3 = mapattrNetCDF(filename)

        nf1 = Dataset(filename, 'r')
        value = nf1.variables.items()[-1][0]  # get the last variable name
        mapnp = nf1.variables[value][i, cut2:cut3, cut0:cut1]
        nf1.close()
        mapnp[np.isnan(mapnp)] = -9999
        map = numpy2pcr(Scalar, mapnp, -9999)
        name = filename

    if Flags['check']:
        checkmap(os.path.basename(pcrvalue), name, map, True, 0)
    return map


def readmapsparse(name, time, oldmap):
    """
    load stack of maps 1 at each timestamp in Pcraster format
    """

    filename = generateName(name, time)
    try:
        map = readmap(filename)
        find = 1
    except:
        find = 2
        if oldmap is None:
            for i in range(time - 1, 0, -1):
                altfilename = generateName(name, i)
                if os.path.exists(altfilename):
                    map = readmap(altfilename)
                    find = 1
                    # break
            if find == 2:
                msg = "no map in stack smaller than: " + filename
                raise LisfloodError(msg)
        else:
            map = oldmap
            if Flags['loud']:
                s = " last_%s" % (os.path.basename(name))
                print s,
    if Flags['check']:
        checkmap(os.path.basename(name), filename, map, True, find)
    return map


def readnetcdf(name, time):
    """
      load stack of maps 1 at each timestamp in netcdf format
    """

    filename = name + ".nc"
    # value = os.path.basename(name)

    number = time - 1

    nf1 = Dataset(filename, 'r')
    value = nf1.variables.items()[-1][0]  # get the last variable name
    # bigmap=nf1.variables['value'][number,:,:]
    mapnp = nf1.variables[value][
        number, cutmap[2]:cutmap[3], cutmap[0]:cutmap[1]]
    nf1.close()
    mapnp[np.isnan(mapnp)] = -9999
    map = numpy2pcr(Scalar, mapnp, -9999)
    timename = os.path.basename(name) + str(time)
    if Flags['check']:
        checkmap(timename, filename, map, True, 1)
    return map


def generateName(name, time):
    """Returns a filename based on the name and time step passed in.
    The resulting name obeys the 8.3 DOS style format. The time step
    will be added to the end of the filename and be prepended by 0's if
    needed.
    The time step normally ranges from [1, nrTimeSteps].
    The length of the name should be max 8 characters to leave room for
    the time step.
    The name passed in may contain a directory name.
    See also: generateNameS(), generateNameST()
    """
    head, tail = os.path.split(name)

    if re.search("\.", tail):
        msg = "File extension given in '" + name + "' not allowed"
        raise LisfloodError(msg)
    if len(tail) == 0:
        msg = "No filename specified"
        raise LisfloodError(msg)
    if len(tail) > 8:
        msg = "Filename '" + name + "' must be shorter than 8 characters"
        raise LisfloodError(msg)
    if time < 0:
        msg = "Timestep must be larger than 0"
        raise LisfloodError(msg)

    nr = "%d" % (time)
    space = 11 - (len(tail) + len(nr))
    assert space >= 0
    result = "%s%s%s" % (tail, space * "0", nr)
    result = "%s.%s" % (result[:8], result[8:])
    assert len(result) == 12
    return os.path.join(head, result)


def Calendar(input):
    """
    get the date from CalendarDayStart in the settings xml
    """
    try:
        value = float(input)
    except ValueError:
        d = input.replace('.', '/')
        d = d.replace('-', '/')
        year = d.split('/')[-1:]
        if len(year[0]) == 4:
            formatstr = "%d/%m/%Y"
        else:
            formatstr = "%d/%m/%y"
        if len(year[0]) == 1:
            d = d.replace('/', '.', 1)
            d = d.replace('/', '/0')
            d = d.replace('.', '/')
            print d
        date = datetime.datetime.strptime(d, formatstr)
        # value=str(int(date.strftime("%j")))
    return date


def writenet(flag, inputmap, netfile, timestep, value_standard_name, value_long_name, value_unit, fillval, startdate, flagTime=True):
    """
    write a netcdf stack
    """

    prefix = netfile.split('/')[-1].split('\\')[-1].split('.')[0]
    netfile = netfile.split('.')[0] + '.nc'
    row = np.abs(cutmap[3] - cutmap[2])
    col = np.abs(cutmap[1] - cutmap[0])
    if flag == 0:
        #print 'filewrite',netfile
        nf1 = Dataset(netfile, 'w', format='NETCDF4_CLASSIC')

        # general Attributes
        nf1.history = 'Created ' + xtime.ctime(xtime.time())
        #nf1.history = 'Created ' + time.ctime(time.time())

        nf1.Conventions = 'CF-1.4'
        nf1.Source_Software = 'Python netCDF4'
        nf1.source = 'Lisvap output maps'

        # Dimension

        

        if 'y' in metadataNCDF.keys():
            lat = nf1.createDimension('y', row)  # x 950
            latitude = nf1.createVariable('y', 'f8', ('y'))
            for i in metadataNCDF['y']:
                exec('%s="%s"') % ("latitude." + i, metadataNCDF['y'][i])

        if 'lat' in metadataNCDF.keys():
            lat = nf1.createDimension('lat', row)  # x 950
            latitude = nf1.createVariable('lat', 'f8', ('lat'))
            for i in metadataNCDF['lat']:
                exec('%s="%s"') % ("latitude." + i, metadataNCDF['lat'][i])
        if 'x' in metadataNCDF.keys():
            lon = nf1.createDimension('x', col)  # x 1000
            longitude = nf1.createVariable('x', 'f8', ('x',))
            for i in metadataNCDF['x']:
                exec('%s="%s"') % ("longitude." + i, metadataNCDF['x'][i])

        if 'lon' in metadataNCDF.keys():
            lon = nf1.createDimension('lon', col)
            longitude = nf1.createVariable('lon', 'f8', ('lon',))
            for i in metadataNCDF['lon']:
                exec('%s="%s"') % ("longitude." + i, metadataNCDF['lon'][i])
                
        if flagTime:
            nf1.createDimension('time', None)
            time = nf1.createVariable('time', 'f8', ('time'))
            time.standard_name = 'time'
            # time.units ='days since 1990-01-01 00:00:00.0'
            time.units = 'days since %s' % startdate.strftime(
                "%Y-%m-%d %H:%M:%S.0")
            time.calendar = 'gregorian'
			# for i in metadataNCDF['time']: exec('%s="%s"') % ("time."+i, metadataNCDF['time'][i])

            value = nf1.createVariable(prefix,fillval,('time','y','x'),zlib=True)
            #value = nf1.createVariable(
            #    prefix, fillval, ('time', 'lat', 'lon'), zlib=True,least_significant_digit=2)

        else:
            value = nf1.createVariable(prefix,fillval,('y','x'),zlib=True)
            #value = nf1.createVariable(prefix, fillval, ('lat', 'lon'), zlib=True )
            # value = nf1.createVariable(prefix,'f4',('time','lat','lon'),zlib=True,complevel=9,least_significant_digit=digit)
            # value = nf1.createVariable(prefix,'f4',('time','lat','lon'),zlib=True,least_significant_digit=digit)

        value.standard_name = value_standard_name
        value.long_name = value_long_name
        value.units = value_unit
        # value.esri_pe_string='PROJCS["ETRS_1989_LAEA",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["false_easting",4321000.0],PARAMETER["false_northing",3210000.0],PARAMETER["central_meridian",10.0],PARAMETER["latitude_of_origin",52.0],UNIT["Meter",1.0]]'
        # projection
        if 'laea' in metadataNCDF.keys():
            proj = nf1.createVariable('laea', 'i4')
            proj.grid_mapping_name='lambert_azimuthal_equal_area'
            proj.false_easting=4321000.0
            proj.false_northing=3210000.0
            proj.longitude_of_projection_origin = 10.0
            proj.latitude_of_projection_origin = 52.0
            proj.semi_major_axis = 6378137.0
            proj.inverse_flattening = 298.257223563
            proj.proj4_params = "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs"
            proj.EPSG_code = "EPSG:3035"
            #for i in metadataNCDF['laea']:
                #exec('%s="%s"') % (
                #    "proj." + i, metadataNCDF['laea'][i])
                #print metadataNCDF['laea'][i]
                #exec('%s="%s\n"') % ("proj." + i, metadataNCDF['laea'][i])
                
        if 'lambert_azimuthal_equal_area' in metadataNCDF.keys():
            proj = nf1.createVariable('laea', 'i4')
            for i in metadataNCDF['lambert_azimuthal_equal_area']:
                exec('%s="%s"') % (
                    "proj." + i, metadataNCDF['lambert_azimuthal_equal_area'][i])

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

    if flagTime:
        nf1.variables['time'][flag] = timestep - 1
    mapnp = pcr2numpy(inputmap, np.nan)
    if flagTime:
        nf1.variables[prefix][flag, :, :] = mapnp
    else:
        # without timeflag
        nf1.variables[prefix][:, :] = mapnp
    nf1.close()
