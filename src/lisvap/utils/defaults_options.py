from collections import namedtuple

TimeSeries = namedtuple('TimeSeries', 'name, output_var, where, repoption, restrictoption, operation')
ReportedMap = namedtuple('ReportedMap', 'name, output_var, unit, end, steps, all, restrictoption, standard_name, scale_factor, add_offset, value_min, value_max')

defaults = {
    'usetavg': False,
    'readnetcdfstack': False, 'writenetcdfstack': False, 'writenetcdf': False,
    'repavtimeseries': False,
    'repet0maps': False, 'repes0maps': False, 'repe0maps': True, 'reptavgmaps': False,
    'efas': True, 'cordex': False, 'glofas': False, 'output6hourly': False, 'splitinput': False, 'splitoutput': False,
    'timeseries': [
        TimeSeries(name='TAvgTS', output_var='TAvg', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='ET0TS', output_var='ETRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='E0TS', output_var='EWRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
        TimeSeries(name='ES0TS', output_var='ESRef', where='1', repoption='repAvTimeseries', restrictoption='', operation=''),
    ],
    'reportedmaps': [
        ReportedMap(name='ET0Maps', output_var='ETRef', unit='mm/day', end='', steps='', all='repET0Maps', restrictoption='', standard_name='water_evapotranspiration_flux', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='E0Maps', output_var='EWRef', unit='mm/day', end='', steps='', all='repE0Maps', restrictoption='', standard_name='water_potential_evaporation_flux', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='ES0Maps', output_var='ESRef', unit='mm/day', end='', steps='', all='repES0Maps', restrictoption='', standard_name='water_evaporation_flux_from_soil', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='TAvgMaps', output_var='TAvg', unit='degree C', end='', steps='', all='repTAvgMaps', restrictoption='', standard_name='air_temperature', scale_factor=0.1, add_offset=0.0, value_min=-60, value_max=60),
    ],
}
