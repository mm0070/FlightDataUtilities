# cython: language_level=3, boundscheck=False
import unittest

from libc.math cimport M_PI

from flightdatautilities.data cimport scalar as sc


################################################################################
# Power of 2


class TestIsPower2(unittest.TestCase):
    def test_is_power2(self):
        self.assertEqual([i for i in range(2000) if sc.is_power2(i)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(sc.is_power2(-2))
        self.assertFalse(sc.is_power2(2.2))


class TestIsPower2Fraction(unittest.TestCase):
    def test_is_power2_fraction(self):
        self.assertEqual([x for x in range(2000) if sc.is_power2_fraction(x)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(sc.is_power2_fraction(-2))
        self.assertFalse(sc.is_power2_fraction(2.2))
        self.assertTrue(sc.is_power2_fraction(0.5))
        self.assertTrue(sc.is_power2_fraction(0.25))
        self.assertTrue(sc.is_power2_fraction(0.125))
        self.assertTrue(sc.is_power2_fraction(0.0625))
        self.assertTrue(sc.is_power2_fraction(0.03125))
        self.assertTrue(sc.is_power2_fraction(0.015625))
        self.assertFalse(sc.is_power2_fraction(0.75))
        self.assertFalse(sc.is_power2_fraction(0.2))
        self.assertFalse(sc.is_power2_fraction(0.015626))


################################################################################
# Random


class TestRandint(unittest.TestCase):
    def test_randint(self):
        self.assertEqual(sc.randint(0, 0), 0)
        self.assertEqual(sc.randint(1, 1), 1)
        self.assertTrue(0 <= sc.randint(0, 10) <= 10)
        self.assertTrue(0 <= sc.randint(10, 0) <= 10)  # min max are automatically flipped

        for x in range(100):
            self.assertTrue(0 <= sc.randint(0, x) <= x)

        for x in range(-100, 0):
            self.assertTrue(x <= sc.randint(x, 1000) <= 1000)


################################################################################
# Bits


class TestFullRange(unittest.TestCase):
    def test_full_range(self):
        self.assertEqual(sc.full_range(0), 0)
        self.assertEqual(sc.full_range(1), 2)
        self.assertEqual(sc.full_range(2), 4)
        self.assertEqual(sc.full_range(3), 8)
        self.assertEqual(sc.full_range(4), 16)


class TestSaturatedValue(unittest.TestCase):
    def test_saturated_value(self):
        self.assertEqual(sc.saturated_value(0), 0)
        self.assertEqual(sc.saturated_value(1), 1)
        self.assertEqual(sc.saturated_value(2), 3)
        self.assertEqual(sc.saturated_value(3), 7)
        self.assertEqual(sc.saturated_value(4), 15)


################################################################################
# Unit conversion


class TestDegreesToRadians(unittest.TestCase):
    def test_degrees_to_radians(self):
        self.assertEqual(sc.degrees_to_radians(0), 0)
        self.assertEqual(sc.degrees_to_radians(180), M_PI)
        self.assertEqual(sc.degrees_to_radians(90), M_PI / 2)
        self.assertEqual(sc.degrees_to_radians(360), M_PI * 2)
        self.assertEqual(sc.degrees_to_radians(1000), 17.453292519943297)


class TestRadiansToDegrees(unittest.TestCase):
    def test_radians_to_degrees(self):
        self.assertEqual(sc.radians_to_degrees(0), 0)
        self.assertEqual(sc.radians_to_degrees(1), 57.29577951308232)
        self.assertEqual(sc.radians_to_degrees(1.5), 85.94366926962348)

