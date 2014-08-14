# -*- coding: utf-8 -*-
"""
    tests
    ~~~~~~~~~~~~~~~~~~

    Contains all test Werkzeug tests.

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

import re
import sys
import unittest
import shutil
import tempfile
import atexit

from werkzeug.utils import find_modules
from werkzeug._compat import text_type, integer_types, reraise


def get_temporary_directory():
    directory = tempfile.mkdtemp()
    @atexit.register
    def remove_directory():
        try:
            shutil.rmtree(directory)
        except EnvironmentError:
            pass
    return directory


class WerkzeugTests(unittest.TestCase):
    """Baseclass for all the tests that Werkzeug uses.  Use these
    methods for testing instead of the camelcased ones in the
    baseclass for consistency.
    """

    def setup(self):
        pass

    def teardown(self):
        pass

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def assert_line_equal(self, x, y):
        assert x == y, "lines not equal\n a = %r\n b = %r" % (x, y)

    def assert_equal(self, x, y, msg=None):
        return self.assertEqual(x, y, msg)

    def assert_not_equal(self, x, y):
        return self.assertNotEqual(x, y)

    def assert_raises(self, exc_type, callable=None, *args, **kwargs):
        catcher = _ExceptionCatcher(self, exc_type)
        if callable is None:
            return catcher
        with catcher:
            callable(*args, **kwargs)

    if sys.version_info[:2] == (2, 6):
        def assertIsNone(self, x):
            assert x is None, "%r is not None" % (x,)

        def assertIsNotNone(self, x):
            assert x is not None, "%r is None" % (x, )

        def assertIn(self, x, y):
            assert x in y, "%r not in %r" % (x, y)

        def assertNotIn(self, x, y):
            assert x not in y, "%r in %r" % (x, y)

        def assertIsInstance(self, x, y):
            assert isinstance(x, y), "not isinstance(%r, %r)" % (x, y)

        def assertIs(self, x, y):
            assert x is y, "%r is not %r" % (x, y)

        def assertIsNot(self, x, y):
            assert x is not y, "%r is %r" % (x, y)

        def assertSequenceEqual(self, x, y):
            self.assertEqual(x, y)

        def assertRaisesRegex(self, exc_type, regex, *args, **kwargs):
            catcher = _ExceptionCatcher(self, exc_type)
            if not args:
                return catcher
            elif callable(args[0]):
                with catcher:
                    args[0](*args[1:], **kwargs)
                if args[0] is not None:
                    assert re.search(args[0], catcher.exc_value[0])
            else:
                raise NotImplementedError()

    elif sys.version_info[0] == 2:
        def assertRaisesRegex(self, *args, **kwargs):
            return self.assertRaisesRegexp(*args, **kwargs)

    def assert_is_none(self, x):
        self.assertIsNone(x)

    def assert_is_not_none(self, x):
        self.assertIsNotNone(x)

    def assert_in(self, x, y):
        self.assertIn(x, y)

    def assert_is_instance(self, x, y):
        self.assertIsInstance(x, y)

    def assert_not_in(self, x, y):
        self.assertNotIn(x, y)

    def assert_is(self, x, y):
        self.assertIs(x, y)

    def assert_is_not(self, x, y):
        self.assertIsNot(x, y)

    def assert_true(self, x):
        self.assertTrue(x)

    def assert_false(self, x):
        self.assertFalse(x)

    def assert_raises_regex(self, *args, **kwargs):
        return self.assertRaisesRegex(*args, **kwargs)

    def assert_sequence_equal(self, x, y):
        self.assertSequenceEqual(x, y)

    def assert_strict_equal(self, x, y):
        '''Stricter version of assert_equal that doesn't do implicit conversion
        between unicode and strings'''
        self.assert_equal(x, y)
        assert issubclass(type(x), type(y)) or issubclass(type(y), type(x)), \
                '%s != %s' % (type(x), type(y))
        if isinstance(x, (bytes, text_type, integer_types)) or x is None:
            return
        elif isinstance(x, dict) or isinstance(y, dict):
            x = sorted(x.items())
            y = sorted(y.items())
        elif isinstance(x, set) or isinstance(y, set):
            x = sorted(x)
            y = sorted(y)
        rx, ry = repr(x), repr(y)
        if rx != ry:
            rx = rx[:200] + (rx[200:] and '...')
            ry = ry[:200] + (ry[200:] and '...')
            raise AssertionError(rx, ry)
        assert repr(x) == repr(y), repr((x, y))[:200]


class _ExceptionCatcher(object):

    def __init__(self, test_case, exc_type):
        self.test_case = test_case
        self.exc_type = exc_type
        self.exc_value = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        exception_name = self.exc_type.__name__
        if exc_type is None:
            self.test_case.fail('Expected exception of type %r' %
                                exception_name)
        elif not issubclass(exc_type, self.exc_type):
            reraise(exc_type, exc_value, tb)
        self.exc_value = exc_value
        return True
