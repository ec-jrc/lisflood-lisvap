import os

from lisvap1 import Lisvapexe

current_dir = os.path.dirname(__file__)
settings_path = os.path.join(current_dir, 'data/tests_settings.xml')
optionxml = os.path.join(current_dir, 'data/OptionTserieMapsLisvap.xml')
reference_nc_filenames = ['data/e0_1_9.nc', 'data/es_1_9.nc', 'data/et_1_9.nc']
reference_nc_paths = {nc[5:7]: os.path.join(current_dir, nc) for nc in reference_nc_filenames}
atol = 0.01


def setup_module():
    Lisvapexe(settings_path, optionxml)


def teardown_module():
    pass
