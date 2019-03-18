'''
 Tests for Python 3 and Numpy 1.15 upgrade helpers.
'''
import numpy as np
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from flightdatautilities.numpy_utils import (
    py2round,
    slices_int,
    np_ma_zeros
)


class TestPy2Round(unittest.TestCase):
    def test_py2round(self):
        test_range = np.arange(0, 100, 0.1).tolist()
        rounded = [py2round(n) for n in test_range]
        expected = [float(0)]*5
        for n in range(1,100):
            expected += [float(n)]*10
        expected += [float(100)]*5
        self.assertEqual(len(rounded), len(expected))
        self.assertEqual(rounded, expected)


class TestSlicesInt(unittest.TestCase):
    def test_single_slice(self):
        self.assertEqual(slices_int(slice(None, None, None)),
                         slice(None, None, None))
        self.assertEqual(slices_int(slice(1, 2, 3)), slice(1, 2, 3))
        self.assertEqual(slices_int(slice(1.1, 2.2, 3.3)), slice(1, 2, 3))
        self.assertEqual(slices_int(slice(1, 2.2, 3)), slice(1, 2, 3))
        self.assertEqual(slices_int(slice(1, 2.2, None)), slice(1, 2, None))
        self.assertEqual(slices_int(slice(1.1, 2.2, 3.3)).start, 1)
        self.assertEqual(slices_int(slice(1.1, 2.2, 3.3)).stop, 2)
        self.assertEqual(slices_int(slice(1.1, 2.2, 3.3)).step, 3)
        self.assertEqual(slices_int(slice(None, None, None)).start, None)
        self.assertEqual(slices_int(slice(None, None, None)).stop, None)
        self.assertEqual(slices_int(slice(None, None, None)).step, None)

    def test_list_of_slices(self):
        self.assertEqual(slices_int([slice(None,None,None),]),
                         [slice(None,None,None),])
        self.assertEqual(slices_int((slice(None,None,None),)),
                         [slice(None,None,None),])
        mixed_slices = [
            slice(1629.0, 2299.0),
            slice(3722, 4708),
            slice(4726, 4807.0),
            slice(5009.0, 5071),
            slice(5168, 6883.0, 2),
            slice(8433.0, 9058, 2.5)
        ]
        expected_slices = [
            slice(1629, 2299),
            slice(3722, 4708),
            slice(4726, 4807),
            slice(5009, 5071),
            slice(5168, 6883, 2),
            slice(8433, 9058, 2)
        ]
        self.assertEqual(slices_int(mixed_slices), expected_slices)

    def test_create_slice_single_arg(self):
        self.assertEqual(slices_int(1.5), slice(1))

    def test_create_slice_two_args(self):
        self.assertEqual(slices_int(1.5, 10.9), slice(1, 10))
        self.assertEqual(slices_int(1.5, None), slice(1, None))
        self.assertEqual(slices_int(None, None), slice(None, None))

    def test_create_slice_three_args(self):
        self.assertEqual(slices_int(1.5, 10.9, 2.2), slice(1, 10, 2))
        self.assertEqual(slices_int(1.5, 10.9, None), slice(1, 10, None))
        self.assertEqual(slices_int(None, None, None), slice(None, None, None))


class TestNpMaZeros(unittest.TestCase):
    def test_np_ma_zeros(self):
        self.assertEqual(np_ma_zeros(None), np.ma.zeros(None))
        np.testing.assert_equal(np_ma_zeros(10), np.ma.zeros(10))
        np.testing.assert_equal(np_ma_zeros(10.6), np.ma.zeros(10))
