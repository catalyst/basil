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

import argparse
from io import to_unicode
from utils import DebugException


class ActionCollectionConfig(object):
    """Configuration management class to manage a collection of available
    actions."""

    def __init__(self):
        # Create parser.
        self.parser = argparse.ArgumentParser(
                description='Build a system instant-like.')
        self.parser.add_argument('-v', '--verbose', action='store_true',
                help='show verbose debug output')
        self.subparsers = self.parser.add_subparsers()

    def add_action(self, name, func, **kwargs):
        """Add an action to this configuration.
        func will be called with a namespace containing the names of
        arguments added to this action. Option dashes will be omitted from the
        names. E.g. '--foo' will be named 'foo'"""
        # Add a subparser for this action.
        action = self.subparsers.add_parser(name, **kwargs)
        # Set the function to be called for this action.
        action.set_defaults(func=func)
        return action

    def execute(self):
        """Parses command line arguments with the configured actions, and
        executes the specified action."""
        args = self.parser.parse_args()
        ex = None
        try:
            args.func(args)
        except DebugException as e:
            e.debug = args.verbose
            ex = e
        except Exception as e:
            ex = e

        if ex != None:
            print('* {}'.format(to_unicode(ex)))
