#!/usr/bin/python3
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

import subprocess

def action_up(project_dir):
    """
    Runs Vagrant up inside project_dir.

    @Later - can parse output to identify port used by vagrant for web interface
    """
    output = subprocess.check_output(['vagrant', 'up'], cwd=project_dir)

def action_down(project_dir):
    """
    Runs Vagrant halt inside project_dir.
    """
    pass

def action_open(project_dir):
    """
    Opens web interface to project on appropriate port.
    """
    pass

def action_destroy(project_dir):
    """
    Calls Vagrant destroy inside project_dir, and deletes project_dir.
    """
    pass
