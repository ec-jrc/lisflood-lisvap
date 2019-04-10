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

import os

from utils import LisSettings, cdf_flags
from lisvap1 import lisvapexe

from tests import listest, reference_files

current_dir = os.path.dirname(__file__)


class TestEFAS(object):
    domain = 'efas'
    settings_path = os.path.join(current_dir, 'data/tests_efas.xml')
    optionxml = os.path.join(current_dir, 'data/OptionTserieMapsLisvap_efas.xml')

    @classmethod
    def setup_class(cls):
        settings = LisSettings(cls.settings_path, cls.optionxml)
        # settings.flags['printtime'] = True
        lisvapexe(settings)

    @classmethod
    def teardown_class(cls):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        for var in reference_files:
            output_nc = os.path.join(output_path, var) + '.nc'
            if os.path.exists(output_nc):
                os.remove(output_nc)
        cdf_flags['all'] = 0
        cdf_flags['steps'] = 0
        cdf_flags['end'] = 0

    @listest(domain, 'e0')
    def test_e0(self):
        pass

    @listest(domain, 'es')
    def test_es(self):
        pass

    @listest(domain, 'et')
    def test_et(self):
        pass


class TestCORDEX(object):
    domain = 'cordex'
    settings_path = os.path.join(current_dir, 'data/tests_cordex.xml')
    optionxml = os.path.join(current_dir, 'data/OptionTserieMapsLisvap_cordex.xml')

    @classmethod
    def setup_class(cls):
        settings = LisSettings(cls.settings_path, cls.optionxml)
        # settings.flags['printtime'] = True
        lisvapexe(settings)

    @classmethod
    def teardown_class(cls):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        for var in reference_files:
            output_nc = os.path.join(output_path, var) + '.nc'
            if os.path.exists(output_nc):
                os.remove(output_nc)
        cdf_flags['all'] = 0
        cdf_flags['steps'] = 0
        cdf_flags['end'] = 0

    @listest(domain, 'e0')
    def test_e0(self):
        pass

    @listest(domain, 'et')
    def test_et(self):
        pass
