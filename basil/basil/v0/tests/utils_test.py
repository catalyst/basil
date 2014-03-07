"""
Basil: Build A System Instant-Like
Copyright (C) 2014 Catalyst IT Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Run with: basil$ python -m v0.tests.utils_test
import unittest
from .. import utils
from types import ModuleType

invalid_package_name = 'templates.no_one_would_make_this_basil_template1234'
test_package_name = 'templates.django'
test_module_major_version = 0
# Relative to basil module path.
valid_module_path = 'v0/io.py'
invalid_module_path = 'no_module_ever.py'


class TestUtilsModule(unittest.TestCase):

    def test_debug_exception(self):
        e = Exception('base_exception')
        de = utils.DebugException('friendly_exception', e)
        string_de = str(de)

        self.assertIn('friendly_exception', string_de)
        self.assertNotIn('base_exception', string_de)

        de.debug = True
        string_de = str(de)

        self.assertIn('friendly_exception', string_de)
        self.assertIn('base_exception', string_de)

    def test_get_basil_major_version(self):
        self.assertEqual(utils.get_basil_major_version('1.2.3'), '1')
        self.assertEqual(utils.get_basil_major_version('2.1'), '2')
        self.assertEqual(utils.get_basil_major_version('3'), '3')
        self.assertEqual(utils.get_basil_major_version('3345.43'), '3345')
        self.assertEqual(utils.get_basil_major_version(3), '3')
        self.assertEqual(utils.get_basil_major_version(4.3), '4')
        self.assertEqual(utils.get_basil_major_version(455.233), '455')

    def test_get_module_major_version(self):
        self.assertEqual(utils.get_module_major_version('1.2.3'), '2')
        self.assertEqual(utils.get_module_major_version('2.1'), '1')
        self.assertRaises(Exception, utils.get_module_major_version, '3')
        self.assertEqual(utils.get_module_major_version('3345.43'), '43')
        self.assertRaises(Exception, utils.get_module_major_version, 3)
        self.assertEqual(utils.get_module_major_version(4.3), '3')
        self.assertEqual(utils.get_module_major_version(455.233), '233')

    def test_get_latest_version_number(self):
        self.assertIsInstance(utils.get_latest_version_number(
                test_package_name), int)
        self.assertRaises(utils.BasilVersionException,
                utils.get_latest_version_number, invalid_package_name)
        self.assertRaises(utils.BasilVersionException,
                utils.get_latest_version_number, 'tests')

    def test_get_module(self):
        self.assertIsInstance(utils.get_module(test_package_name), ModuleType)
        self.assertIsInstance(utils.get_module(test_package_name,
                test_module_major_version), ModuleType)
        self.assertIsInstance(utils.get_module(test_package_name,
                str(test_module_major_version)), ModuleType)
        self.assertRaises(utils.BasilVersionException, utils.get_module,
                invalid_package_name)
        self.assertRaises(utils.BasilVersionException, utils.get_module,
                invalid_package_name, test_module_major_version)
        self.assertRaises(utils.BasilVersionException, utils.get_module,
                invalid_package_name, str(test_module_major_version))

    def test_load_module_from_file(self):
        self.assertRaises(Exception, utils.load_module_from_file,
                invalid_module_path)
        self.assertIsInstance(utils.load_module_from_file(valid_module_path),
                ModuleType)

if __name__ == '__main__':
    unittest.main()
