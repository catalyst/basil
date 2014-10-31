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

import re

def validator(validation_message):
    def validation_decorator(boolean_validator):
        def error_message_validator(field_name, value):
            return None if boolean_validator(value) else validation_message
        return error_message_validator
    return validation_decorator

@validator('invalid directory name.')
def validate_directory(value):
    """
    Returns True if value is a valid name for a directory.
    """
    return bool(re.search(r'^[A-z][A-z0-9_]+$', value))

@validator('invalid email address.')
def validate_email(value):
    """
    Returns True if value is a valid email address.
    Regex from: http://www.regular-expressions.info/email.html
    """
    return bool(re.search(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', value, re.IGNORECASE))

@validator('field cannot be left blank')
def validate_nonempty(value):
    """
    Returns True if value is not empty.
    """
    return bool(value)
