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

from setuptools import setup, find_packages
from pkgutil import iter_modules
from importlib import import_module


def get_console_script_line(basil_version, script_name=None):
    """Generate the console script line for a given basil version.
    Can also take a custom name for the console script."""
    if script_name == None:
        script_name = 'basil{}'.format(basil_version)
    return '{} = basil.v{}.main:main'.format(script_name, basil_version)

console_scripts = []
basil_package = import_module('basil')
latest_version = -1

for _, modname, _ in iter_modules(basil_package.__path__):
    version_number = int(modname.strip('v'))
    console_scripts.append(get_console_script_line(version_number))
    if version_number > latest_version:
        latest_version = version_number

console_scripts.append(get_console_script_line(latest_version, 'basil'))

packages = find_packages()
namespace_packages = packages[:]
for package in namespace_packages:
    if package.split('.')[-1] == 'tests':
        namespace_packages.remove(package)

setup(
      name='basil',
      version='0.1',
      author='Benjamin Denham',
      author_email='bend@catalyst.net.nz',
      packages=packages,
      namespace_packages=namespace_packages,
      url='http://pypi.python.org/pypi/basil',
      license='LICENSE.txt',
      description='Build a system instant-like.',
      long_description=open('README.txt').read(),
      install_requires=[
              'virtualenvwrapper',
              ],
      entry_points={'console_scripts': console_scripts}
      )
