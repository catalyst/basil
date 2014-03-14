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

from sys import version_info, exc_info
from traceback import format_exception
from io import to_unicode
from os.path import abspath, basename, splitext
from textwrap import wrap

python3 = version_info.major >= 3
if python3:
    iteritems = lambda d: iter(d.items())
else:
    iteritems = lambda d: d.iteritems()


class BasilVersionException(Exception):
    """Exception to throw when a basil version-related issue occurred.
    E.g. A template/db_api could not be found for a given version, or a
    project is incompatible with the current version of basil."""
    pass


class DebugException(Exception):
    """Exception that contains a user-friendly message, along with a more
    detailed exception for debugging purposes."""

    def __init__(self, message, original_exception):
        self.message = message
        self.original_exception = original_exception
        self.debug = False

    def __unicode__(self):
        message = to_unicode(self.message)
        if self.debug:
            message += '\n\n' + ''.join(format_exception(
                    type(self.original_exception),
                    to_unicode(self.original_exception), exc_info()[2]))
        return message

    def __str__(self):
        return str(unicode(self))


def get_basil_major_version(version_number):
    """Get the basil major version from a full version number of basil or
    a template/db_api module."""
    return unicode(version_number).split('.')[0]


def get_module_major_version(version_number):
    """Get the major version from a full version number of a template/db_api
    module."""
    numbers = unicode(version_number).split('.')
    if len(numbers) < 2:
        raise Exception('Could not determine module major version from '
                'version number: {} (No second number)'.format(version_number))
    else:
        return numbers[1]


def get_latest_version_number(package_name):
    """Get the latest version number that exists for a package in this version
    of Basil."""
    from pkgutil import iter_modules
    from importlib import import_module

    try:
        package = import_module('.' + package_name, __package__)
    except:
        raise BasilVersionException('{} package was not found.'.format(
                __package__ + '.' + package_name))

    latest_version_number = -1

    for _, modname, _ in iter_modules(package.__path__):
        try:
            version_number = int(modname.strip('v'))
        except:
            continue
        if version_number > latest_version_number:
            latest_version_number = version_number

    if latest_version_number >= 0:
        return latest_version_number
    else:
        raise BasilVersionException('No valid versions of {} were found.'
                .format(__package__ + '.' + package_name))


def get_module(package_name, major_version_number=None):
    """Get the path to a module relative to this version of basil.
    E.g. For 'package_name=templates.django', return '.templates.django.v1'
    (where v1 is the latest version of django for this version of basil.)"""
    from importlib import import_module

    if major_version_number == None:
        major_version_number = get_latest_version_number(package_name)

    # This should be similar to: '.(templates|db_apis).package_name.v[0-9]+'
    module_path = '.{}.v{}'.format(package_name, major_version_number)

    try:
        return import_module(module_path, __package__)
    except ImportError:
        raise BasilVersionException("Module: '{}' could not be found. Perhaps "
                "it, or a module it depends on, is not installed."
                .format(__package__ + module_path))


def load_module_from_file(module_path):
    """Load a python module from a given path."""
    module_path = abspath(module_path)
    module_name = splitext(basename(module_path))[0]

    if python3:
        import importlib.machinery  # @UnresolvedImport (exists in python3)
        loader = importlib.machinery.SourceFileLoader(module_name, module_path)
        return loader.load_module(module_name)
    else:
        from imp import load_source
        return load_source(module_name, module_path)

def format_instructions(instructions_dict):
    """Formats a given set of instructions for terminal display.
    instructions should be a dictionary of lists of instructions keyed by
    section titles."""
    
    output = ''
    
    for title, instructions in iteritems(instructions_dict):
        if not instructions:
            continue
        
        instruction_lines = ['']
        for instruction in instructions:
            instruction_lines += wrap(u'- ' + to_unicode(instruction),
                    replace_whitespace=False)
            # Add blank line between insructions.
            instruction_lines.append('')
        
        output += """
---------------------------------------------------------------------
 {title}
---------------------------------------------------------------------
{instructions}""".format(
        title=to_unicode(title),
        instructions = '\n'.join(instruction_lines))

    return output
