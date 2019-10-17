# cython: language_level=3, boundscheck=False
import unittest

import numpy as np

from flightdatautilities.array cimport cython as cy
from flightdatautilities.type import is_memoryview

"""
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
        self.assertFalse(array.entirely_masked(data))
        data.mask = True
        self.assertTrue(array.entirely_masked(data))
        def call(x):
            data = np.ma.empty(len(x))
            data.mask = x
            return array.entirely_masked(data)
        self.assertTrue(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestEntirelyUnmasked(unittest.TestCase):
    def test_entirely_unmasked(self):
        data = np.ma.arange(5)
        self.assertTrue(array.entirely_unmasked(data))
        data.mask = True
        self.assertFalse(array.entirely_unmasked(data))
        def call(x):
            data = np.ma.empty(len(x))
            data.mask = x
            return array.entirely_unmasked(data)
        self.assertTrue(call([]))
        self.assertFalse(call([True]))
        self.assertTrue(call([False]))
        self.assertFalse(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestFirstValidSample(unittest.TestCase):
    def test_first_valid_sample(self):
        data = np.arange(11, 15)
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (1, 12))
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=True)), (None, None))
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 2), (3, 14))
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 1), (1, 12))
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (None, None))
        self.assertEqual(array.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (3, 14))


class TestInterpolator(unittest.TestCase):
    def test_interpolator(self):
        def interpolate(points, data, copy=True):
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=np.float64)
            return np.asarray(array.Interpolator(points).interpolate(data, copy=copy)).tolist()

        # Must be at least two points.
        self.assertRaises(ValueError, array.Interpolator, [])
        self.assertRaises(ValueError, array.Interpolator, [(0, 1)])
        points = [(0, 1), (1, 2)]
        self.assertEqual(interpolate(points, [0, 1]), [1, 2])
        points = [(0, 1), (1, 2), (2, 3)]
        self.assertEqual(interpolate(points, [0]), [1])
        self.assertEqual(interpolate(points, [2]), [3])
        self.assertEqual(interpolate(points, [0, 1, 2]), [1, 2, 3])
        self.assertEqual(interpolate(points, [1.5]), [2.5])
        self.assertEqual(interpolate(points, [-1, 0, 1, 2, 3]), [0, 1, 2, 3, 4])
        self.assertEqual(interpolate(points, [131.3]), [132.3])
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
        for x, y in zip(interpolate(points, data), expected):
            self.assertAlmostEqual(x, y, places=8)
        points = [(0, 10), (1, 20), (1.5, 40), (2.0, 400)]
        data = [0, 1, 1.5, 2.0]
        expected = [10, 20, 40, 400]
        self.assertEqual(interpolate(points, data), expected)
        # check results are the same with copy=False
        self.assertEqual(interpolate(points, data, copy=False), expected)


class TestIsConstant(unittest.TestCase):
    def test_is_constant(self):
        self.assertTrue(array.is_constant(np.empty(0, dtype=np.uint16)))
        self.assertTrue(array.is_constant(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(array.is_constant(np.zeros(10, dtype=np.uint16)))
        self.assertTrue(array.is_constant(np.zeros(10, dtype=np.uint32)))
        self.assertFalse(array.is_constant(np.arange(10, dtype=np.uint32)))


class TestIsConstantUint16(unittest.TestCase):
    def test_is_constant_uint16(self):
        self.assertTrue(array.is_constant_uint16(np.empty(0, dtype=np.uint16)))
        self.assertTrue(array.is_constant_uint16(np.zeros(1, dtype=np.uint16)))
        self.assertTrue(array.is_constant_uint16(np.zeros(10, dtype=np.uint16)))
        self.assertTrue(array.is_constant_uint16(np.ones(10, dtype=np.uint16)))
        self.assertFalse(array.is_constant_uint16(np.arange(10, dtype=np.uint16)))


class TestIsConstantUint8(unittest.TestCase):
    def test_is_constant_uint8(self):
        self.assertTrue(array.is_constant_uint8(np.empty(0, dtype=np.uint8)))
        self.assertTrue(array.is_constant_uint8(np.zeros(1, dtype=np.uint8)))
        self.assertTrue(array.is_constant_uint8(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(array.is_constant_uint8(np.ones(10, dtype=np.uint8)))
        self.assertFalse(array.is_constant_uint8(np.arange(10, dtype=np.uint8)))


class TestIsPower2(unittest.TestCase):
    def test_is_power2(self):
        self.assertEqual([i for i in range(2000) if array.is_power2(i)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(array.is_power2(-2))
        self.assertFalse(array.is_power2(2.2))


class TestIsPower2Fraction(unittest.TestCase):
    def test_is_power2_fraction(self):
        self.assertEqual([i for i in range(2000) if array.is_power2_fraction(i)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.assertFalse(array.is_power2_fraction(-2))
        self.assertFalse(array.is_power2_fraction(2.2))
        self.assertTrue(array.is_power2_fraction(0.5))
        self.assertTrue(array.is_power2_fraction(0.25))
        self.assertTrue(array.is_power2_fraction(0.125))
        self.assertTrue(array.is_power2_fraction(0.0625))
        self.assertTrue(array.is_power2_fraction(0.03125))
        self.assertTrue(array.is_power2_fraction(0.015625))
        self.assertFalse(array.is_power2_fraction(0.75))
        self.assertFalse(array.is_power2_fraction(0.2))
        self.assertFalse(array.is_power2_fraction(0.015626))


class TestLastValidSample(unittest.TestCase):
    def test_last_valid_sample(self):
        data = np.arange(11, 15)
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (3, 14))
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=True)), (None, None))
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (1, 12))
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -3), (1, 12))
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (3, 14))
        self.assertEqual(array.last_valid_sample(np.ma.array(data, mask=[0,0,0,1])), (2, 13))


class TestMaxValues(unittest.TestCase):
    def test_max_values(self):
        self.assertEqual(list(array.max_values(np.ma.empty(0, dtype=np.float64), np.empty(0, dtype=np.bool))), [])
        self.assertEqual(list(array.max_values(np.ma.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(array.max_values(np.ma.zeros(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 0)])
        self.assertEqual(list(array.max_values(np.ma.ones(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(array.max_values(np.ma.ones(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 1)])
        arr = np.ma.arange(10, dtype=np.float64)
        matching = np.zeros(10, dtype=np.bool)
        self.assertEqual(list(array.max_values(arr, matching)), [])
        matching[0] = True
        self.assertEqual(list(array.max_values(arr, matching)), [(0, 0)])
        matching[1] = True
        self.assertEqual(list(array.max_values(arr, matching)), [(1, 1)])
        matching[3] = True
        self.assertEqual(list(array.max_values(arr, matching)), [(1, 1), (3, 3)])
        matching[7:] = True
        self.assertEqual(list(array.max_values(arr, matching)), [(1, 1), (3, 3), (9, 9)])
        arr[1] = np.ma.masked
        self.assertEqual(list(array.max_values(arr, matching)), [(0, 0), (3, 3), (9, 9)])
        arr[0] = np.ma.masked
        self.assertEqual(list(array.max_values(arr, matching)), [(3, 3), (9, 9)])


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
        self.assertEqual(array.nearest_slice(np.empty(0, dtype=np.bool), 1), None)
        data = np.zeros(5, dtype=np.bool)
        self.assertEqual(array.nearest_slice(data, 2), None)
        self.assertEqual(array.nearest_slice(data, -1), None)
        self.assertEqual(array.nearest_slice(data, 8), None)
        data = np.array([False, False, False, False, True])
        self.assertEqual(array.nearest_slice(data, 2), slice(4, 5))
        self.assertEqual(array.nearest_slice(data, 5), slice(4, 5))
        self.assertEqual(array.nearest_slice(data, 8), slice(4, 5))
        self.assertEqual(array.nearest_slice(data, -2), slice(4, 5))
        data = np.array([True, True, False, False, False])
        self.assertEqual(array.nearest_slice(data, 0), slice(0, 2))
        self.assertEqual(array.nearest_slice(data, 2), slice(0, 2))
        self.assertEqual(array.nearest_slice(data, 5), slice(0, 2))
        self.assertEqual(array.nearest_slice(data, 8), slice(0, 2))
        self.assertEqual(array.nearest_slice(data, -2), slice(0, 2))
        data = np.array([False, True, True, False, False, True, False, False])
        for idx, sl in [(0, slice(1, 3)), (1, slice(1, 3)), (2, slice(1, 3)), (3, slice(1, 3)),
                        (4, slice(5, 6)), (5, slice(5, 6)), (6, slice(5, 6)), (7, slice(5, 6))]:
            self.assertEqual(array.nearest_slice(data, idx), sl)


class TestRepairMask(unittest.TestCase):
    def setUp(self):
        self.basic_data = np.ma.array(
            [0, 0, 10, 0, 0, 20, 23, 26, 30, 0, 0],
            mask=[1,1,0,1,1,0,0,0,0,1,1])

    def test_repair_mask_basic_fill_start(self):
        self.assertEqual(repair_mask(self.basic_data,
                                           method='fill_start').tolist(),
                         [None, None, 10, 10, 10, 20, 23, 26, 30, 30, 30])
        self.assertEqual(repair_mask(self.basic_data, extrapolate=True,
                                           method='fill_start').tolist(),
                         [10, 10, 10, 10, 10, 20, 23, 26, 30, 30, 30])

    def test_repair_mask_basic_fill_stop(self):
        self.assertEqual(repair_mask(self.basic_data, method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, None, None])
        self.assertEqual(repair_mask(self.basic_data, extrapolate=True, method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, 30, 30])

    def test_repair_mask_basic_1(self):
        data = np.ma.arange(10)
        data[3] = np.ma.masked
        data[6:8] = np.ma.masked
        res = repair_mask(data)
        np.testing.assert_array_equal(res.data,range(10))
        # test mask is now unmasked
        self.assertFalse(np.any(res.mask[3:9]))

    def test_repair_mask_too_much_invalid(self):
        data = np.ma.arange(20)
        data[4:15] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    def test_repair_mask_not_at_start(self):
        data = np.ma.arange(10)
        data[0] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    def test_repair_mask_not_at_end(self):
        data = np.ma.arange(10)
        data[9] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    def test_repair_mask_short_sample(self):
        # Very short samples were at one time returned as None, but simply
        # applying the normal "rules" seems more consistent, so this is a
        # test to show that an old function no longer applies.
        data = np.ma.arange(2)
        data[1] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    def test_repair_mask_extrapolate(self):
        data = np.ma.array([2,4,6,7,5,3,1], mask=[1,1,0,0,1,1,1])
        res = repair_mask(data, extrapolate=True)
        expected = np.ma.array([6,6,6,7,7,7,7], mask=False)
        assert_array_equal(res, expected)

    def test_repair_mask_fully_masked_array(self):
        data = np.ma.array(np.arange(10), mask=[1]*10)
        # fully masked raises ValueError
        self.assertRaises(ValueError, repair_mask, data)
        # fully masked returns a masked zero array
        res = repair_mask(data, raise_entirely_masked=False)
        assert_array_equal(res.data, data.data)
        assert_array_equal(res.mask, True)

    #@unittest.skip('repair_above has not yet been carried over from analysis_engine.library version')
    #def test_repair_mask_above(self):
        #data = np.ma.arange(10)
        #data[5] = np.ma.masked
        #data[7:9] = np.ma.masked
        #res = repair_mask(data, repair_above=5)
        #np.testing.assert_array_equal(res.data, range(10))
        #mask = np.ma.getmaskarray(data)
        ## test only array[5] is still masked as is the first
        #self.assertFalse(mask[4])
        #self.assertTrue(mask[5])
        #self.assertFalse(np.any(mask[6:]))


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
            return array.section_overlap(np.array(x, dtype=np.bool),
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
        self.assertEqual(array.slices_to_array(0, []).tolist(), [])
        self.assertEqual(array.slices_to_array(0, [slice(0, 1)]).tolist(), [])
        self.assertEqual(array.slices_to_array(1, []).tolist(), [False])
        self.assertEqual(array.slices_to_array(1, [slice(0, 1)]).tolist(), [True])
        self.assertEqual(array.slices_to_array(5, []).tolist(), [False] * 5)
        self.assertEqual(array.slices_to_array(5, [slice(None, None)]).tolist(), [True] * 5)
        self.assertEqual(array.slices_to_array(5, [slice(-1, 6)]).tolist(), [True] * 5)
        self.assertEqual(array.slices_to_array(5, [slice(None, 3)]).tolist(), [1, 1, 1, 0, 0])
        self.assertEqual(array.slices_to_array(5, [slice(3, None)]).tolist(), [0, 0, 0, 1, 1])
        self.assertEqual(array.slices_to_array(5, [slice(4, 3)]).tolist(), [False] * 5)
        self.assertEqual(array.slices_to_array(5, [slice(1, 2), slice(3, 5)]).tolist(), [0, 1, 0, 1, 1])


class TestKeyValue(unittest.TestCase):
    def test_key_value(self):
        data = np.fromstring(b'***\x0ATAILNUM=G-FDSL\x0ASERIALNUM=10344\x0A***', dtype=np.uint8)
        delimiter = b'='
        separator = b'\x0A'
        self.assertEqual(array.key_value(data, 'TAILNUM', delimiter, separator), b'G-FDSL')
        self.assertEqual(array.key_value(data, 'SERIALNUM', delimiter, separator), b'10344')


class TestSwapBytes(unittest.TestCase):
    def test_swap_bytes(self):
        arr = np.ones(0, dtype=np.uint16)
        self.assertEqual(len(array.swap_bytes(arr)), 0)
        data = b'\xAF'
        arr = np.fromstring(data, dtype=np.uint8)
        self.assertEqual(array.swap_bytes(arr).tostring(), data)
        data = b'\x12\xAB\xCD\xEF'
        arr = np.fromstring(data, dtype=np.uint8)
        self.assertEqual(array.swap_bytes(arr).tostring(), data)
        arr = np.fromstring(data, dtype=np.uint16)
        self.assertEqual(array.swap_bytes(arr).tostring(), b'\xAB\x12\xEF\xCD')


class TestPack(unittest.TestCase):
    def test_pack(self):
        self.assertEqual(
            array.pack(np.fromstring(b'\x47\x02\xAB\x0C', dtype=np.uint8)).tostring(),
            np.fromstring(b'\x47\xB2\xCA', dtype=np.uint8).tostring())


class TestUnpack(unittest.TestCase):
    def test_unpack(self):
        self.assertEqual(
            array.unpack(np.fromstring(b'\x47\xB2\xCA', dtype=np.uint8)).tostring(),
            np.fromstring(b'\x47\x02\xAB\x0C', dtype=np.uint8).tostring())


class TestUnpackLittleEndian(unittest.TestCase):
    def test_unpack_little_endian(self):
        data = np.frombuffer(b'\x24\x70\x5C\x12\x34\x56', dtype=np.uint8).copy()
        self.assertEqual(hexlify(np.asarray(array.unpack_little_endian(data)).tostring()), b'47025c0023015604')


class TestArrayIndexUint16(unittest.TestCase):
    def test_array_index_uint16(self):
        self.assertEqual(array.array_index_uint16(10, np.empty(0, dtype=np.uint16)), -1)
        self.assertEqual(array.array_index_uint16(10, np.array([2,4,6,8], dtype=np.uint16)), -1)
        self.assertEqual(array.array_index_uint16(10, np.array([10], dtype=np.uint16)), 0)
        self.assertEqual(array.array_index_uint16(10, np.array([2,4,6,8,10], dtype=np.uint16)), 4)


class TestIndexOfSubarray(unittest.TestCase):
    def test_index_of_subarray(self):
        arr = np.zeros(16, dtype=np.uint8)
        subarr = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr), -1)
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr, start=5), -1)
        arr[0] = 1
        arr[1] = 2
        arr[2] = 3
        arr[3] = 4
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr), 0)
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr, start=1), -1)
        arr[1] = 5
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr), -1)
        arr[12] = 1
        arr[13] = 2
        arr[14] = 3
        arr[15] = 4
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr), 12)
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr, start=10), 12)
        self.assertEqual(array.index_of_subarray_uint8(arr, subarr, start=14), -1)
        self.assertEqual(array.index_of_subarray_uint8(subarr, arr), -1)
        self.assertEqual(array.index_of_subarray_uint8(subarr, arr, start=10000), -1)
"""

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
        self.assertEqual(cy.none_idx(None), -1)


class TestIdxNone(unittest.TestCase):
    def test_idx_none(self):
        self.assertEqual(cy.idx_none(0), 0)
        self.assertEqual(cy.idx_none(2), 2)
        self.assertEqual(cy.idx_none(-1), None)


class TestGetmaskarray1d(unittest.TestCase):
    def test_getmaskarray1d(self):
        array = np.ma.empty(3)
        mask = np.asarray(cy.getmaskarray1d(array))
        self.assertEqual(mask.dtype, np.dtype('uint8'))
        self.assertEqual(list(cy.getmaskarray1d(array)), [0, 0, 0])
        array[1] = np.ma.masked
        self.assertEqual(list(cy.getmaskarray1d(array)), [0, 1, 0])


"""
class TestLongestSectionUint8(unittest.TestCase):
    def test_longest_section_uint8(self):
        self.assertEqual(array.longest_section_uint8(np.empty(0, dtype=np.uint8)), 0)
        data = np.zeros(10, dtype=np.uint8)
        self.assertEqual(array.longest_section_uint8(data), 10)
        self.assertEqual(array.longest_section_uint8(data, 0), 10)
        self.assertEqual(array.longest_section_uint8(data, 1), 0)
        data[0] = 1
        self.assertEqual(array.longest_section_uint8(data), 9)
        self.assertEqual(array.longest_section_uint8(data, 1), 1)
        data[9] = 1
        self.assertEqual(array.longest_section_uint8(data), 8)
        self.assertEqual(array.longest_section_uint8(data, 1), 1)
        data[2:4] = 2
        self.assertEqual(array.longest_section_uint8(data), 5)
        self.assertEqual(array.longest_section_uint8(data, 1), 1)
        self.assertEqual(array.longest_section_uint8(data, 2), 2)
        data[:] = 2
        self.assertEqual(array.longest_section_uint8(data), 0)
        self.assertEqual(array.longest_section_uint8(data, 1), 0)
        self.assertEqual(array.longest_section_uint8(data, 2), 10)
"""