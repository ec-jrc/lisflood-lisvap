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

from tests import TestLis

current_dir = os.path.dirname(__file__)


class TestEFAS(TestLis):
    domain = 'efas'
    settings_path = os.path.join(current_dir, 'data/tests_efas.xml')

    def test_e0(self):
        return self.listest('e0')

    def test_es(self):
        return self.listest('es')

    def test_et(self):
        return self.listest('et')


class TestEFAS1arcmin(TestLis):
    domain = 'efas_1arcmin'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin.xml')

    def test_e0(self):
        return self.listest('e0')

    def test_es(self):
        return self.listest('es')

    def test_et(self):
        return self.listest('et')


class TestEFAS1arcminYearly(TestLis):
    domain = 'efas_1arcmin_yearly'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin_yearly.xml')

    def test_e0(self):
        return self.listest('e0')

    def test_es(self):
        return self.listest('es')

    def test_et(self):
        return self.listest('et')


class TestCORDEX(TestLis):
    domain = 'cordex'
    settings_path = os.path.join(current_dir, 'data/tests_cordex.xml')

    def test_e0(self):
        return self.listest('e0')

    def test_et(self):
        return self.listest('et')


class TestGLOFAS(TestLis):
    domain = 'glofas'
    settings_path = os.path.join(current_dir, 'data/tests_glofas.xml')

    def test_e0(self):
        return self.listest('e0')
