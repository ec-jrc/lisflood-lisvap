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
from __future__ import (absolute_import, print_function, unicode_literals)
from nine import str, range

import datetime
import sys
from bisect import bisect_left

from dateutil import parser
import numpy as np
import pcraster
from pcraster import numpy_operations, Nominal
from pcraster.framework.dynamicFramework import DynamicFramework
from pcraster.operations import scalar, defined, maptotal, ifthenelse, mapminimum, mapmaximum

from . import LisfloodError
from .decorators import counted


def valuecell(coordx, coordstr):
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

    for i in range(int(len(coord) / 2)):
        col = int((coord[i * 2] - pcraster.clone().west()) / pcraster.clone().cellSize())
        row = int((pcraster.clone().north() - coord[i * 2 + 1]) / pcraster.clone().cellSize())
        if 0 <= col < pcraster.clone().nrCols() and 0 <= row < pcraster.clone().nrRows():
            null[row, col] = i + 1
        else:
            msg = 'Coordinates: {}, {} to put value in is outside mask map - col,row: {}, {}'.format(coord[i * 2], coord[i * 2 + 1], col, row)
            raise LisfloodError(msg)

    return numpy_operations.numpy2pcr(Nominal, null, -9999)


def take_closest(a_list, a_number):
    """ Returns the closest left value to myNumber in myList

    Assumes myList is sorted. Returns closest left value to myNumber.
    If myList is sorted in raising order, it returns the closest smallest value.
    https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value

    :param a_list: list of ordered values
    :param a_number: number to be searched in a_list
    :return: closest left number to a_number in a_list
    """
    pos = bisect_left(a_list, a_number)
    if pos == 0:
        return a_list[0]
    if pos == len(a_list):
        return a_list[-1]
    before = a_list[pos - 1]
    return before


def get_calendar_configuration(netcdf_file_obj, settings=None):
    """
    Retrieves the units and calendar type from a netcdf file

    :param: netcdf_file_obj: netCDF file object
    :param: settings: Internal settings dictionary containing the system configurations.
            If provided it will setup/bind 'internal.time.unit' and 'internal.time.calendar'
            with the corresponding values in case they are not set yet
    :default: u'hours since 2015-01-01 06:00:00', u'gregorian'
    :returns: unit, calendar
    """
    try:
        t_unit = netcdf_file_obj.variables['time'].units  # get unit (u'hours since 2015-01-01 06:00:00')
        t_cal = netcdf_file_obj.variables['time'].calendar  # get calendar from netCDF file
    except AttributeError:  # Attribute does not exist
        t_unit = u'hours since 1990-01-01 06:00:00'
        t_cal = u'gregorian'  # Use standard calendar
    if settings is not None and not ('internal.time.unit' in settings.binding and
                                     'internal.time.calendar' in settings.binding):
        settings.binding['internal.time.unit'] = t_unit
        settings.binding['internal.time.calendar'] = t_cal
    return t_unit, t_cal


def calendar(date_or_ts):
    """ Get date or number of steps from input.

    Get date from input string using one of the available formats or get time step number from input number or string.
    Used to get the date from CalendarDayStart (input) in the settings xml

    :param date_or_ts: string containing a date in one of the available formats or time step number as number or string
    :rtype: datetime object or float number
    :returns: date as datetime or time step number as float
    :raises ValueError: stop if input is not a step number AND it is in wrong date format
    """
    if isinstance(date_or_ts, (float, int)):
        return float(date_or_ts)

    try:
        # try reading step number from number or string
        date = parser.parse(date_or_ts, dayfirst=True)
    except (TypeError, ValueError) as e:
        # if cannot read input then stop
        msg = ' Wrong step or date format: {}, Input {} '.format(e, date_or_ts)
        raise LisfloodError(msg)
    else:
        return date


def date_to_int(date_in, both=False):
    """ Get number of steps between dateIn and CalendarDayStart.

    Get the number of steps between dateIn and CalendarDayStart and return it as integer number.
    It can now compute the number of sub-daily steps.
    dateIn can be either a date or a number. If dateIn is a number, it must be the number of steps between
    dateIn and CalendarDayStart.

    :param date_in: date as string or number
    :param both: if true it returns both the number of steps as integer and the input date as string. If false only
    the number of steps as integer is returned
    :return: number of steps as integer and input date as string
    """
    from lisvap.utils import LisSettings
    settings = LisSettings.instance()
    binding = settings.binding
    # CM: get reference date to be used with step numbers from 'CalendarDayStart' in Settings.xml file
    date1 = calendar(date_in)
    begin = calendar(binding['CalendarDayStart'])
    # CM: get model time step as float form 'DtSec' in Settings.xml file
    DtSec = float(binding['DtSec'])
    # CM: compute fraction of day corresponding to model time step as float
    # DtDay = float(DtSec / 86400)
    # Time step, expressed as fraction of day (same as self.var.DtSec and self.var.DtDay)

    if type(date1) is datetime.datetime:
        str1 = date1.strftime("%d/%m/%Y %H:%M")
        # CM: get total number of seconds corresponding to the time interval between dateIn and CalendarDayStart
        timeinterval_in_sec = int((date1 - begin).total_seconds())
        # CM: get total number of steps between dateIn and CalendarDayStart
        int1 = int(timeinterval_in_sec / DtSec + 1)
    else:
        int1 = int(date1)
        str1 = str(date1)
    return int1, str1 if both else int1


def checkdate(start, end):
    """ Check simulation start and end dates or timesteps

    Check simulation start and end dates/timesteps to be later than begin date (CalendarStartDay).
    If dates are used for binding[start] and binding[end], it substitutes dates with time step numbers.

    :param start: start date for model run (# or date as string)
    :param end: end date for model run (# or date as string)
    """
    from . import LisSettings
    settings = LisSettings.instance()
    binding = settings.binding
    # CM: calendar date start (CalendarDayStart)
    begin = calendar(binding['CalendarDayStart'])

    int_start, str_start = date_to_int(binding[start], True)
    # CM mod
    # CM overwrite date with time step
    binding[start] = int_start
    int_end, str_end = date_to_int(binding[end], True)
    # CM mod
    binding[end] = int_end

    # test if start and end > begin
    if int_start < 0 or int_end < 0 or (int_end - int_start) < 0:
        str_begin = begin.strftime("%d/%m/%Y %H:%M")
        msg = "Simulation start date and/or simulation end date are wrong or do not match CalendarStartDate!\n" + \
              "CalendarStartDay: " + str_begin + "\n" + \
              "Simulation start: " + str_start + " - " + str(int_start) + "\n" + \
              "Simulation end: " + str_end + " - " + str(int_end)
        raise LisfloodError(msg)
    return


class DynamicFrame(DynamicFramework):
    """Adjusting the def _atStartOfTimeStep defined in DynamicFramework
       for a real quiet output
    """
    rquiet = True
    rtrace = False

    def _atStartOfTimeStep(self, step):
        self._userModel()._setInTimeStep(True)
        if not self.rquiet:
            if not self.rtrace:
                msg = u"#"
            else:
                msg = u"%s<time step=\"%s\">\n" % (self._indentLevel(), step)
            sys.stdout.write(msg)
            sys.stdout.flush()


@counted
def checkmap(name, value, map, flagmap, find):
    """ check maps if they fit to the mask map
    """
    s = [name, value]
    MMaskMap = 0
    if flagmap:
        amap = scalar(defined(MMaskMap))
        try:
            smap = scalar(defined(map))
        except:
            msg = "Map: " + name + " in " + value + " does not fit"
            if name == "LZAvInflowMap":
                msg += "\nTry to execute the initial run first"
            raise LisfloodError(msg)

        mvmap = maptotal(smap)
        mv = pcraster.cellvalue(mvmap, 1, 1)[0]
        s.append(mv)

        less = maptotal(ifthenelse(defined(MMaskMap), amap - smap, scalar(0)))
        s.append(pcraster.cellvalue(less, 1, 1)[0])
        less = mapminimum(scalar(map))
        s.append(pcraster.cellvalue(less, 1, 1)[0])
        less = maptotal(scalar(map))
        s.append(pcraster.cellvalue(less, 1, 1)[0] / mv) if mv > 0 else s.append('0')
        less = mapmaximum(scalar(map))
        s.append(pcraster.cellvalue(less, 1, 1)[0])
        if find > 0:
            if find == 2:
                s.append('last_Map_used')
            else:
                s.append('')

    else:
        s.append(0)
        s.append(0)
        s.append(float(map))
        s.append(float(map))
        s.append(float(map))

    if checkmap.called == 1:  # FIXME omg
        print ("%-25s%-40s%11s%11s%11s%11s%11s" % ("Name", "File/Value", "nonMV", "MV", "min", "mean", "max"))
    print ("%-25s%-40s%11i%11i%11.2f%11.2f%11.2f" % (s[0], s[1][-39:], s[2], s[3], s[4], s[5], s[6]))
    return
