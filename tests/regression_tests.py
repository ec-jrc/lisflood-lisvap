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


class TestEFAS1arcminHourly(TestLis):
    domain = 'efas_1arcmin_hourly'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin_hourly.xml')

    def test_e0(self):
        return self.listest('e0')

    def test_es(self):
        return self.listest('es')

    def test_et(self):
        return self.listest('et')


class TestEFAS1arcmin6Hourly(TestLis):
    domain = 'efas_1arcmin_6hourly'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin_6hourly.xml')

    def test_e0_202112(self):
        return self.listest('e0', '_202112')

    def test_es_202112(self):
        return self.listest('es', '_202112')

    def test_et_202112(self):
        return self.listest('et', '_202112')

    def test_e0_202201(self):
        return self.listest('e0', '_202201')

    def test_es_202201(self):
        return self.listest('es', '_202201')

    def test_et_202201(self):
        return self.listest('et', '_202201')


class TestEFAS1arcminYearlyOutput(TestLis):
    domain = 'efas_1arcmin_yearly_output'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin_yearly_output.xml')

    def test_e0_2015(self):
        return self.listest('e0', '_2015')

    def test_es_2015(self):
        return self.listest('es', '_2015')

    def test_et_2015(self):
        return self.listest('et', '_2015')

    def test_e0_2016(self):
        return self.listest('e0', '_2016')

    def test_es_2016(self):
        return self.listest('es', '_2016')

    def test_et_2016(self):
        return self.listest('et', '_2016')


class TestEFAS1arcmin360DaysCalendar(TestLis):
    domain = 'efas_1arcmin_360days_calendar'
    settings_path = os.path.join(current_dir, 'data/tests_efas_1arcmin_360days_calendar.xml')

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
