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

# Run with: basil$ python -m v0.tests.actions_test
import unittest
from .. import actions
import argparse


class TestActionCollectionConfig(unittest.TestCase):

    def setUp(self):
        self.acc = actions.ActionCollectionConfig()

    def test_add_action(self):
        def test_func():
            pass

        action = self.acc.add_action('testing', test_func)
        self.assertIsInstance(action, argparse.ArgumentParser)
        self.assertEqual(action._defaults['func'], test_func)

if __name__ == '__main__':
    unittest.main()
