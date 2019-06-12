from collections import namedtuple

TimeSeries = namedtuple('TimeSeries', 'name, output_var, where, repoption, restrictoption, operation')
ReportedMap = namedtuple('ReportedMap', 'name, output_var, unit, end, steps, all, restrictoption')

defaults = {
    'useTavg': False,
    'readNetcdfStack': False, 'writeNetcdfStack': False, 'writeNetcdf': False,
    'repAvTimeseries': False,
    'repET0Maps': False, 'repES0Maps': False, 'repE0Maps': True, 'repTAvgMaps': False,
    'EFAS': True, 'CORDEX': False, 'GLOFAS': False,
    'timeseries': [
        TimeSeries(name='TAvgTS', output_var='TAvg', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='ET0TS', output_var='ETRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='E0TS', output_var='EWRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='ES0TS', output_var='ESRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
    ],
    'reportedmaps': [
        ReportedMap(name='ET0Maps', output_var='ETRef', unit='mm/day', end='', steps='', all='repET0Maps', restrictoption=''),
        ReportedMap(name='E0Maps', output_var='EWRef', unit='mm/day', end='', steps='', all='repE0Maps', restrictoption=''),
        ReportedMap(name='ES0Maps', output_var='ESRef', unit='mm/day', end='', steps='', all='repES0Maps', restrictoption=''),
        ReportedMap(name='TAvgMaps', output_var='TAvg', unit='degree C', end='', steps='', all='repTAvgMaps', restrictoption=''),
    ],
}
