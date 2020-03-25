# cython: language_level=3, boundscheck=False
import unittest

import numpy as np

from flightdatautilities.data import interpolate


class TestInterpolator(unittest.TestCase):
    def test_interpolator(self):
        def interp(points, data, copy=True):
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=np.float64)
            return np.asarray(interpolate.Interpolator(points).interpolate(data, copy=copy)).tolist()

        # Must be at least two points.
        self.assertRaises(ValueError, interpolate.Interpolator, [])
        self.assertRaises(ValueError, interpolate.Interpolator, [(0, 1)])
        points = [(0, 1), (1, 2)]
        self.assertEqual(interp(points, [0, 1]), [1, 2])
        points = [(0, 1), (1, 2), (2, 3)]
        self.assertEqual(interp(points, [0]), [1])
        self.assertEqual(interp(points, [2]), [3])
        self.assertEqual(interp(points, [0, 1, 2]), [1, 2, 3])
        self.assertEqual(interp(points, [1.5]), [2.5])
        self.assertEqual(interp(points, [-1, 0, 1, 2, 3]), [0, 1, 2, 3, 4])
        self.assertEqual(interp(points, [131.3]), [132.3])
        points = [
            (204.8, 0.5),
            (362.496, 0.9),
            (495.616, 5),
            (626.688, 15),
            (759.808, 20),
            (890.88, 25.2),
            (1024, 30),
        ]
        data = [101.2, 203.5, 312.4, 442.1, 582.4, 632.12, 785.2, 890.21, 904.64, 1000, 1024, 1200]
        # output exactly matches extrap1d implementation.
        expected = [
            0.23721590909090898,
            0.4967025162337662,
            0.7729301948051948,
            3.351745793269232,
            11.62109375,
            15.204026442307693,
            21.007373046875003,
            25.173419189453124,
            25.696153846153845,
            29.134615384615383,
            30.0,
            36.34615384615385,
        ]
        for x, y in zip(interp(points, data), expected):
            self.assertAlmostEqual(x, y, places=8)
        points = [(0, 10), (1, 20), (1.5, 40), (2.0, 400)]
        data = [0, 1, 1.5, 2.0]
        expected = [10, 20, 40, 400]
        self.assertEqual(interp(points, data), expected)
        # check results are the same with copy=False
        self.assertEqual(interp(points, data, copy=False), expected)
