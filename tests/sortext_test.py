# -*- coding: utf-8 -*-
##############################################################################

'''
Flight Data Utilities: Sort Extensions: Unit Tests
'''

##############################################################################
# Imports


import logging
import unittest

from operator import itemgetter

from flightdatautilities import sortext


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


class TestNsorted(unittest.TestCase):
    '''
    '''

    arguments = [
        [],
        [1, 2, 3],
        [1.0, 2.0, 3.0],
        ['1', '2', '3'],
        ['1.0', '2.0', '3.0'],
        [4, 1, 2, 3],
        [4.0, 1.0, 2.0, 3.0],
        ['4', '1', '2', '3'],
        ['4.0', '1.0', '2.0', '3.0'],
        ['Item #8', 'Item #9', 'Item #10', 'Item #11'],
        ['Item #1', 'Item #2', 'Item #3', 'Item #10'],
        ['Item #1', 'Item #10', 'Item #100', 'Item #1000'],
    ]

    expected = [
        [],
        [1, 2, 3],
        [1.0, 2.0, 3.0],
        ['1', '2', '3'],
        ['1.0', '2.0', '3.0'],
        [1, 2, 3, 4],
        [1.0, 2.0, 3.0, 4.0],
        ['1', '2', '3', '4'],
        ['1.0', '2.0', '3.0', '4.0'],
        ['Item #8', 'Item #9', 'Item #10', 'Item #11'],
        ['Item #1', 'Item #2', 'Item #3', 'Item #10'],
        ['Item #1', 'Item #10', 'Item #100', 'Item #1000'],
    ]

    def test_nsorted(self):
        '''
        '''
        for argument, expected in zip(self.arguments, self.expected):
            iterable = sortext.nsorted(argument)
            self.assertEqual(iterable, expected)

    def test_nsorted__key(self):
        '''
        '''
        argument = [('Screw', 'S100'), ('Bolt', 'B20'), ('Switch', 'S50')]
        expected = [('Bolt', 'B20'), ('Switch', 'S50'), ('Screw', 'S100')]
        iterable = sortext.nsorted(argument, key=itemgetter(1))
        self.assertEqual(iterable, expected)

    def test_nsorted__reverse(self):
        '''
        '''
        for argument, expected in zip(self.arguments, self.expected):
            iterable = sortext.nsorted(argument, reverse=True)
            expected.reverse()
            self.assertEqual(iterable, expected)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
