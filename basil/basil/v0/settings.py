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

from os import getenv
from os.path import join, isfile
from io import to_unicode, EncodedFile
import json

basil_settings_path = join(getenv('HOME'), '.basil-settings')


def read_basil_settings():
    settings = {}

    if isfile(basil_settings_path):
        with EncodedFile(basil_settings_path, 'r') as fp:
            try:
                settings = json.load(fp)
            except:
                pass

    if type(settings) != dict:
        settings = {}

    return settings


def get_basil_setting(key, default=None):
    key = to_unicode(key)

    settings = read_basil_settings()

    return settings.get(key, default)


def set_basil_setting(key, value):
    key = to_unicode(key)

    settings = read_basil_settings()
    settings[key] = value

    with EncodedFile(basil_settings_path, 'w') as fp:
        json.dump(settings, fp, ensure_ascii=False)


def unset_basil_setting(key):
    key = to_unicode(key)

    settings = read_basil_settings()
    settings.pop(key, None)

    with EncodedFile(basil_settings_path, 'w') as fp:
        json.dump(settings, fp, ensure_ascii=False)
