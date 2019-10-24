# cython: language_level=3, boundscheck=False
import unittest

import numpy as np

from flightdatautilities.array cimport cython as cy
from flightdatautilities.type import is_memoryview


class TestEmptyInt64(unittest.TestCase):
    def test_empty_int64(self):
        memview = cy.empty_int64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('int64'))


class TestEmpty2dInt64(unittest.TestCase):
    def test_empty2d_int64(self):
        memview = cy.empty2d_int64(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('int64'))


class TestZerosInt64(unittest.TestCase):
    def test_zeros_int64(self):
        memview = cy.zeros_int64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('int64'))
        self.assertEqual(array.tolist(), [0, 0, 0, 0, 0])


class TestZeros2dInt64(unittest.TestCase):
    def test_zeros2d_int64(self):
        memview = cy.zeros2d_int64(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('int64'))
        self.assertEqual(array.tolist(), [[0, 0, 0], [0, 0, 0]])


class TestEmptyIntp(unittest.TestCase):
    def test_empty_intp(self):
        memview = cy.empty_intp(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('intp'))


class TestEmpty2dIntp(unittest.TestCase):
    def test_empty2d_intp(self):
        memview = cy.empty2d_intp(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('intp'))


class TestZerosIntp(unittest.TestCase):
    def test_zeros_intp(self):
        memview = cy.zeros_intp(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('intp'))
        self.assertEqual(array.tolist(), [0, 0, 0, 0, 0])


class TestZeros2dIntp(unittest.TestCase):
    def test_zeros2d_intp(self):
        memview = cy.zeros2d_intp(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('intp'))
        self.assertEqual(array.tolist(), [[0, 0, 0], [0, 0, 0]])


class TestEmptyUint8(unittest.TestCase):
    def test_empty_uint8(self):
        memview = cy.empty_uint8(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('uint8'))


class TestZerosUint8(unittest.TestCase):
    def test_zeros_uint8(self):
        memview = cy.zeros_uint8(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('uint8'))
        self.assertEqual(array.tolist(), [0, 0, 0, 0, 0])


class TestOnesUint8(unittest.TestCase):
    def test_ones_uint8(self):
        memview = cy.ones_uint8(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('uint8'))
        self.assertEqual(array.tolist(), [1, 1, 1, 1, 1])


class TestEmptyUint16(unittest.TestCase):
    def test_empty_uint16(self):
        memview = cy.empty_uint16(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('uint16'))


class TestZerosUint16(unittest.TestCase):
    def test_zeros_uint16(self):
        memview = cy.zeros_uint16(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('uint16'))
        self.assertEqual(array.tolist(), [0, 0, 0, 0, 0])


class TestEmptyUint64(unittest.TestCase):
    def test_empty_uint64(self):
        memview = cy.empty_uint64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('uint64'))


class TestZerosUint64(unittest.TestCase):
    def test_zeros_uint64(self):
        memview = cy.zeros_uint64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('uint64'))
        self.assertEqual(array.tolist(), [0, 0, 0, 0, 0])


class TestEmptyFloat64(unittest.TestCase):
    def test_empty_float64(self):
        memview = cy.empty_float64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('float64'))


class TestEmpty2dFloat64(unittest.TestCase):
    def test_empty2d_float64(self):
        memview = cy.empty2d_float64(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        self.assertEqual(np.asarray(memview).dtype, np.dtype('float64'))


class TestZerosFloat64(unittest.TestCase):
    def test_zeros_float64(self):
        memview = cy.zeros_float64(5)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (5,))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('float64'))
        self.assertEqual(array.tolist(), [0., 0., 0., 0., 0.])


class TestZeros2dFloat64(unittest.TestCase):
    def test_zeros2d_float64(self):
        memview = cy.zeros2d_float64(2, 3)
        self.assertTrue(is_memoryview(memview))
        self.assertEqual(memview.shape, (2, 3))
        array = np.asarray(memview)
        self.assertEqual(array.dtype, np.dtype('float64'))
        self.assertEqual(array.tolist(), [[0., 0., 0.], [0., 0., 0.]])


class TestReadUint(unittest.TestCase):
    def test_read_uint16_le(self):
        data = np.zeros(4, dtype=np.uint8)
        self.assertEqual(cy.read_uint16_le(data, 0), 0)
        self.assertEqual(cy.read_uint16_le(data, 1), 0)
        self.assertEqual(cy.read_uint16_le(data, 2), 0)
        data = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(cy.read_uint16_le(data, 0), 513)
        self.assertEqual(cy.read_uint16_le(data, 1), 770)
        self.assertEqual(cy.read_uint16_le(data, 2), 1027)

    def test_read_uint16_be(self):
        data = np.zeros(4, dtype=np.uint8)
        self.assertEqual(cy.read_uint16_be(data, 0), 0)
        self.assertEqual(cy.read_uint16_be(data, 1), 0)
        self.assertEqual(cy.read_uint16_be(data, 2), 0)
        data = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(cy.read_uint16_be(data, 0), 258)
        self.assertEqual(cy.read_uint16_be(data, 1), 515)
        self.assertEqual(cy.read_uint16_be(data, 2), 772)

    def test_read_uint32_le(self):
        data = np.zeros(6, dtype=np.uint8)
        self.assertEqual(cy.read_uint32_le(data, 0), 0)
        self.assertEqual(cy.read_uint32_le(data, 1), 0)
        self.assertEqual(cy.read_uint32_le(data, 2), 0)
        data = np.arange(1, 7, dtype=np.uint8)
        self.assertEqual(cy.read_uint32_le(data, 0), 67305985)
        self.assertEqual(cy.read_uint32_le(data, 1), 84148994)
        self.assertEqual(cy.read_uint32_le(data, 2), 100992003)

    def test_read_uint32_be(self):
        data = np.zeros(6, dtype=np.uint8)
        self.assertEqual(cy.read_uint32_be(data, 0), 0)
        self.assertEqual(cy.read_uint32_be(data, 1), 0)
        self.assertEqual(cy.read_uint32_be(data, 2), 0)
        data = np.arange(1, 7, dtype=np.uint8)
        self.assertEqual(cy.read_uint32_be(data, 0), 16909060)
        self.assertEqual(cy.read_uint32_be(data, 1), 33752069)
        self.assertEqual(cy.read_uint32_be(data, 2), 50595078)


class TestNoneIdx(unittest.TestCase):
    def test_none_idx(self):
        self.assertEqual(cy.none_idx(0), 0)
        self.assertEqual(cy.none_idx(2), 2)
        self.assertEqual(cy.none_idx(-1), -1)
        self.assertEqual(cy.none_idx(None), cy.NONE_IDX)


class TestIdxNone(unittest.TestCase):
    def test_idx_none(self):
        self.assertEqual(cy.idx_none(0), 0)
        self.assertEqual(cy.idx_none(2), 2)
        self.assertEqual(cy.idx_none(-1), -1)
        self.assertEqual(cy.idx_none(cy.NONE_IDX), None)


class TestArrayWraparoundIdx(unittest.TestCase):
    def test_array_wraparound_idx(self):
        self.assertEqual(cy.array_wraparound_idx(0, 1), 0)
        self.assertEqual(cy.array_wraparound_idx(1, 1), 0)
        self.assertEqual(cy.array_wraparound_idx(2, 1), 0)
        self.assertEqual(cy.array_wraparound_idx(-1, 1), 0)
        self.assertEqual(cy.array_wraparound_idx(-2, 1), 0)
        self.assertEqual(cy.array_wraparound_idx(0, 2), 0)
        self.assertEqual(cy.array_wraparound_idx(1, 2), 1)
        self.assertEqual(cy.array_wraparound_idx(2, 2), 1)
        self.assertEqual(cy.array_wraparound_idx(3, 2), 1)
        self.assertEqual(cy.array_wraparound_idx(-1, 2), 1)
        self.assertEqual(cy.array_wraparound_idx(-2, 2), 0)
        self.assertEqual(cy.array_wraparound_idx(-3, 2), 0)
        self.assertEqual(cy.array_wraparound_idx(cy.NONE_IDX, 10), 9)


class TestNearestIdx(unittest.TestCase):

    def test_nearest_idx(self):
        self.assertEqual(cy.nearest_idx(np.empty(0, dtype=np.uint8), 0), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(np.array([False], dtype=np.uint8), 0), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(np.array([True], dtype=np.uint8), 0), 0)
        self.assertEqual(cy.nearest_idx(np.array([False], dtype=np.uint8), 0, match=False), 0)
        data = np.zeros(5, dtype=np.bool)
        self.assertEqual(cy.nearest_idx(data, 0), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, 3), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, -2), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, 5), cy.NONE_IDX)
        data = np.ones(5, dtype=np.bool)
        self.assertEqual(cy.nearest_idx(data, 0), 0)
        self.assertEqual(cy.nearest_idx(data, 0, match=False), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, 3), 3)
        self.assertEqual(cy.nearest_idx(data, -2), 0)
        self.assertEqual(cy.nearest_idx(data, 5), 4)
        self.assertEqual(cy.nearest_idx(data, 0, match=True, start_idx=2), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, 4, match=True, start_idx=2), 4)
        self.assertEqual(cy.nearest_idx(data, 4, match=True, start_idx=0, stop_idx=2), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(data, 1, match=True, start_idx=0, stop_idx=2), 1)
        self.assertEqual(cy.nearest_idx(data, 1, match=True, start_idx=0, stop_idx=2), 1)
        self.assertEqual(cy.nearest_idx(data, 2, match=True, start_idx=0, stop_idx=2), cy.NONE_IDX)
        self.assertEqual(cy.nearest_idx(np.array([True, False, False, False, False], dtype=np.uint8), 3), 0)
        self.assertEqual(cy.nearest_idx(np.array([False, False, False, False, True], dtype=np.uint8), 1), 4)
        self.assertEqual(cy.nearest_idx(np.array([False, True, True, False, False], dtype=np.uint8), 3), 2)

