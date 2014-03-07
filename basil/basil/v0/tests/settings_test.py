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

# Run with: basil$ python -m v0.tests.settings_test
import unittest
from .. import settings
from os import remove
from sys import version_info
import codecs
import json

python3 = version_info.major >= 3
if python3:
    iteritems = lambda d: d.iteritems()
else:
    iteritems = lambda d: iter(d.items())

settings.basil_settings_path = '__test_basil_settings_file__.txt'
test_settings = {
                'a': 1,
                'b': u'test',
                3.5: u'testing',
                4: 4.3
        }


class TestUtilsModule(unittest.TestCase):

    def test_read_basil_settings(self):
        test_cases = [
                ({'a': 1, 'b': u'test', 3.5: u'testing', 4: 4.3},
                    {u'a': 1, u'b': 'test', u'3.5': u'testing', u'4': 4.3}),
                ({}, {}),
                ('asdf', {}),
                ([1, 2, 3], {}),
                (1.5, {}),
                ({'a': [1, 2, 'a', (3, 4)]}, {u'a': [1, 2, u'a', [3, 4]]})
                ]

        for test_case in test_cases:
            with codecs.open(
                    settings.basil_settings_path, 'w', encoding='utf-8') as fp:
                json.dump(test_case[0], fp)

            self.assertEqual(settings.read_basil_settings(), test_case[1])

    def test_get_basil_setting(self):
        with codecs.open(
                settings.basil_settings_path, 'w', encoding='utf-8') as fp:
            json.dump(test_settings, fp)

        for key, value in iteritems(test_settings):
            self.assertEqual(settings.get_basil_setting(key), value)

    def test_set_basil_setting(self):
        for key, value in iteritems(test_settings):
            settings.set_basil_setting(key, value)

        with codecs.open(
                settings.basil_settings_path, 'r', encoding='utf-8') as fp:
            loaded_settings = fp.read()

        self.assertEqual(loaded_settings, json.dumps(test_settings))

    def test_unset_basil_setting(self):
        with codecs.open(
                settings.basil_settings_path, 'w', encoding='utf-8') as fp:
            json.dump(test_settings, fp)

        unset_key = test_settings.keys()[0]
        altered_settings = test_settings.copy()
        del altered_settings[unset_key]

        settings.unset_basil_setting(unset_key)
        settings.unset_basil_setting('key_does_not_exist')

        with codecs.open(
                settings.basil_settings_path, 'r', encoding='utf-8') as fp:
            loaded_settings = fp.read()

        self.assertEqual(loaded_settings, json.dumps(altered_settings))

    def tearDown(self):
        try:
            remove(settings.basil_settings_path)
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main()
