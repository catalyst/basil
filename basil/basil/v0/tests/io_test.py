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

# Run with: ~/basil/basil$ python -m v0.tests.io_test
import unittest
from os import remove
from .. import io
import codecs


utf8_string = 'I \xe2\x99\xa5 unicode'
unicode_string = u'I \u2665 unicode'
cp1252_string = '\x80'
bom = '\xef\xbb\xbf'
bom_utf8_string = bom + utf8_string
utf8_unknown = '\xef\xbf\xbd'
unicode_unknown = u'\ufffd'
filename = '__io_test_file__.txt'


class TestIoModule(unittest.TestCase):

    def test_to_unicode(self):
        # Test basic decoding of utf8.
        self.assertEqual(unicode_string, io.to_unicode(utf8_string))

        # Test exception when utf8 is decoded as ascii.
        self.assertRaises(io.EncodingException, io.to_unicode,
                utf8_string, encoding='ascii')

        # Test exception when non-utf8 char is decoded as utf8.
        self.assertRaises(io.EncodingException, io.to_unicode, cp1252_string)
        # Test replacement of bad character.
        self.assertEqual(unicode_unknown,
                io.to_unicode(cp1252_string, errors='replace'))
        # Test ignoring bad character.
        self.assertEqual('',
                io.to_unicode(cp1252_string, errors='ignore'))

    def test_encoding_exception(self):
        bad_e = io.EncodingException(cp1252_string, 'utf-8', True)

        # Test the exception handles unknown characters for both unicode and
        # ascii.
        self.assertIn(unicode_unknown, unicode(bad_e))
        self.assertIn(utf8_unknown, str(bad_e))

    def test_from_unicode(self):
        # Test basic utf8 encoding.
        self.assertEqual(utf8_string,
                io.from_unicode(unicode_string))

        # Test exception when encoding utf8 as ascii.
        self.assertRaises(io.EncodingException,
                io.from_unicode, unicode_string, encoding='ascii')
        # Test replacement of bad character.
        self.assertEqual('I ? unicode',
                io.from_unicode(unicode_string, encoding='ascii',
                        errors='replace'))
        # Test ignoring bad character.
        self.assertEqual('I  unicode',
                io.from_unicode(unicode_string, encoding='ascii',
                        errors='ignore'))

    def test_skip_bom(self):
        # File containing BOM only.
        with open(filename, 'wb') as fp:
            fp.write(bom)
        with codecs.open(filename, 'r', encoding='utf-8') as fp:
            io.skip_bom(fp)
            self.assertEqual(u'', fp.read())

        # File containing BOM and string.
        with open(filename, 'wb') as fp:
            fp.write(bom_utf8_string)
        with codecs.open(filename, 'r', encoding='utf-8') as fp:
            io.skip_bom(fp)
            self.assertEqual(unicode_string, fp.read())

        # File containing string with no BOM.
        with open(filename, 'wb') as fp:
            fp.write(utf8_string)
        with codecs.open(filename, 'r', encoding='utf-8') as fp:
            io.skip_bom(fp)
            self.assertEqual(unicode_string, fp.read())

        # Empty file.
        with open(filename, 'wb') as fp:
            fp.write('')
        with codecs.open(filename, 'r', encoding='utf-8') as fp:
            io.skip_bom(fp)
            self.assertEqual(u'', fp.read())

    def tearDown(self):
        try:
            remove(filename)
        except OSError:
            pass


class TestIoEncodedFile(unittest.TestCase):

    def test_write(self):
        with io.EncodedFile(filename, 'w') as fp:
            # Test exception when a non-utf8 character it to be written as
            # utf8.
            self.assertRaises(io.EncodingException, fp.write, cp1252_string)
            # Test exception when a utf8 character to be written to a file is
            # specified as being encoded as ascii
            self.assertRaises(io.EncodingException, fp.write, utf8_string,
                    value_encoding='ascii')

            # Write both a utf8-encoded byte string and a unicode string.
            fp.write(utf8_string)
            fp.write(unicode_string)

        with open(filename, 'rb') as fp:
            # Check file contents.
            self.assertEqual(utf8_string * 2, fp.read())

        # Test bad-character replacement.
        with io.EncodedFile(filename, 'w', errors='replace') as fp:
            fp.write(cp1252_string)
        with open(filename, 'rb') as fp:
            self.assertEqual(utf8_unknown, fp.read())

        # Test ignoring bad-characters.
        with io.EncodedFile(filename, 'w', errors='ignore') as fp:
            fp.write(cp1252_string)
        with open(filename, 'rb') as fp:
            self.assertEqual('', fp.read())

    def test_writelines(self):
        with io.EncodedFile(filename, 'w') as fp:
            # Test exception when a non-utf8 character it to be written as
            # utf8.
            self.assertRaises(io.EncodingException, fp.writelines,
                    [utf8_string, cp1252_string])
            # Test exception when a utf8 character to be written to a file is
            # specified as being encoded as ascii
            self.assertRaises(io.EncodingException, fp.writelines,
                    ['ok ascii', utf8_string], value_encoding='ascii')

            # Write both a utf8-encoded byte string and a unicode string.
            fp.writelines([utf8_string, unicode_string])

        with open(filename, 'rb') as fp:
            # Check file contents.
            self.assertEqual(utf8_string * 2, fp.read())

        # Test bad-character replacement.
        with io.EncodedFile(filename, 'w', errors='replace') as fp:
            fp.writelines([utf8_string, cp1252_string])
        with open(filename, 'rb') as fp:
            self.assertEqual(utf8_string + utf8_unknown, fp.read())

        # Test ignoring bad-characters.
        with io.EncodedFile(filename, 'w', errors='ignore') as fp:
            fp.writelines([utf8_string, cp1252_string])
        with open(filename, 'rb') as fp:
            self.assertEqual(utf8_string, fp.read())

    def test_read(self):
        # Test writing utf8-encoded text, and reading unicode.
        with open(filename, 'wb') as fp:
            fp.write(utf8_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertEqual(unicode_string, fp.read())

        # Test exception when reading utf8 as ascii.
        with io.EncodedFile(filename, 'r', encoding='ascii') as fp:
            self.assertRaises(io.EncodingException, fp.read)

        # Test exception when reading non-utf8 character as utf8.
        with open(filename, 'wb') as fp:
            fp.write(cp1252_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertRaises(io.EncodingException, fp.read)

        # Test ignoring BOM.
        with open(filename, 'wb') as fp:
            fp.write(bom_utf8_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertEqual(unicode_string, fp.read())

    def test_readlines(self):
        # Test writing utf8-encoded text, and reading unicode.
        with open(filename, 'wb') as fp:
            fp.write(utf8_string + '\n' + utf8_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertEqual([unicode_string + '\n', unicode_string],
                    fp.readlines())

        # Test exception when reading utf8 as ascii.
        with io.EncodedFile(filename, 'r', encoding='ascii') as fp:
            self.assertRaises(io.EncodingException, fp.readlines)

        # Test exception when reading non-utf8 character as utf8.
        with open(filename, 'wb') as fp:
            fp.write(cp1252_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertRaises(io.EncodingException, fp.readlines)

        # Test ignoring BOM.
        with open(filename, 'wb') as fp:
            fp.write(bom_utf8_string)
        with io.EncodedFile(filename, 'r') as fp:
            self.assertEqual([unicode_string], fp.readlines())

    def tearDown(self):
        try:
            remove(filename)
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main()
