import inspect
import os
import sys
import getopt
import xml.dom.minidom
from functools import wraps


def cached(f):
    _cache = {}
    @wraps(f)
    def _decorator(args):
        args = tuple(args)
        if args not in _cache:
            _cache[args] = f(args)
        return _cache[args]
    return _decorator


class Singleton(type):
    """
    Singleton that keep single instance for single set of arguments. E.g.:
    assert Singleton('spam') is not Singleton('eggs')
    assert Singleton('spam') is Singleton('spam')
    """
    _instances = {}
    _init = {}
    _current = {}

    def __init__(cls, name, bases, dct):
        cls._init[cls] = dct.get('__init__', None)
        super(Singleton, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs):
        init = cls._init[cls]
        if init is not None:
            key = (cls, frozenset(inspect.getcallargs(init, None, *args, **kwargs).items()))
        else:
            key = cls

        if key not in cls._instances:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
        cls._current[cls] = cls._instances[key]
        return cls._instances[key]


class LisSettings(object):
    __metaclass__ = Singleton

    def __init__(self, settings_file, options_xml):
        dom = xml.dom.minidom.parse(settings_file)
        domopt = xml.dom.minidom.parse(options_xml)

        self.flags = self.config_flags()

        user_settings, bindings = self.get_binding(dom)
        self.binding = bindings
        self.options = self.get_options(dom, domopt)
        self.report_steps = self._report_steps(user_settings, bindings)
        self.report_timeseries = self._report_tss(domopt, self.options)
        reportMapsSteps, reportMapsAll, reportMapsEnd = self._reported_maps(self.options, domopt)
        self.report_maps_steps = reportMapsSteps
        self.report_maps_all = reportMapsAll
        self.report_maps_end = reportMapsEnd

    @classmethod
    def instance(cls):
        return cls._current[cls]

    @staticmethod
    def _report_steps(user_settings, bindings):
        ReportSteps = {}
        repsteps = user_settings['ReportSteps'].split(',')
        if repsteps[-1] == 'endtime':
            repsteps[-1] = bindings['StepEnd']
        jjj = []
        for i in repsteps:
            if '..' in i:
                j = map(int, i.split('..'))
                for jj in xrange(j[0], j[1] + 1):
                    jjj.append(jj)
            else:
                jjj.append(i)
        ReportSteps['rep'] = map(int, jjj)
        return ReportSteps

    @staticmethod
    def _report_tss(domopt, options):
        repTimeserie = {}
        reportTimeSerieAct = {}
        # running through all times series
        reportTimeSerie = domopt.getElementsByTagName("lftime")[0]
        for repTime in reportTimeSerie.getElementsByTagName("setserie"):
            d = {}
            for key in repTime.attributes.keys():
                if key != 'name':
                    value = repTime.attributes[key].value
                    d[key] = value.split(',')
            key = repTime.attributes['name'].value
            repTimeserie[key] = d
            repOpt = repTimeserie[key]['repoption']

            if 'restrictoption' not in repTimeserie[key]:
                repTimeserie[key]['restrictoption'] = ['']
            if 'operation' not in repTimeserie[key]:
                repTimeserie[key]['operation'] = ['']
            restOpt = repTimeserie[key]['restrictoption']

            # sort out if this option is not active
            # put in if one of this option is active
            for i in repOpt:
                for o1key in options:
                    if options[o1key]:  # if option is active = 1
                        if o1key == i:
                            # option is active and time series has this option to select it
                            # now test if there is any restrictions
                            allow = True
                            for j in restOpt:
                                for o2key in options:
                                    if o2key == j:
                                        if not options[o2key]:
                                            allow = False
                            if allow:
                                reportTimeSerieAct[key] = repTimeserie[key]
        return reportTimeSerieAct

    @staticmethod
    def _reported_maps(options, domopt):

        # local vars
        repMaps = {}

        # -------------------------
        # out vars
        reportMapsSteps = {}
        reportMapsAll = {}
        reportMapsEnd = {}
        # -------------------------

        # running through all maps

        reportMap = domopt.getElementsByTagName("lfmaps")[0]
        for repMap in reportMap.getElementsByTagName("setmap"):
            d = {}
            for key in repMap.attributes.keys():
                if key != 'name':
                    value = repMap.attributes[key].value
                    d[key] = value.split(',')
            key = repMap.attributes['name'].value
            repMaps[key] = d
            if 'all' not in repMaps[key]:
                repMaps[key]['all'] = ['']
            repAll = repMaps[key]['all']
            if 'steps' not in repMaps[key]:
                repMaps[key]['steps'] = ['']
            repSteps = repMaps[key]['steps']
            if 'end' not in repMaps[key]:
                repMaps[key]['end'] = ['']
            repEnd = repMaps[key]['end']
            if 'restrictoption' not in repMaps[key]:
                repMaps[key]['restrictoption'] = ['']
            restOpt = repMaps[key]['restrictoption']
            if 'unit' not in repMaps[key]:
                repMaps[key]['unit'] = ['']
            # repUnit = repMaps[key]['unit']

            #  -------- All -----------------
            # sort out if this option is not active
            # put in if one of this option is active
            for i in repAll:
                # run through all the output option
                for o1key in options:
                    # run through all the options
                    if options[o1key]:  # if option is active = 1
                        if o1key == i:
                            # option is active and time series has this option to select it
                            # now test if there is any restrictions
                            allow = True
                            for j in restOpt:
                                # running through all the restrictions
                                for o2key in options:
                                    if (o2key == j) and (not (options[o2key])):
                                        allow = False
                            if allow:
                                reportMapsAll[key] = repMaps[key]

            #  -------- Steps -----------------
            for i in repSteps:
                for o1key in options:
                    if options[o1key]:  # if option is active = 1
                        if o1key == i:
                            allow = True
                            for j in restOpt:
                                for o2key in options:
                                    if (o2key == j) and (not (options[o2key])):
                                        allow = False
                            if allow:
                                reportMapsSteps[key] = repMaps[key]

            #  -------- End -----------------
            for i in repEnd:
                for o1key in options:
                    if options[o1key]:  # if option is active = 1
                        if o1key == i:
                            allow = True
                            for j in restOpt:
                                for o2key in options:
                                    if (o2key == j) and (not (options[o2key])):
                                        allow = False
                            if allow:
                                reportMapsEnd[key] = repMaps[key]

        return reportMapsSteps, reportMapsAll, reportMapsEnd

    @staticmethod
    def config_flags():
        """ read flags - according to the flags the output is adjusted
            quiet, veryquiet, loud, checkfiles, noheader, printtime
        """
        flag_names = ['quiet', 'veryquiet', 'loud',
                      'checkfiles', 'noheader', 'printtime']
        flags = {'quiet': False, 'veryquiet': False, 'loud': False,
                 'check': False, 'noheader': False, 'printtime': False}

        @cached
        def _flags(argz):

            try:
                opts, arguments = getopt.getopt(argz, 'qvlcht', flag_names)
            except getopt.GetoptError as e:
                from lisvap1 import usage
                usage()
            else:
                for o, a in opts:
                    if o in ('-q', '--quiet'):
                        flags['quiet'] = True
                    elif o in ('-v', '--veryquiet'):
                        flags['veryquiet'] = True
                    elif o in ('-l', '--loud'):
                        flags['loud'] = True
                    elif o in ('-c', '--checkfiles'):
                        flags['check'] = True
                    elif o in ('-h', '--noheader'):
                        flags['noheader'] = True
                    elif o in ('-t', '--printtime'):
                        flags['printtime'] = True
            return flags

        if 'test' in sys.argv[0] or 'test' in sys.argv[1]:
            return flags
        args = sys.argv[2:]
        return _flags(args)

    @staticmethod
    def get_options(dom, domopt):
        # getting all possible option from the general optionxml
        # and setting them to their default value
        options = {}
        option_setting = {}
        optDef = domopt.getElementsByTagName("lfoptions")[0]
        for optset in optDef.getElementsByTagName("setoption"):
            options[optset.attributes['name'].value] = bool(int(optset.attributes['default'].value))

        # getting option set in the specific settings file
        # and resetting them to their choice value
        optSet = dom.getElementsByTagName("lfoptions")[0]
        for optset in optSet.getElementsByTagName("setoption"):
            option_setting[optset.attributes['name'].value] = bool(int(optset.attributes['choice'].value))
        for key in option_setting.keys():
            options[key] = option_setting[key]

        # reverse the initLisflood option to use it as a restriction for output
        # eg. produce output if not(initLisflood)
        options['nonInit'] = not (options['InitLisflood'])
        return options

    @staticmethod
    def get_binding(dom):
        binding = {}
        user = {'ProjectDir': os.path.normpath(os.path.join(os.path.dirname(__file__), '../'))}
        #  built-in variables
        user['ProjectPath'] = user['ProjectDir']

        lfuse = dom.getElementsByTagName("lfuser")[0]
        for userset in lfuse.getElementsByTagName("textvar"):
            user[userset.attributes['name'].value] = str(userset.attributes['value'].value)
            binding[userset.attributes['name'].value] = str(userset.attributes['value'].value)

        # get all the binding in the last part of the settingsfile  = lfbinding
        bind = dom.getElementsByTagName("lfbinding")[0]
        for bindset in bind.getElementsByTagName("textvar"):
            binding[bindset.attributes['name'].value] = str(bindset.attributes['value'].value)

        # replace/add the information from lfuser to lfbinding
        for i in binding:
            expr = binding[i]
            while expr.find('$(') > -1:
                a1 = expr.find('$(')
                a2 = expr.find(')')
                try:
                    s2 = user[expr[a1 + 2:a2]]
                except KeyError:
                    print 'no ', expr[a1 + 2:a2], ' in lfuser defined'
                else:
                    expr = expr.replace(expr[a1:a2 + 1], s2)
            binding[i] = expr
        return user, binding
