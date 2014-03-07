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

from __future__ import unicode_literals, print_function
from sys import version_info
from codecs import open as codecs_open
from codecs import BOM_UTF8
from sys import getdefaultencoding

default_encoding = 'utf-8'

# Python 2/3 input compatibility.
python3 = version_info.major >= 3
if python3:
    iteritems = lambda d: d.iteritems()
else:
    iteritems = lambda d: iter(d.items())
    input = raw_input


class EncodingException(Exception):
    """Friendly exception for when an encoding-related error occurred."""

    def __init__(self, value, encoding, encoding_operation):
        self.value = to_unicode(value, errors='replace')
        self.encoding = to_unicode(encoding, errors='replace')
        self.encoding_operation = encoding_operation

    def __unicode__(self):
        if self.encoding_operation:
            return u'Could not encode "{}" from unicode to {}.'.format(
                   self.value, self.encoding)
        else:
            return u'Could not decode "{}" from {} to unicode.'.format(
                    self.value, self.encoding)

    def __str__(self):
        return from_unicode(self.__unicode__())


def to_unicode(obj, encoding=default_encoding, errors='strict'):
    """Safely decodes a string to unicode if it isn't already.
    Ensures that the output is a unicode object."""
    if not isinstance(obj, unicode):
        if isinstance(obj, basestring):
            try:
                obj = unicode(obj, encoding, errors=errors)
            except UnicodeDecodeError:
                raise EncodingException(obj, encoding, False)
        else:
            try:
                obj = unicode(obj)
            except UnicodeDecodeError:
                raise EncodingException(obj, None, False)
    return obj


def from_unicode(obj, encoding=default_encoding, errors='strict'):
    """Safely encodes a string from unicode if it isn't already."""
    if isinstance(obj, unicode):
        try:
            obj = obj.encode(encoding, errors=errors)
        except UnicodeEncodeError:
            raise EncodingException(obj, encoding, True)
    return obj


def prompt_settings(default_settings={}):
    """Prompt a user for settings values, based on a dictionary of default
    settings values."""
    settings = {}

    print('')
    print('Please enter values for the following project settings:')

    for key, value in iteritems(default_settings):
        key = to_unicode(key)
        value = to_unicode(value)
        prompt = from_unicode('- {} (default is "{}"): '.format(key, value))

        try:
            input_value = input(prompt)
        except:
            raise EncodingException('value for {}'.format(key),
                    getdefaultencoding())

        if not python3:
            input_value = to_unicode(input_value)

        input_value = input_value.strip()

        if input_value == '':
            input_value = value

        settings[key] = input_value

    print('')
    return settings


def skip_bom(fp):
    """Move a codecs encoded-file handle's streamreader to just past any
    utf-8 BOM that exists at the start of the file."""

    # Move the start of the file.
    fp.stream.seek(0)
    try:
        # Read the first character.
        first = fp.read(1)
    except:
        # If we could not read the file, then the character was not a BOM.
        first = None
    # If the first character wasn't a BOM, then move to the start of the file.
    if first != to_unicode(BOM_UTF8):
        fp.stream.seek(0)
    # If the first character was a BOM, then the stream reader is now
    # at the beginning of the file's content (directly after the BOM).


class EncodedFile(object):
    """File wrapper to raise friendly exceptions when an encoding error
    occurs."""

    def __init__(self, filepath, mode, encoding=default_encoding,
            errors='strict'):
        self.encoding = to_unicode(encoding.lower())
        self.errors = errors
        self.filepath = to_unicode(filepath)
        self.fp = codecs_open(filepath, mode, encoding=encoding)

        # If the mode allows reading, and encoding is utf8, then we need to
        # make sure the stream reader has moved past any BOM.
        if 'r' in self.fp.mode and self.encoding in ('utf-8', 'utf8'):
            skip_bom(self.fp)

    def write(self, value, value_encoding=default_encoding):
        value = to_unicode(value, encoding=value_encoding, errors=self.errors)
        try:
            self.fp.write(value)
        except UnicodeEncodeError:
            raise EncodingException(value, self.encoding, True)

    def writelines(self, lines, value_encoding=default_encoding):
        lines = [to_unicode(line, encoding=value_encoding, errors=self.errors)
                for line in lines]
        try:
            self.fp.writelines(lines)
        except UnicodeEncodeError:
            raise EncodingException(''.join(lines), self.encoding, True)

    def read(self, *args, **kwargs):
        """Note: Errors will always be treated as 'strict' when reading."""
        try:
            return self.fp.read(*args, **kwargs)
        except UnicodeDecodeError:
            raise EncodingException('Text in {}'.format(self.filepath),
                    self.encoding, False)

    def readline(self, *args, **kwargs):
        """Note: Errors will always be treated as 'strict' when reading."""
        try:
            return self.fp.readline(*args, **kwargs)
        except UnicodeDecodeError:
            raise EncodingException('Lines in {}'.format(self.filepath),
                    self.encoding, False)

    def readlines(self, *args, **kwargs):
        """Note: Errors will always be treated as 'strict' when reading."""
        try:
            return self.fp.readlines(*args, **kwargs)
        except UnicodeDecodeError:
            raise EncodingException('Lines in {}'.format(self.filepath),
                    self.encoding, False)

    def close(self):
        self.fp.close()

    def __getattr__(self, name):
        # Pass unknown calls to the file handle.
        return getattr(self.fp, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()
