from collections import namedtuple

# TimeSeries = namedtuple('TimeSeries', 'name, output_var, where, repoption, restrictoption, operation')
ReportedMap = namedtuple('ReportedMap', 'name, output_var, unit, all, restrictoption, standard_name, scale_factor, add_offset, value_min, value_max')

defaults = {
    'usetavg': False, 'usetdewmaps': False, 'userelhumiditymaps': False, 'usewinduvmaps': False,
    'temperatureinkelvinflag': False,
    'repet0maps': True, 'repes0maps': True, 'repe0maps': True, 'reptavgmaps': True,
    'efas': True, 'cordex': False, 'glofas': False, 'output6hourly': False, 'splitinput': False,
    'splitoutput': False, 'monthlyOutput': False,
    'reportedmaps': [
        ReportedMap(name='ET0Maps', output_var='ETRef', unit='mm/day', all='repET0Maps', restrictoption='', standard_name='water_evapotranspiration_flux', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='E0Maps', output_var='EWRef', unit='mm/day', all='repE0Maps', restrictoption='', standard_name='water_potential_evaporation_flux', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='ES0Maps', output_var='ESRef', unit='mm/day', all='repES0Maps', restrictoption='', standard_name='water_evaporation_flux_from_soil', scale_factor=0.01, add_offset=0.0, value_min=0, value_max=50),
        ReportedMap(name='TAvgMaps', output_var='TAvg', unit='degree C', all='repTAvgMaps', restrictoption='', standard_name='air_temperature', scale_factor=0.1, add_offset=0.0, value_min=-60, value_max=60),
    ],
}
