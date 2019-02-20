import os

from global_modules.globals import binding
from lisvap1 import lisvapexe
from global_modules.zusatz import option_binding


current_dir = os.path.dirname(__file__)
settings_path = os.path.join(current_dir, 'data/tests_settings.xml')
optionxml = os.path.join(current_dir, 'data/OptionTserieMapsLisvap.xml')
reference_nc_filenames = ['data/e0_1_15', 'data/es_1_15', 'data/et_1_15']
reference_nc_paths = {nc[5:7]: os.path.join(current_dir, nc) for nc in reference_nc_filenames}
atol = 0.01


def setup_module():
    # remove old output files
    option_binding(settings_path, optionxml)
    output_path = binding['PathOut']
    for var in reference_nc_paths:
        output_nc = os.path.join(output_path, var) + '.nc'
        os.remove(output_nc)
    # execute current version of lisvap
    lisvapexe(settings_path, optionxml)


def teardown_module():
    pass
