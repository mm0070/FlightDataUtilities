# -*- coding: utf-8 -*-
##############################################################################

'''
'''

##############################################################################
# Imports


import unittest

from decimal import Decimal
from itertools import chain

from flightdatautilities.units import *  # noqa


##############################################################################
# Test Cases


class TestUnitsModule(unittest.TestCase):

    def test__check_definitions(self):

        values = set(available())
        constants =  set(available(values=False)[1])
        # Check we have no redefinitions of units:
        self.assertEqual(len(values), len(constants), 'Unit redefinition!')
        # Check we have a category for every unit constant:
        x = list(chain.from_iterable(UNIT_CATEGORIES.values()))
        self.assertEqual(len(x), len(set(x)), 'Unit in multiple categories!')
        self.assertItemsEqual(set(x), values)
        # Check we have a description for every unit constant:
        self.assertItemsEqual(set(UNIT_DESCRIPTIONS.keys()), values)
        # Check we only correct to (and not from) standard units:
        self.assertLessEqual(set(UNIT_CORRECTIONS.values()), values)
        self.assertEqual(set(UNIT_CORRECTIONS.keys()) & values, set())
        # Check we only convert to and from standard units:
        self.assertLessEqual(set(STANDARD_CONVERSIONS.keys()), values)
        self.assertLessEqual(set(STANDARD_CONVERSIONS.values()), values)
        for mapping in CONVERSION_MULTIPLIERS, CONVERSION_FUNCTIONS:
            for k, v in mapping.iteritems():
                self.assertIn(k, values)
                self.assertLessEqual(set(v.keys()), values)

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
            # Angles:
            (1, DEGREE, RADIAN): 0.0174532925,
            (1, RADIAN, DEGREE): 57.2957795,
            # Energy:
            (1, JOULE, KJ): 0.001,
            (1, JOULE, MJ): 0.000001,
            (1, KJ, JOULE): 1000,
            (1, KJ, MJ): 0.001,
            (1, MJ, JOULE): 1000000,
            (1, MJ, KJ): 1000,
            # Flow (Mass):
            (1, LB_H, KG_H): 0.453592,
            (1, LB_H, LB_MIN): 0.0166666667,
            (1, LB_H, TONNE_H): 0.000453592,
            (1, LB_MIN, LB_H): 60,
            (1, LB_MIN, KG_H): 27.2155422,
            (1, LB_MIN, TONNE_H): 0.0272155422,
            (1, KG_H, LB_H): 2.20462,
            (1, KG_H, LB_MIN): 0.0367437104,
            (1, KG_H, TONNE_H): 0.001,
            (1, TONNE_H, LB_H): 2204.62,
            (1, TONNE_H, LB_MIN): 36.7437104,
            (1, TONNE_H, KG_H): 1000,
            # Flow (Volume):
            (1, PINT_H, QUART_H): 0.5,
            (1, PINT_H, GALLON_H): 0.125,
            (1, PINT_H, LITER_H): 0.473176,
            (1, QUART_H, PINT_H): 2,
            (1, QUART_H, GALLON_H): 0.25,
            (1, QUART_H, LITER_H): 0.946353,
            (1, GALLON_H, PINT_H): 8,
            (1, GALLON_H, QUART_H): 4,
            (1, GALLON_H, LITER_H): 3.78541,
            (1, LITER_H, PINT_H): 2.11338,
            (1, LITER_H, QUART_H): 1.05669,
            (1, LITER_H, GALLON_H): 0.264172,
            # Force:
            (1, LBF, KGF): 0.45359237,
            (1, LBF, DECANEWTON): 0.444822162,
            (1, LBF, NEWTON): 4.44822162,
            (1, KGF, LBF): 2.20462262,
            (1, KGF, DECANEWTON): 0.980665,
            (1, KGF, NEWTON): 9.80665,
            (1, DECANEWTON, LBF): 2.24808943,
            (1, DECANEWTON, KGF): 1.01971621,
            (1, DECANEWTON, NEWTON): 10,
            (1, NEWTON, LBF): 0.224808943,
            (1, NEWTON, KGF): 0.101971621,
            (1, NEWTON, DECANEWTON): 0.1,
            # Frequency:
            (1, KHZ, MHZ): 0.001,
            (1, KHZ, GHZ): 0.000001,
            (1, MHZ, KHZ): 1000.0,
            (1, MHZ, GHZ): 0.001,
            (1, GHZ, KHZ): 1000000.0,
            (1, GHZ, MHZ): 1000.0,
            # Length:
            (1, FT, METER): 0.3048,
            (1, FT, KM): 0.0003048,
            (1, FT, MILE): 0.000189394,
            (1, FT, NM): 0.000164579,
            (1, FT, MILLIMETER): 304.8,
            (1, METER, FT): 3.28084,
            (1, METER, KM): 0.001,
            (1, METER, MILE): 0.000621371,
            (1, METER, NM): 0.000539957,
            (1, METER, MILLIMETER): 1000,
            (1, KM, FT): 3280.84,
            (1, KM, METER): 1000,
            (1, KM, MILE): 0.621371,
            (1, KM, NM): 0.539957,
            (1, KM, MILLIMETER): 1000000,
            (1, MILE, FT): 5280,
            (1, MILE, METER): 1609.344,
            (1, MILE, KM): 1.60934,
            (1, MILE, NM): 0.868976,
            (1, MILE, MILLIMETER): 1609344,
            (1, NM, FT): 6076.12,
            (1, NM, METER): 1852,
            (1, NM, KM): 1.852,
            (1, NM, MILE): 1.15078,
            (1, NM, MILLIMETER): 1852000,
            (1, MILLIMETER, FT): 0.003280839895,
            (1, MILLIMETER, METER): 0.001,
            (1, MILLIMETER, KM): 0.000001,
            (1, MILLIMETER, MILE): 0.000000621371,
            (1, MILLIMETER, NM): 0.000000539957,
            # Mass:
            (1, LB, KG): 0.453592,
            (1, LB, SLUG): 0.0310809502,
            (1, LB, TONNE): 0.000453592,
            (1, KG, LB): 2.20462,
            (1, KG, SLUG): 0.0685217659,
            (1, KG, TONNE): 0.001,
            (1, SLUG, LB): 32.1740486,
            (1, SLUG, KG): 14.5939029,
            (1, SLUG, TONNE): 0.0145939029,
            (1, TONNE, LB): 2204.62,
            (1, TONNE, KG): 1000,
            (1, TONNE, SLUG): 68.5217659,
            # Pressure:
            (1, INHG, MILLIBAR): 33.86,
            (1, INHG, PASCAL): 3386.389,
            (1, INHG, HECTOPASCAL): 33.86389,
            (1, INHG, PSI): 0.4910,             # Google: 0.49109778
            (1, MILLIBAR, INHG): 0.029533,      # Google: 0.0295333727
            (1, MILLIBAR, PASCAL): 100,
            (1, MILLIBAR, HECTOPASCAL): 1,
            (1, MILLIBAR, PSI): 0.0145037738,
            (1, PASCAL, INHG): 0.0002952998,
            (1, PASCAL, MILLIBAR): 0.01,
            (1, PASCAL, HECTOPASCAL): 0.01,
            (1, PASCAL, PSI): 0.00014503774,
            (1, HECTOPASCAL, INHG): 0.02952998,
            (1, HECTOPASCAL, MILLIBAR): 1,
            (1, HECTOPASCAL, PASCAL): 100,
            (1, HECTOPASCAL, PSI): 0.014503774,
            (1, PSI, INHG): 2.0362,             # Google: 2.03625437
            (1, PSI, MILLIBAR): 68.94757,       # Google: 68.9475729
            (1, PSI, PASCAL): 6894.757,
            (1, PSI, HECTOPASCAL): 68.94757,
            # Speed:
            (1, KT, MPH): 1.15078,
            (1, KT, FPM): 101.2686,
            (1, MPH, KT): 0.868976,
            (1, MPH, FPM): 88.0002,
            (1, FPM, KT): 0.0098747300,
            (1, FPM, MPH): 0.0113636364,
            (1, FPM, FPS): 60.0,
            (1, FPS, FPM): 0.016666666666666666,
            # Temperature:
            (0, CELSIUS, FAHRENHEIT): 32,
            (0, CELSIUS, KELVIN): 273.15,
            (0, FAHRENHEIT, CELSIUS): -17.7778,
            (0, FAHRENHEIT, KELVIN): 255.372,
            (0, KELVIN, CELSIUS): -273.15,
            (0, KELVIN, FAHRENHEIT): -459.67,
            # Time:
            (1, HOUR, MINUTE): 60,
            (1, HOUR, SECOND): 3600,
            (1, MINUTE, HOUR): 0.0166667,
            (1, MINUTE, SECOND): 60,
            (1, SECOND, HOUR): 0.000277778,
            (1, SECOND, MINUTE): 0.0166667,
            # Torque:
            (1, FT_LB, IN_LB): 12,
            (1, FT_LB, IN_OZ): 192,
            (1, IN_LB, FT_LB): 0.0833,
            (1, IN_LB, IN_OZ): 16,
            (1, IN_OZ, FT_LB): 0.00520833,
            (1, IN_OZ, IN_LB): 0.0625,
            # Volume:
            (1, PINT, QUART): 0.5,
            (1, PINT, GALLON): 0.125,
            (1, PINT, LITER): 0.473176,
            (1, QUART, PINT): 2,
            (1, QUART, GALLON): 0.25,
            (1, QUART, LITER): 0.946353,
            (1, GALLON, PINT): 8,
            (1, GALLON, QUART): 4,
            (1, GALLON, LITER): 3.78541,
            (1, LITER, PINT): 2.11338,
            (1, LITER, QUART): 1.05669,
            (1, LITER, GALLON): 0.264172,
            # Other:
            (1, GS_DDM, DOTS): 11.428571428571429,
            (1, LOC_DDM, DOTS): 12.903225806451614,
            (1, MILLIVOLT, DOTS): 0.01333333333333333,
            (1, MICROAMP, DOTS): 0.01333333333333333,
            (1, DOTS, GS_DDM): 0.0875,
            (1, DOTS, LOC_DDM): 0.0775,
            (1, DOTS, MILLIVOLT): 75,
            (1, DOTS, MICROAMP): 75,
        }

        for arguments, expected in data.iteritems():
            dp = max(abs(Decimal(str(expected)).as_tuple().exponent) - 1, 0)
            # Check forward conversion:
            i = arguments
            o = expected
            m = 'Invalid conversion from %s --> %s' % i[1:]
            self.assertAlmostEqual(convert(*i), o, places=dp, msg=m)
            # Check backward conversion:
            i = tuple([expected] + list(arguments)[:0:-1])
            o = arguments[0]
            m = 'Invalid reverse conversion from %s --> %s' % i[1:]
            self.assertAlmostEqual(convert(*i), o, delta=0.001, msg=m)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
