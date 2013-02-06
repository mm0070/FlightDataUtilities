# -*- coding: utf-8 -*-
##############################################################################

'''
'''

##############################################################################
# Imports


import unittest

from decimal import Decimal

from flightdatautilities import units


##############################################################################
# Test Cases


class TestConversion(unittest.TestCase):

    @unittest.skip('Test not implemented.')
    def test__normalise(self):

        pass

    @unittest.skip('Test not implemented.')
    def test__function(self):

        pass

    @unittest.skip('Test not implemented.')
    def test__multiplier(self):

        pass

    def test__convert(self):

        data = {
            # Frequency:
            (1, 'KHz', 'MHz'): 0.001,
            (1, 'KHz', 'GHz'): 0.000001,
            (1, 'MHz', 'KHz'): 1000.0,
            (1, 'MHz', 'GHz'): 0.001,
            (1, 'GHz', 'KHz'): 1000000.0,
            (1, 'GHz', 'MHz'): 1000.0,
            # Flow (Volume):
            (1, 'lb/h', 'kg/h'): 0.453592,
            (1, 'lb/h', 't/h'): 0.000453592,
            (1, 'kg/h', 'lb/h'): 2.20462,
            (1, 'kg/h', 't/h'): 0.001,
            (1, 't/h', 'lb/h'): 2204.62,
            (1, 't/h', 'kg/h'): 1000,
            # Length:
            (1, 'ft', 'm'): 0.3048,
            (1, 'ft', 'km'): 0.0003048,
            (1, 'ft', 'mi'): 0.000189394,
            (1, 'ft', 'nm'): 0.000164579,
            (1, 'm', 'ft'): 3.28084,
            (1, 'm', 'km'): 0.001,
            (1, 'm', 'mi'): 0.000621371,
            (1, 'm', 'nm'): 0.000539957,
            (1, 'km', 'ft'): 3280.84,
            (1, 'km', 'm'): 1000,
            (1, 'km', 'mi'): 0.621371,
            (1, 'km', 'nm'): 0.539957,
            (1, 'mi', 'ft'): 5280,
            (1, 'mi', 'm'): 1609.34,
            (1, 'mi', 'km'): 1.60934,
            (1, 'mi', 'nm'): 0.868976,
            (1, 'nm', 'ft'): 6076.12,
            (1, 'nm', 'm'): 1852,
            (1, 'nm', 'km'): 1.852,
            (1, 'nm', 'mi'): 1.15078,
            # Mass:
            (1, 'lb', 'kg'): 0.453592,
            (1, 'lb', 't'): 0.000453592,
            (1, 'kg', 'lb'): 2.20462,
            (1, 'kg', 't'): 0.001,
            (1, 't', 'lb'): 2204.62,
            (1, 't', 'kg'): 1000,
            # Pressure:
            (1, 'inHg', 'mB'): 33.86,
            (1, 'inHg', 'psi'): 0.4910,         # Google: 0.49109778
            (1, 'mB', 'inHg'): 0.029533,        # Google: 0.0295333727
            (1, 'mB', 'psi'): 0.0145037738,
            (1, 'psi', 'inHg'): 2.0362,         # Google: 2.03625437
            (1, 'psi', 'mB'): 68.94757,         # Google: 68.9475729
            # Speed:
            (1, 'kt', 'mph'): 1.15078,
            (1, 'kt', 'fpm'): 101.2686,
            (1, 'mph', 'kt'): 0.868976,
            (1, 'mph', 'fpm'): 88.0002,
            (1, 'fpm', 'kt'): 0.0098747300,
            (1, 'fpm', 'mph'): 0.0113636364,
            # Temperature:
            (0, u'°C', u'°F'): 32,
            (0, u'°C', u'°K'): 273.15,
            (0, u'°F', u'°C'): -17.7778,
            (0, u'°F', u'°K'): 255.372,
            (0, u'°K', u'°C'): -273.15,
            (0, u'°K', u'°F'): -459.67,
            # Time:
            (1, 'h', 'min'): 60,
            (1, 'h', 's'): 3600,
            (1, 'min', 'h'): 0.0166667,
            (1, 'min', 's'): 60,
            (1, 's', 'h'): 0.000277778,
            (1, 's', 'min'): 0.0166667,
            # Other:
            (1, 'gs-ddm', 'dots'): 11.428571428571429,
            (1, 'loc-ddm', 'dots'): 12.903225806451614,
            (1, 'mV', 'dots'): 0.01333333333333333,
        }

        for arguments, expected in data.iteritems():
            dp = max(abs(Decimal(str(expected)).as_tuple().exponent) - 1, 0)
            # Check forward conversion:
            i = arguments
            o = expected
            self.assertAlmostEqual(units.convert(*i), o, places=dp)
            # Check backward conversion:
            i = [expected] + list(arguments)[:0:-1]
            o = arguments[0]
            self.assertAlmostEqual(units.convert(*i), o, delta=0.001)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
