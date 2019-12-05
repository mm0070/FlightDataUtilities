# cython: language_level=3, boundscheck=False
from binascii import hexlify
import os
import unittest

cimport cython
import numpy as np
cimport numpy as np
from numpy.ma.testutils import assert_array_equal

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.data cimport cython as cy, operations as op
from flightdatautilities.data.operations import contract_runs, remove_small_runs, runs_of_ones
from flightdatautilities.read import reader


################################################################################
# Slice operations

class TestNearestSlice(unittest.TestCase):
    def test_nearest_slice(self):
        self.assertEqual(op.nearest_slice(np.empty(0, dtype=np.bool), 1), None)
        data = np.zeros(5, dtype=np.bool)
        self.assertEqual(op.nearest_slice(data, 2), None)
        self.assertEqual(op.nearest_slice(data, -1), None)
        self.assertEqual(op.nearest_slice(data, 8), None)
        data = np.array([False, False, False, False, True])
        self.assertEqual(op.nearest_slice(data, 2), slice(4, 5))
        self.assertEqual(op.nearest_slice(data, 5), slice(4, 5))
        self.assertEqual(op.nearest_slice(data, 8), slice(4, 5))
        self.assertEqual(op.nearest_slice(data, -2), slice(4, 5))
        data = np.array([True, True, False, False, False])
        self.assertEqual(op.nearest_slice(data, 0), slice(0, 2))
        self.assertEqual(op.nearest_slice(data, 2), slice(0, 2))
        self.assertEqual(op.nearest_slice(data, 5), slice(0, 2))
        self.assertEqual(op.nearest_slice(data, 8), slice(0, 2))
        self.assertEqual(op.nearest_slice(data, -2), slice(0, 2))
        data = np.array([False, True, True, False, False, True, False, False])
        for idx, sl in [(0, slice(1, 3)), (1, slice(1, 3)), (2, slice(1, 3)), (3, slice(1, 3)),
                        (4, slice(5, 6)), (5, slice(5, 6)), (6, slice(5, 6)), (7, slice(5, 6))]:
            self.assertEqual(op.nearest_slice(data, idx), sl)


class TestRunsOfOnes(unittest.TestCase):
    def test_runs_of_ones(self):
        data = np.ma.array(
            [0,0,1,0,1,1,1,1,1,0,0,1,1,1,0,1,1,1],
            mask=np.concatenate([np.zeros(14, dtype=np.bool), np.ones(4, dtype=np.bool)]),
            dtype=np.bool,
        )
        self.assertEqual(list(runs_of_ones(data)), [slice(2, 3), slice(4, 9), slice(11, 14), slice(15, 18)])
        self.assertEqual(list(runs_of_ones(data, min_samples=2)), [slice(4, 9), slice(11, 14), slice(15, 18)])
        self.assertEqual(list(runs_of_ones(data, min_samples=3)), [slice(4, 9)])


class TestSlicesToArray(unittest.TestCase):
    def test_slices_to_array(self):
        self.assertEqual(op.slices_to_array(0, []).tolist(), [])
        self.assertEqual(op.slices_to_array(0, [slice(0, 1)]).tolist(), [])
        self.assertEqual(op.slices_to_array(1, []).tolist(), [False])
        self.assertEqual(op.slices_to_array(1, [slice(0, 1)]).tolist(), [True])
        self.assertEqual(op.slices_to_array(5, []).tolist(), [False] * 5)
        self.assertEqual(op.slices_to_array(5, [slice(None, None)]).tolist(), [True] * 5)
        self.assertEqual(op.slices_to_array(5, [slice(-1, 6)]).tolist(), [True] * 5)
        self.assertEqual(op.slices_to_array(5, [slice(None, 3)]).tolist(), [1, 1, 1, 0, 0])
        self.assertEqual(op.slices_to_array(5, [slice(3, None)]).tolist(), [0, 0, 0, 1, 1])
        self.assertEqual(op.slices_to_array(5, [slice(4, 3)]).tolist(), [False] * 5)
        self.assertEqual(op.slices_to_array(5, [slice(1, 2), slice(3, 5)]).tolist(), [0, 1, 0, 1, 1])


################################################################################
# Type-inspecific array operations

class TestAlignArrays(unittest.TestCase):
    def test_align_arrays(self):
        self.assertEqual(op.align_arrays(np.arange(10), np.arange(20, 30)).tolist(),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(op.align_arrays(np.arange(40, 80), np.arange(20, 40)).tolist(),
                         [40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78])
        self.assertEqual(op.align_arrays(np.arange(40,80), np.arange(30, 40)).tolist(),
                         [40, 44, 48, 52, 56, 60, 64, 68, 72, 76])
        self.assertEqual(op.align_arrays(np.arange(10), np.arange(20, 40)).tolist(),
                         [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9])


class TestIsConstant(unittest.TestCase):
    def test_is_constant(self):
        self.assertTrue(op.is_constant[np.uint16_t](cy.empty_uint16(0)))
        self.assertTrue(op.is_constant[np.uint8_t](cy.zeros_uint8(10)))
        self.assertTrue(op.is_constant[np.uint16_t](cy.zeros_uint16(10)))
        self.assertTrue(op.is_constant[np.uint32_t](cy.zeros_uint32(10)))
        self.assertTrue(op.is_constant[np.uint8_t](cy.ones_uint8(10)))
        self.assertFalse(op.is_constant[np.uint32_t](np.arange(10, dtype=np.uint32)))
        self.assertFalse(op.is_constant[np.float64_t](np.arange(10, dtype=np.float64)))


class TestLongestSection(unittest.TestCase):
    def test_longest_section(self):
        self.assertEqual(op.longest_section[np.uint8_t](np.empty(0, dtype=np.uint8)), 0)
        data = np.zeros(10, dtype=np.uint8)
        self.assertEqual(op.longest_section[np.uint8_t](data), len(data))
        self.assertEqual(op.longest_section[np.uint8_t](data, 0), len(data))
        self.assertEqual(op.longest_section[np.uint8_t](data, 1), 0)
        data[0] = 1
        self.assertEqual(op.longest_section[np.uint8_t](data), 9)
        self.assertEqual(op.longest_section[np.uint8_t](data, 1), 1)
        data[9] = 1
        self.assertEqual(op.longest_section[np.uint8_t](data), 8)
        self.assertEqual(op.longest_section[np.uint8_t](data, 1), 1)
        data[2:4] = 2
        self.assertEqual(op.longest_section[np.uint8_t](data), 5)
        self.assertEqual(op.longest_section[np.uint8_t](data, 1), 1)
        self.assertEqual(op.longest_section[np.uint8_t](data, 2), 2)
        data[:] = 2
        self.assertEqual(op.longest_section[np.uint8_t](data), 0)
        self.assertEqual(op.longest_section[np.uint8_t](data, 1), 0)
        self.assertEqual(op.longest_section[np.uint8_t](data, 2), len(data))
        data = np.zeros(5, dtype=np.float64)
        self.assertEqual(op.longest_section[np.float64_t](data), 5)
        self.assertEqual(op.longest_section[np.float64_t](data, 1.5), 0)
        data[1] = 1.5
        self.assertEqual(op.longest_section[np.float64_t](data), 3)
        self.assertEqual(op.longest_section[np.float64_t](data, 1.5), 1)
        self.assertEqual(op.longest_section[np.float64_t](data, 4.7), 0)
        data[3:] = 1.5
        self.assertEqual(op.longest_section[np.float64_t](data), 1)
        self.assertEqual(op.longest_section[np.float64_t](data, 1.5), 2)
        data[:] = 1.5
        self.assertEqual(op.longest_section[np.float64_t](data), 0)
        self.assertEqual(op.longest_section[np.float64_t](data, 1.5), len(data))


class TestSwapBytes(unittest.TestCase):
    def test_swap_bytes(self):
        self.assertEqual(len(op.swap_bytes(np.ones(0, dtype=np.uint16))), 0)
        data = b'\xAF'
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint8).copy()).tostring(), data)
        data = b'\x12\xAB\xCD\xEF'
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint8).copy()).tostring(), data)
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint16).copy()).tostring(), b'\xAB\x12\xEF\xCD')


class TestTwosComplement(unittest.TestCase):
    def test_twos_complement(self):
        self.assertEqual(op.twos_complement(np.arange(4), 2).tolist(), [0, 1, -2, -1])


################################################################################
# Boolean array operations

class TestRemoveSmallRuns(unittest.TestCase):
    def test_remove_small_runs(self):
        def call(x, *args, **kwargs):
            return remove_small_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
        T, F = True, False
        self.assertEqual(call([]), [])
        self.assertEqual(call([F,T,F], 0), [F,T,F])
        self.assertEqual(call([F,T,F], 1), [F,F,F])
        self.assertEqual(call([T,F,T], 1, match=False), [T,T,T])
        self.assertEqual(call([T,T,F], 1), [T,T,F])
        self.assertEqual(call([T,T,F], 2), [F,F,F])
        self.assertEqual(call([T,T,F], 1, 2), [F,F,F])
        self.assertEqual(call([T,T,T], 1), [T,T,T])
        self.assertEqual(call([T,T,T], 3), [F,F,F])
        self.assertEqual(call([T,T,T], 1, 4), [F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T], 2), [F,T,T,T,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 2), [F,T,T,T,F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 2, 2), [F,F,F,F,F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 1.5, 2), [F,F,F,F,F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 1.4, 2), [F,T,T,T,F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 1.4, 2.2), [F,F,F,F,F,F,F,F])


class TestSectionOverlap(unittest.TestCase):
    def test_section_overlap(self):
        def call(x, y):
            return op.section_overlap(np.array(x, dtype=np.bool),
                                         np.array(y, dtype=np.bool)).tolist()
        T, F = True, False
        self.assertEqual(call([], []), [])
        self.assertEqual(call([F], [F]), [F])
        self.assertEqual(call([T], [F]), [F])
        self.assertEqual(call([F], [T]), [F])
        self.assertEqual(call([T], [T]), [T])
        self.assertEqual(call([F,F], [F,F]), [F,F])
        self.assertEqual(call([T,F], [F,F]), [F,F])
        self.assertEqual(call([F,T], [F,F]), [F,F])
        self.assertEqual(call([F,F], [T,F]), [F,F])
        self.assertEqual(call([F,F], [F,T]), [F,F])
        self.assertEqual(call([T,F], [F,T]), [F,F])
        self.assertEqual(call([T,F], [T,F]), [T,F])
        self.assertEqual(call([F,T], [F,T]), [F,T])
        self.assertEqual(call([T,T], [T,F]), [T,T])
        self.assertEqual(call([T,T], [F,T]), [T,T])
        self.assertEqual(call([T,T], [T,T]), [T,T])
        self.assertEqual(call([F,F,F], [F,F,F]), [F,F,F])
        self.assertEqual(call([F,T,F], [F,T,F]), [F,T,F])
        self.assertEqual(call([T,T,F], [F,T,F]), [T,T,F])
        self.assertEqual(call([F,T,T], [F,T,F]), [F,T,T])
        self.assertEqual(call([F,F,T,T,F,T,F,F,F,F,T,T,F],
                              [F,T,T,F,F,F,T,F,T,T,T,T,F]),
                              [F,T,T,T,F,F,F,F,T,T,T,T,F])


################################################################################
# Uint8 array (bytes) operations


class TestKeyValue(unittest.TestCase):
    def test_key_value(self):
        data = b'***\x0ATAILNUM=G-FDSL\x0ASERIALNUM=10344\x0A***'
        delimiter = b'='
        separator = b'\x0A'
        self.assertEqual(op.key_value(data, b'TAILNUM', delimiter, separator), b'G-FDSL')
        self.assertEqual(op.key_value(data, b'SERIALNUM', delimiter, separator), b'10344')


class TestSubarrayIdxUint8(unittest.TestCase):
    def test_subarray_idx_uint8(self):
        arr = np.zeros(16, dtype=np.uint8)
        subarr = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(op.subarray_idx_uint8(arr, subarr), None)
        self.assertEqual(op.subarray_idx_uint8(arr, subarr, start=5), None)
        arr[0] = 1
        arr[1] = 2
        arr[2] = 3
        arr[3] = 4
        self.assertEqual(op.subarray_idx_uint8(arr, subarr), 0)
        self.assertEqual(op.subarray_idx_uint8(arr, subarr, start=1), None)
        arr[1] = 5
        self.assertEqual(op.subarray_idx_uint8(arr, subarr), None)
        arr[12] = 1
        arr[13] = 2
        arr[14] = 3
        arr[15] = 4
        self.assertEqual(op.subarray_idx_uint8(arr, subarr), 12)
        self.assertEqual(op.subarray_idx_uint8(arr, subarr, start=10), 12)
        self.assertEqual(op.subarray_idx_uint8(arr, subarr, start=14), None)
        self.assertEqual(op.subarray_idx_uint8(subarr, arr), None)
        self.assertEqual(op.subarray_idx_uint8(subarr, arr, start=10000), None)


class TestSubarrayExistsUint8(unittest.TestCase):
    def test_subarray_exists_uint8(self):
        arr = np.zeros(16, dtype=np.uint8)
        subarr = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(op.subarray_exists_uint8(arr, subarr), False)
        self.assertEqual(op.subarray_exists_uint8(arr, subarr, start=5), False)
        arr[0] = 1
        arr[1] = 2
        arr[2] = 3
        arr[3] = 4
        self.assertEqual(op.subarray_exists_uint8(arr, subarr), True)
        self.assertEqual(op.subarray_exists_uint8(arr, subarr, start=1), False)
        arr[1] = 5
        self.assertEqual(op.subarray_exists_uint8(arr, subarr), False)
        arr[12] = 1
        arr[13] = 2
        arr[14] = 3
        arr[15] = 4
        self.assertEqual(op.subarray_exists_uint8(arr, subarr), True)
        self.assertEqual(op.subarray_exists_uint8(arr, subarr, start=10), True)
        self.assertEqual(op.subarray_exists_uint8(arr, subarr, start=14), False)
        self.assertEqual(op.subarray_exists_uint8(subarr, arr), False)
        self.assertEqual(op.subarray_exists_uint8(subarr, arr, start=10000), False)


################################################################################
# Flight Data Recorder data operations

class TestPack(unittest.TestCase):
    def test_pack(self):
        self.assertEqual(bytes(op.pack(b'')), b'')
        self.assertEqual(bytes(op.pack(b'\x47')), b'')
        self.assertEqual(bytes(op.pack(b'\x47\x02')), b'')
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB')), b'')
        result = b'\x47\xB2\xCA'
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB\x0C')), result)
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB\x0C\xB8')), result)
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB\x0C\xB8\x05')), result)
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB\x0C\xB8\x05\xDE')), result)
        self.assertEqual(bytes(op.pack(b'\x47\x02\xAB\x0C\xB8\x05\xDE\x0F')), result + b'\xB8\xE5\xFD')


class TestUnpack(unittest.TestCase):
    def test_unpack(self):
        self.assertEqual(bytes(op.unpack(b'')), b'')
        self.assertEqual(bytes(op.unpack(b'\x47')), b'')
        self.assertEqual(bytes(op.unpack(b'\x47\xB2')), b'')
        result = b'\x47\x02\xAB\x0C'
        self.assertEqual(bytes(op.unpack(b'\x47\xB2\xCA')), result)
        self.assertEqual(bytes(op.unpack(b'\x47\xB2\xCA\xB8')), result)
        self.assertEqual(bytes(op.unpack(b'\x47\xB2\xCA\xB8\xDF')), result)
        self.assertEqual(bytes(op.unpack(b'\x47\xB2\xCA\xB8\xDF\x35')), result + b'\xB8\x0F\x5D\x03')

# TODO: unpack_little_endian


################################################################################
# Array serialisation

# TODO: tests
