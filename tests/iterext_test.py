# -*- coding: utf-8 -*-
##############################################################################

'''
Flight Data Utilities: Iter Extensions: Unit Tests
'''

##############################################################################
# Imports


import logging
import unittest

from flightdatautilities import iterext


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


class TestNestedGroupby(unittest.TestCase):
    '''
    '''

    @unittest.skip('Not implemented.')
    def test_nested_groupby(self):
        '''
        '''
        pass


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
