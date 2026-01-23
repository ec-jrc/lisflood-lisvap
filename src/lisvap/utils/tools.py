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

import datetime
import sys
from bisect import bisect_left

import cftime
from dateutil import parser
import numpy as np
from .operators import scalar, defined, ifthenelse
from netCDF4 import num2date, date2num

from . import LisfloodError
from . import LisSettings
from .decorators import counted


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
    try:
        t_frequency = int(netcdf_file_obj.variables['time'].frequency) # get frequency
    except AttributeError:  # Attribute does not exist
        t_frequency = 1
    if settings is not None and not ('internal.time.unit' in settings.binding and
                                     'internal.time.calendar' in settings.binding and
                                     'internal.time.frequency' in settings.binding):
        settings.binding['internal.time.unit'] = t_unit
        settings.binding['internal.time.calendar'] = t_cal
        settings.binding['internal.time.frequency'] = t_frequency
    return t_unit, t_cal, t_frequency


def date2calendar(date, settings=None):
    if (settings is not None and
        'internal.time.unit' in settings.binding and
        'internal.time.calendar' in settings.binding):
        t_unit = settings.binding['internal.time.unit']
        t_cal = settings.binding['internal.time.calendar']
        date_number = date2num(date, units=t_unit, calendar=t_cal)
        date = num2date(date_number, t_unit, t_cal)
    return date


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
        # Convert the date into the calendar type as soon as it is defined
        settings = LisSettings.instance()
        date = date2calendar(date, settings)
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

    if isinstance(date1, cftime.datetime) or isinstance(date1, datetime.datetime):
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


class FrameworkError(Exception):
    def __init__(self,
        msg):
        self._msg = msg
    
    def __str__(self):
        return self._msg


class DynamicFrame():
    """Adjusting the def _atStartOfTimeStep defined in DynamicFramework
       for a real quiet output
    """
    rquiet = True
    rtrace = False

    _d_quiet = False
    _d_trace = False
    _d_debug = False
    _d_indentLevel = 0
    _d_inScript = False

    def __init__(self,
        userModel,
        lastTimeStep=0,
        firstTimestep=1):
        self._d_silentModelOutput = False
        self._d_silentFrameworkOutput = True
        self._d_quietProgressDots = False
        self._d_quietProgressSampleNr = False
    
        self._d_model = userModel
        self._testRequirements()
    
        # # fttb
        # self._addMethodToClass(self._readmapNew)
        # self._addMethodToClass(self._reportNew)
    
        try:
          self._userModel()._setNrTimeSteps(lastTimeStep)
          self._d_firstTimestep = firstTimestep
          self._userModel()._setFirstTimeStep(self._d_firstTimestep)
        except Exception as msg:
          sys.stderr.write('Error: %s\n' % str(msg))
          sys.exit(1)
    
    def _userModel(self):
        """
        Return the model instance provided by the user.
        """
        return self._d_model
    
    def run(self):
        """
        Run the dynamic user model.
    
        .. todo::
    
          This method depends on the filter frameworks concept. Shouldn't its run
          method call _runSuspend()?
        """
        self._atStartOfScript()
        if(hasattr(self._userModel(), "resume")):
          if self._userModel().firstTimeStep() == 1:
            self._runInitial()
          else:
            self._runResume()
        else:
          self._runInitial()
    
        self._runDynamic()
    
        # Only execute this section while running filter frameworks.
        if hasattr(self._userModel(), "suspend") and \
          hasattr(self._userModel(), "filterPeriod"):
          self._runSuspend()
    
        return 0
    
    def _testRequirements(self):
        """
        Test whether the user model models the
        :ref:`Dynamic Model Concept <dynamicModelConcept>`.
        """
        if hasattr(self._userModel(), "_userModel"):
          msg = "The _userModel method is deprecated and obsolete"
          self.showWarning(msg)
    
        if( not hasattr(self._userModel(), "dynamic") and not hasattr(self._userModel(), "run")):
          msg = "Cannot run dynamic framework: Implement dynamic method"
          raise FrameworkError(msg)
    
        if not hasattr(self._userModel(), "initial"):
          if self._debug():
            self.showWarning("No initial section defined.")

    def _trace(self):
        return DynamicFrame._d_trace
    
    def _debug(self):
        return DynamicFrame._d_debug
    
    def _indentLevel(self):
        return DynamicFrame._d_indentLevel * "  "
    
    def _traceIn(self, functionName):
        if not self._quiet():
          if self._trace():
            self.showMessage("%s<%s>" % (self._indentLevel(), functionName))
    
    def _traceOut(self, functionName):
        if not self._quiet():
          if self._trace():
            self.showMessage("%s</%s>" % (self._indentLevel(), functionName))

    def _quiet(self):
        """
        Return the quiet state.
        """
        return self._d_quietProgressDots
    
    def setQuiet(self, quiet=True):
        """
        Disables the progress display of timesteps.
        """
        self._d_quietProgressDots = quiet

    def setTrace(self,
        trace):
        """
        Trace framework output to stdout.
    
        `trace`
          True/False. Default is set to False.
    
        If tracing is enabled the user will get a detailed framework output
        in an XML style.
        """
        DynamicFrame._d_trace = trace
    
    def setDebug(self,
        debug):
        DynamicFrame._d_debug = debug

    def _atStartOfSample(self,
        nr):
        self._userModel()._d_inSample = True
    
        if not self._quietProgressSampleNr():
          if not self._trace():
            msg = u"%d " % (nr)
          else:
            msg = u"%s<sample nr=\"%s\">\n" % (self._indentLevel(), nr)
          # no showMessage here, \n not desired in non-trace "..." timestep output
          sys.stdout.write(msg)
          sys.stdout.flush()
    
    def _sampleFinished(self):
        self._userModel()._d_inSample = False
    
        if not self._quiet():
          #if not self._trace():
            #msg = "]"
          #else:
          if self._trace():
            msg = "%s</sample>" % (self._indentLevel())
            self.showMessage(msg)
    
    def _atStartOfFilterPeriod(self,
        nr):
        self._userModel()._d_inFilterPeriod = True
        if not self._d_model._quiet():
          if not self._d_model._trace():
            msg = "\nPeriod %d" % (nr + 1)
          else:
            msg = "%s<period nr=\"%s\">" % (self._indentLevel(), nr + 1)
    
          self.showMessage(msg)
    
    def _atEndOfFilterPeriod(self):
        self._userModel()._d_inFilterPeriod = False
        if not self._d_model._quiet():
          if self._d_model._trace():
            msg = "%s</period>" % (self._indentLevel())
            self.showMessage(msg)
    
    def _runInitial(self):
        self._userModel()._setInInitial(True)
        if(hasattr(self._userModel(), 'initial')):
          self._incrementIndentLevel()
          self._traceIn("initial")
          self._userModel().initial()
          self._traceOut("initial")
          self._decrementIndentLevel()
    
        self._userModel()._setInInitial(False)
    
    def _runDynamic(self):
        self._userModel()._setInDynamic(True)
        step = self._userModel().firstTimeStep()
        while step <= self._userModel().nrTimeSteps():
    
          self._incrementIndentLevel()
          self._atStartOfTimeStep(step)
          self._userModel()._setCurrentTimeStep(step)
          if hasattr(self._userModel(), 'dynamic'):
            self._incrementIndentLevel()
            self._traceIn("dynamic")
            self._userModel().dynamic()
            self._traceOut("dynamic")
            self._decrementIndentLevel()
    
          self._timeStepFinished()
          self._decrementIndentLevel()
          step += 1
    
        self._userModel()._setInDynamic(False)

    def _atStartOfTimeStep(self, step):
        self._userModel()._setInTimeStep(True)
        if not self.rquiet:
            if not self.rtrace:
                msg = u"#"
            else:
                msg = u"%s<time step=\"%s\">\n" % (self._indentLevel(), step)
            sys.stdout.write(msg)
            sys.stdout.flush()

    def _timeStepFinished(self):
        self._userModel()._setInTimeStep(False)
    
        if not self._quiet():
          if self._trace():
            self.showMessage("%s</time>" % (self._indentLevel()))
    
    def _atStartOfScript(self):
        if not self._d_inScript:
          self._userModel()._d_inScript = True
          if not self._quiet():
            if self._trace():
              self.showMessage("<script>")
    
    def _atEndOfScript(self):
        if self._d_inScript:
          self._d_inScript = False
          if not self._quiet():
            if not self._trace():
              msg = u"\n"
            else:
              msg = u"</script>\n"
            # showMessage does not work due to encode throw
            sys.stdout.write(msg)
            sys.stdout.flush()

    def _incrementIndentLevel(self):
        DynamicFrame._d_indentLevel += 1
    
    def _decrementIndentLevel(self):
        assert DynamicFrame._d_indentLevel > 0
        DynamicFrame._d_indentLevel -= 1
    
    def _scriptFinished(self):
        self._atEndOfScript()


@counted
def checkmap(name, value, npmap, flagmap, find):
    """ check maps if they fit to the mask map
    """
    s = [name, value]
    MMaskMap = 0
    if flagmap:
        amap = scalar(MMaskMap) # Set Maskmap to zeros
        try:
            smap = scalar(defined(npmap)) # Get a boolean map containing the cells from npmap in the mask map area
        except:
            msg = "Map: " + name + " in " + value + " does not fit"
            if name == "LZAvInflowMap":
                msg += "\nTry to execute the initial run first"
            raise LisfloodError(msg)

        mv = np.sum(smap) # sum all True values or the vales that are in the area
        s.append(mv)

        less = np.sum(ifthenelse(defined(scalar(MMaskMap)), amap - smap, scalar(0)))
        s.append(less)
        less = np.min(scalar(npmap))
        s.append(less)
        less = np.sum(scalar(npmap))
        s.append(less / mv) if mv > 0 else s.append('0')
        less = np.max(scalar(npmap))
        s.append(less)
        if find > 0:
            if find == 2:
                s.append('last_Map_used')
            else:
                s.append('')
    else:
        s.append(0)
        s.append(0)
        s.append(float(npmap))
        s.append(float(npmap))
        s.append(float(npmap))

    # called comes from the counted decorator and counts the number of times the function is called
    if checkmap.called == 1:
        print ("%-25s%-40s%11s%11s%11s%11s%11s" % ("Name", "File/Value", "nonMV", "MV", "min", "mean", "max"))
    print ("%-25s%-40s%11i%11i%11.2f%11.2f%11.2f" % (s[0], s[1][-39:], s[2], s[3], s[4], s[5], s[6]))
    return
