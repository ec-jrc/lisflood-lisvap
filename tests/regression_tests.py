import os

from global_modules import LisSettings
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
        lisvapexe(settings)

    @classmethod
    def teardown_class(cls):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        for var in reference_files:
            output_nc = os.path.join(output_path, var) + '.nc'
            if os.path.exists(output_nc):
                os.remove(output_nc)

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
        lisvapexe(settings)

    @classmethod
    def teardown_class(cls):
        settings = LisSettings.instance()
        output_path = settings.binding['PathOut']
        for var in reference_files:
            output_nc = os.path.join(output_path, var) + '.nc'
            if os.path.exists(output_nc):
                os.remove(output_nc)

    @listest(domain, 'e0')
    def test_e0(self):
        pass

    @listest(domain, 'et')
    def test_et(self):
        pass
