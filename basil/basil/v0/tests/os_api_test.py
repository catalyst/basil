# -*- coding: utf-8 -*-

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

# Run with: basil$ python -m v0.tests.os_api_test
import unittest
from .. import os_api
from .. import utils
#import sys
#from StringIO import StringIO


class TestOsApiModule(unittest.TestCase):

    def test_validate_virtualenv_name(self):
        self.assertEqual(os_api.validate_virtualenv_name('test_name'), True)
        self.assertEqual(os_api.validate_virtualenv_name('123'), True)
        self.assertEqual(os_api.validate_virtualenv_name(u'test_name'), True)
        self.assertEqual(os_api.validate_virtualenv_name(123), True)
        self.assertRaises(utils.DebugException,
                os_api.validate_virtualenv_name, u'I \u2665 unicode')
        self.assertRaises(utils.DebugException,
                os_api.validate_virtualenv_name, 'I ♥ unicode')
        self.assertRaises(Exception, os_api.validate_virtualenv_name, '')

    def test_quiet_call(self):
        """

        # This doesn't work, because redirecting stdout doesn't work for the
        # underlying subprocess.check_call()

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr
        try:
            args = ['bash', '-c', 'echo out && echo err >&2']
            # Test cases for different levels of "quietness".
            test_cases = [
                    (True, True),
                    (True, False),
                    (False, True),
                    (False, False)
                    ]

            for test_case in test_cases:
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                try:
                    self.assertEqual(os_api.quiet_call(args, test_case[0],
                            test_case[1]), 0)
                    out = sys.stdout.getvalue().strip()
                    err = sys.stderr.getvalue().strip()

                    self.assertEqual(('out' not in out), test_case[0])
                    self.assertEqual(('err' not in err), test_case[0])
                finally:
                    sys.stdout.close()
                    sys.stderr.close()
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
        """

        # Check a failed command will raise a DebugException.
        self.assertRaises(Exception, os_api.quiet_call,
                ['uncallable_command'])

    def test_get_output(self):
        self.assertEqual(os_api.get_output(['echo', 'out']), u'out\n')
        self.assertRaises(Exception, os_api.get_output,
                ['uncallable_command'])


class TestPipPackage(unittest.TestCase):

    def test_get_args(self):
        test_cases = [
                (('psycopg2', None, []), ['psycopg2']),
                (('psycopg2', '==1.0', []), ['psycopg2==1.0']),
                ((u'psycopg2', u'==1.0', []), ['psycopg2==1.0']),
                (('psycopg2', '>=1.0', ['--some-option', 'some-value']),
                        ['psycopg2>=1.0', '--some-option', 'some-value']),
                ]

        for test_case in test_cases:
            pkg = test_case[0]
            self.assertEqual(
                    os_api.PipPackage(pkg[0], pkg[1], pkg[2]).get_args(),
                    test_case[1])

if __name__ == '__main__':
    unittest.main()
