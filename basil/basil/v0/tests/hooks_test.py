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

# Run with: basil$ python -m v0.tests.hooks_test
from __future__ import print_function
import unittest
from .. import hooks
import sys
from StringIO import StringIO


def bad_hook(settings):
    raise Exception('bad_hook{}'.format(settings['a']))


def good_hook(settings):
    print('good_hook{}'.format(settings['a']))


class TestHooksModule(unittest.TestCase):

    def test_run_hook(self):
        saved_stdout = sys.stdout
        try:
            settings = {'a': 1}

            test_cases = [
                    (sys.modules[self.__module__], 'good_hook',
                            ('good_hook{}'.format(settings['a']))),
                    (sys.modules[self.__module__], 'bad_hook',
                            ('* bad_hook{}'.format(settings['a']),
                            '* bad_hook-hook failed'.format(settings['a']))),
                    (sys.modules[self.__module__], 'unknown_hook',
                            ('* unknown_hook() function not found in module'))
                    ]

            for test_case in test_cases:
                sys.stdout = StringIO()
                try:
                    hooks.run_hook(hook_module=test_case[0], hook=test_case[1],
                            settings=settings)
                    output = sys.stdout.getvalue().strip()

                    for asserted_output in test_case[2]:
                        self.assertIn(asserted_output, output)
                finally:
                    sys.stdout.close()

        finally:
            sys.stdout = saved_stdout

if __name__ == '__main__':
    unittest.main()
