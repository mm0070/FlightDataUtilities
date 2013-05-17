# -*- coding: utf-8 -*-
##############################################################################

'''
Flight Data Utilities: Date Extensions: Unit Tests
'''

##############################################################################
# Imports


import logging
import unittest

from datetime import date, datetime

from flightdatautilities import dateext


##############################################################################
# Module Setup


def setUpModule():
    '''
    Prepare the environment for all tests in this module.
    '''
    # Disable all logging but most critical:
    logging.disable(logging.CRITICAL)


##############################################################################
# Test Cases


class TestRange(unittest.TestCase):
    '''
    '''

    expected = [
        [datetime(2000, 1, x) for x in range(1, 32, 1)],
        [datetime(2000, 1, x) for x in range(31, 0, -1)],
        [datetime(2000, 1, x) for x in range(1, 32, 2)],
        [datetime(2000, 1, x) for x in range(31, 0, -2)],
        [date(2000, 1, x) for x in range(1, 5, 1)],
    ]

    def test_range__step_float(self):
        '''
        '''
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), 1.5)
        self.assertRaises(TypeError, dateext.range, *args)

    def test_range__step_none(self):
        '''
        '''
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), None)
        self.assertRaises(TypeError, dateext.range, *args)

    def test_range__step_zero(self):
        '''
        '''
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), 0)
        self.assertRaises(ValueError, dateext.range, *args)

    def test_range__step_normal(self):
        '''
        '''
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1)
        self.assertEquals(dateext.range(*args), self.expected[0])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), -1)
        self.assertEquals(dateext.range(*args), self.expected[1])
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 2)
        self.assertEquals(dateext.range(*args), self.expected[2])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), -2)
        self.assertEquals(dateext.range(*args), self.expected[3])

    def test_range__step_reversed(self):
        '''
        '''
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), -1)
        self.assertEquals(dateext.range(*args), [])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), 1)
        self.assertEquals(dateext.range(*args), [])

    def test_range__valid_field(self):
        '''
        '''
        for field in ('seconds', 'minutes', 'hours', 'days', 'weeks'):
            try:
                args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1, field)
                dateext.range(*args)
            except:
                self.fail('Unexpected exception raised for field %s' % field)

    def test_range__invalid_field(self):
        '''
        '''
        for field in ('months', 'years', 'centuries', 'millenia'):
            args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1, field)
            self.assertRaises(ValueError, dateext.range, *args)

    def test_range__date_convert(self):
        '''
        '''
        args = (date(2000, 1, 1), date(2000, 1, 5), 12)
        kwargs = {'field': 'hours'}
        self.assertEquals(dateext.range(*args, **kwargs), self.expected[4])


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
