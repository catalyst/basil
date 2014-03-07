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

from __future__ import print_function


def run_hook(hook_module, hook, settings):
    """Run a function in a given python module, passing a dictionary of
    project settings as an argument"""

    hook_func = hook_module.__dict__.get(hook)
    if hook_func == None:
        print("* {}() function not found in module: '{}'\n* Skipping {}-hook"
                .format(hook, hook_module.__name__, hook))
        return

    try:
        hook_func(settings.copy())
    except Exception as e:
        print("* {}".format(e))
        print("* {}-hook failed".format(hook))
