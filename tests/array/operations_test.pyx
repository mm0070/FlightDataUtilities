# cython: language_level=3, boundscheck=False
from binascii import hexlify
import os
import unittest

cimport cython
import numpy as np
cimport numpy as np
from numpy.ma.testutils import assert_array_equal

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.array cimport cython as cy, operations as op
from flightdatautilities.array.operations import contract_runs, nearest_idx, remove_small_runs, runs_of_ones
from flightdatautilities.read import reader


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


class TestAllArray(unittest.TestCase):
    def test_all_array(self):
        def call(x):
            return op.all_array(np.array(x))
        self.assertTrue(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestAnyArray(unittest.TestCase):
    def test_any_array(self):
        def call(x):
            return op.any_array(np.array(x))
        self.assertFalse(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertTrue(call([True, False]))
        self.assertTrue(call([False, True]))


class TestContractRuns(unittest.TestCase):
    def test_contract_runs(self):
        def call(x, *args, **kwargs):
            return contract_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
        T, F = True, False
        self.assertEqual(call([], 1), [])
        self.assertEqual(call([F,F,F,F], 0), [F,F,F,F])
        self.assertEqual(call([T,T,T,T], 0), [T,T,T,T])
        self.assertEqual(call([F,F,F,F], 1), [F,F,F,F])
        self.assertEqual(call([T,T,T,F], 1, match=False), [T,T,T,T])
        self.assertEqual(call([F,F,T,T], 1), [F,F,F,F])
        self.assertEqual(call([F,T,T,T], 1), [F,F,T,F])
        self.assertEqual(call([F,T,T,T], 2), [F,F,F,F])
        self.assertEqual(call([T,T,T,T], 2), [F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 1), [F,F,T,F,F,F,F,F])


class TestEntirelyMasked(unittest.TestCase):
    def test_entirely_masked(self):
        data = np.ma.arange(5)
        self.assertFalse(op.entirely_masked(data))
        data.mask = True
        self.assertTrue(op.entirely_masked(data))
        def call(x):
            data = np.ma.empty(len(x))
            data.mask = x
            return op.entirely_masked(data)
        self.assertTrue(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestEntirelyUnmasked(unittest.TestCase):
    def test_entirely_unmasked(self):
        data = np.ma.arange(5)
        self.assertTrue(op.entirely_unmasked(data))
        data.mask = True
        self.assertFalse(op.entirely_unmasked(data))
        def call(x):
            data = np.ma.empty(len(x))
            data.mask = x
            return op.entirely_unmasked(data)
        self.assertTrue(call([]))
        self.assertFalse(call([True]))
        self.assertTrue(call([False]))
        self.assertFalse(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestIsConstant(unittest.TestCase):
    def test_is_constant(self):
        self.assertTrue(op.is_constant[np.uint16_t](cy.empty_uint16(0)))
        self.assertTrue(op.is_constant[np.uint8_t](cy.zeros_uint8(10)))
        self.assertTrue(op.is_constant[np.uint16_t](cy.zeros_uint16(10)))
        self.assertTrue(op.is_constant[np.uint32_t](cy.zeros_uint32(10)))
        self.assertTrue(op.is_constant[np.uint8_t](cy.ones_uint8(10)))
        self.assertFalse(op.is_constant[np.uint32_t](np.arange(10, dtype=np.uint32)))
        self.assertFalse(op.is_constant[np.float64_t](np.arange(10, dtype=np.float64)))


class TestIsPower2(unittest.TestCase):
    def test_is_power2(self):
        self.assertEqual([i for i in range(2000) if op.is_power2(i)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(op.is_power2(-2))
        self.assertFalse(op.is_power2(2.2))


class TestIsPower2Fraction(unittest.TestCase):
    def test_is_power2_fraction(self):
        self.assertEqual([i for i in range(2000) if op.is_power2_fraction(i)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(op.is_power2_fraction(-2))
        self.assertFalse(op.is_power2_fraction(2.2))
        self.assertTrue(op.is_power2_fraction(0.5))
        self.assertTrue(op.is_power2_fraction(0.25))
        self.assertTrue(op.is_power2_fraction(0.125))
        self.assertTrue(op.is_power2_fraction(0.0625))
        self.assertTrue(op.is_power2_fraction(0.03125))
        self.assertTrue(op.is_power2_fraction(0.015625))
        self.assertFalse(op.is_power2_fraction(0.75))
        self.assertFalse(op.is_power2_fraction(0.2))
        self.assertFalse(op.is_power2_fraction(0.015626))


class TestMaxValues(unittest.TestCase):
    def test_max_values(self):
        self.assertEqual(list(op.max_values(np.ma.empty(0, dtype=np.float64), np.empty(0, dtype=np.bool))), [])
        self.assertEqual(list(op.max_values(np.ma.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(op.max_values(np.ma.zeros(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 0)])
        self.assertEqual(list(op.max_values(np.ma.ones(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(op.max_values(np.ma.ones(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 1)])
        arr = np.ma.arange(10, dtype=np.float64)
        matching = np.zeros(10, dtype=np.bool)
        self.assertEqual(list(op.max_values(arr, matching)), [])
        matching[0] = True
        self.assertEqual(list(op.max_values(arr, matching)), [(0, 0)])
        matching[1] = True
        self.assertEqual(list(op.max_values(arr, matching)), [(1, 1)])
        matching[3] = True
        self.assertEqual(list(op.max_values(arr, matching)), [(1, 1), (3, 3)])
        matching[7:] = True
        self.assertEqual(list(op.max_values(arr, matching)), [(1, 1), (3, 3), (9, 9)])
        arr[1] = np.ma.masked
        self.assertEqual(list(op.max_values(arr, matching)), [(0, 0), (3, 3), (9, 9)])
        arr[0] = np.ma.masked
        self.assertEqual(list(op.max_values(arr, matching)), [(3, 3), (9, 9)])


class TestNearestIdx(unittest.TestCase):

    def test_nearest_idx(self):
        self.assertEqual(nearest_idx(np.empty(0, dtype=np.bool), 0), None)
        self.assertEqual(nearest_idx(np.array([False], dtype=np.bool), 0), None)
        self.assertEqual(nearest_idx(np.array([True], dtype=np.bool), 0), 0)
        data = np.zeros(5, dtype=np.bool)
        self.assertEqual(nearest_idx(data, 0), None)
        self.assertEqual(nearest_idx(data, 3), None)
        self.assertEqual(nearest_idx(data, -2), None)
        self.assertEqual(nearest_idx(data, 5), None)
        data = np.ones(5, dtype=np.bool)
        self.assertEqual(nearest_idx(data, 0), 0)
        self.assertEqual(nearest_idx(data, 3), 3)
        self.assertEqual(nearest_idx(data, -2), 0)
        self.assertEqual(nearest_idx(data, 5), 4)
        self.assertEqual(nearest_idx(data, 0, start_idx=2), None)
        self.assertEqual(nearest_idx(data, 4, start_idx=2), 4)
        self.assertEqual(nearest_idx(data, 4, stop_idx=2), None)
        self.assertEqual(nearest_idx(data, 1, stop_idx=2), 1)
        self.assertEqual(nearest_idx(data, 1, start_idx=0, stop_idx=2), 1)
        self.assertEqual(nearest_idx(data, 2, start_idx=0, stop_idx=2), None)
        data = np.array([True, False, False, False, False])
        self.assertEqual(nearest_idx(data, 3), 0)
        data = np.array([False, False, False, False, True])
        self.assertEqual(nearest_idx(data, 1), 4)
        data = np.array([False, True, True, False, False])
        self.assertEqual(nearest_idx(data, 3), 2)


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


class TestKeyValue(unittest.TestCase):
    def test_key_value(self):
        data = b'***\x0ATAILNUM=G-FDSL\x0ASERIALNUM=10344\x0A***'
        delimiter = b'='
        separator = b'\x0A'
        self.assertEqual(op.key_value(data, b'TAILNUM', delimiter, separator), b'G-FDSL')
        self.assertEqual(op.key_value(data, b'SERIALNUM', delimiter, separator), b'10344')


class TestSwapBytes(unittest.TestCase):
    def test_swap_bytes(self):
        self.assertEqual(len(op.swap_bytes(np.ones(0, dtype=np.uint16))), 0)
        data = b'\xAF'
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint8).copy()).tostring(), data)
        data = b'\x12\xAB\xCD\xEF'
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint8).copy()).tostring(), data)
        self.assertEqual(op.swap_bytes(np.frombuffer(data, dtype=np.uint16).copy()).tostring(), b'\xAB\x12\xEF\xCD')


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


class TestUnpackLittleEndian(unittest.TestCase):
    def test_unpack_little_endian(self):
        self.assertEqual(hexlify(np.asarray(op.unpack_little_endian(b'\x24\x70\x5C\x12\x34\x56')).tostring()), b'47025c0023015604')


class TestArrayValueIdx(unittest.TestCase):
    def test_array_value_idx(self):
        self.assertEqual(op.array_value_idx[np.uint16_t](np.empty(0, dtype=np.uint16), 10), cy.NONE_IDX)
        self.assertEqual(op.array_value_idx[np.uint16_t](np.array([2,4,6,8], dtype=np.uint16), 10), cy.NONE_IDX)
        self.assertEqual(op.array_value_idx[np.uint16_t](np.array([10], dtype=np.uint16), 10), 0)
        self.assertEqual(op.array_value_idx[np.uint16_t](np.array([2,4,6,8,10], dtype=np.uint16), 10), 4)


class TestIndexOfSubarrayUint8(unittest.TestCase):
    def test_index_of_subarray_uint8(self):
        arr = np.zeros(16, dtype=np.uint8)
        subarr = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr), -1)
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr, start=5), -1)
        arr[0] = 1
        arr[1] = 2
        arr[2] = 3
        arr[3] = 4
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr), 0)
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr, start=1), -1)
        arr[1] = 5
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr), -1)
        arr[12] = 1
        arr[13] = 2
        arr[14] = 3
        arr[15] = 4
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr), 12)
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr, start=10), 12)
        self.assertEqual(op.index_of_subarray_uint8(arr, subarr, start=14), -1)
        self.assertEqual(op.index_of_subarray_uint8(subarr, arr), -1)
        self.assertEqual(op.index_of_subarray_uint8(subarr, arr, start=10000), -1)


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



class TestTwosComplement(unittest.TestCase):
    def test_twos_complement(self):
        self.assertEqual(op.twos_complement(np.arange(4), 2).tolist(), [0, 1, -2, -1])


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
