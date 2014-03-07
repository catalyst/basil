"""
Basil Django: Basil Template for standard Django projects.
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

packages = find_packages()
namespace_packages = packages[:]
for package in namespace_packages:
    if package.split('.')[-1] == 'tests':
        namespace_packages.remove(package)

setup(
      name='basil_django',
      version='0.1',
      author='Benjamin Denham',
      author_email='bend@catalyst.net.nz',
      packages=packages,
      namespace_packages=namespace_packages,
      url='',
      license='LICENSE.txt',
      description='Basil template to create a basic django project.',
      long_description=open('README.txt').read(),
      install_requires=['basil'],
      )
