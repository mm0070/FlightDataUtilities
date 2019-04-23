import unittest

import numpy as np

from numpy.ma.testutils import assert_array_equal

from flightdatautilities.array import (
    contract_runs,
    first_valid_sample,
    Interpolator,
    is_constant,
    is_constant_uint8,
    is_constant_uint16,
    last_valid_sample,
    max_values,
    nearest_idx,
    nearest_slice,
    remove_small_runs,
    repair_mask,
    runs_of_ones,
    section_overlap,
    slices_to_array,
)
from flightdatautilities import masked_array_testutils as ma_test


class TestContractRuns(unittest.TestCase):
    def test_contract_runs(self):
        def call(x, *args, **kwargs):
            return contract_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
        T, F = True, False
        self.assertEqual(call([], 1), [])
        self.assertEqual(call([F,F,F,F], 0), [F,F,F,F])
        self.assertEqual(call([T,T,T,T], 0), [T,T,T,T])
        self.assertEqual(call([F,F,F,F], 1), [F,F,F,F])
        self.assertEqual(call([F,F,F,T], 1), [F,F,F,F])
        self.assertEqual(call([F,F,T,T], 1), [F,F,F,F])
        self.assertEqual(call([F,T,T,T], 1), [F,F,T,F])
        self.assertEqual(call([F,T,T,T], 2), [F,F,F,F])
        self.assertEqual(call([T,T,T,T], 2), [F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 1), [F,F,T,F,F,F,F,F])


class TestFirstValidSample(unittest.TestCase):
    def test_first_valid_sample(self):
        data = np.arange(11, 15)
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (1, 12))
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=True)), (None, None))
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 2), (3, 14))
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 1), (1, 12))
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (None, None))
        self.assertEqual(first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (3, 14))


class TestInterpolator(unittest.TestCase):
    def test_interpolator(self):
        def interpolate(points, array, copy=True):
            if not isinstance(array, np.ndarray):
                array = np.array(array, dtype=np.float64)
            return np.asarray(Interpolator(points).interpolate(array, copy=copy)).tolist()

        # Must be at least two points.
        self.assertRaises(ValueError, Interpolator, [])
        self.assertRaises(ValueError, Interpolator, [(0, 1)])
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
        array = [101.2, 203.5, 312.4, 442.1, 582.4, 632.12, 785.2, 890.21, 904.64, 1000, 1024, 1200]
        # output exactly matches array_operations.extrap1d implementation.
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
        for x, y in zip(interpolate(points, array), expected):
            self.assertAlmostEqual(x, y, places=8)
        points = [(0, 10), (1, 20), (1.5, 40), (2.0, 400)]
        array = [0, 1, 1.5, 2.0]
        expected = [10, 20, 40, 400]
        self.assertEqual(interpolate(points, array), expected)
        # check results are the same with copy=False
        self.assertEqual(interpolate(points, array, copy=False), expected)


class TestIsConstant(unittest.TestCase):
    def test_is_constant(self):
        self.assertTrue(is_constant(np.empty(0, dtype=np.uint16)))
        self.assertTrue(is_constant(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(is_constant(np.zeros(10, dtype=np.uint16)))
        self.assertTrue(is_constant(np.zeros(10, dtype=np.uint32)))
        self.assertFalse(is_constant(np.arange(10, dtype=np.uint32)))


class TestIsConstantUint16(unittest.TestCase):
    def test_is_constant_uint16(self):
        self.assertTrue(is_constant_uint16(np.empty(0, dtype=np.uint16)))
        self.assertTrue(is_constant_uint16(np.zeros(1, dtype=np.uint16)))
        self.assertTrue(is_constant_uint16(np.zeros(10, dtype=np.uint16)))
        self.assertTrue(is_constant_uint16(np.ones(10, dtype=np.uint16)))
        self.assertFalse(is_constant_uint16(np.arange(10, dtype=np.uint16)))


class TestIsConstantUint8(unittest.TestCase):
    def test_is_constant_uint8(self):
        self.assertTrue(is_constant_uint8(np.empty(0, dtype=np.uint8)))
        self.assertTrue(is_constant_uint8(np.zeros(1, dtype=np.uint8)))
        self.assertTrue(is_constant_uint8(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(is_constant_uint8(np.ones(10, dtype=np.uint8)))
        self.assertFalse(is_constant_uint8(np.arange(10, dtype=np.uint8)))


class TestLastValidSample(unittest.TestCase):
    def test_last_valid_sample(self):
        data = np.arange(11, 15)
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (3, 14))
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=True)), (None, None))
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (1, 12))
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -3), (1, 12))
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (3, 14))
        self.assertEqual(last_valid_sample(np.ma.array(data, mask=[0,0,0,1])), (2, 13))


class TestMaxValues(unittest.TestCase):
    def test_max_values(self):
        self.assertEqual(list(max_values(np.ma.empty(0, dtype=np.float64), np.empty(0, dtype=np.bool))), [])
        self.assertEqual(list(max_values(np.ma.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(max_values(np.ma.zeros(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 0)])
        self.assertEqual(list(max_values(np.ma.ones(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(max_values(np.ma.ones(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 1)])
        array = np.ma.arange(10, dtype=np.float64)
        matching = np.zeros(10, dtype=np.bool)
        self.assertEqual(list(max_values(array, matching)), [])
        matching[0] = True
        self.assertEqual(list(max_values(array, matching)), [(0, 0)])
        matching[1] = True
        self.assertEqual(list(max_values(array, matching)), [(1, 1)])
        matching[3] = True
        self.assertEqual(list(max_values(array, matching)), [(1, 1), (3, 3)])
        matching[7:] = True
        self.assertEqual(list(max_values(array, matching)), [(1, 1), (3, 3), (9, 9)])
        array[1] = np.ma.masked
        self.assertEqual(list(max_values(array, matching)), [(0, 0), (3, 3), (9, 9)])
        array[0] = np.ma.masked
        self.assertEqual(list(max_values(array, matching)), [(3, 3), (9, 9)])


class TestNearestIdx(unittest.TestCase):

    def test_nearest_idx(self):
        self.assertEqual(nearest_idx(np.empty(0, dtype=np.bool), 0), None)
        self.assertEqual(nearest_idx(np.array([False], dtype=np.bool), 0), None)
        self.assertEqual(nearest_idx(np.array([True], dtype=np.bool), 0), 0)
        array = np.zeros(5, dtype=np.bool)
        self.assertEqual(nearest_idx(array, 0), None)
        self.assertEqual(nearest_idx(array, 3), None)
        self.assertEqual(nearest_idx(array, -2), None)
        self.assertEqual(nearest_idx(array, 5), None)
        array = np.ones(5, dtype=np.bool)
        self.assertEqual(nearest_idx(array, 0), 0)
        self.assertEqual(nearest_idx(array, 3), 3)
        self.assertEqual(nearest_idx(array, -2), 0)
        self.assertEqual(nearest_idx(array, 5), 4)
        self.assertEqual(nearest_idx(array, 0, start_idx=2), None)
        self.assertEqual(nearest_idx(array, 4, start_idx=2), 4)
        self.assertEqual(nearest_idx(array, 4, stop_idx=2), None)
        self.assertEqual(nearest_idx(array, 1, stop_idx=2), 1)
        self.assertEqual(nearest_idx(array, 1, start_idx=0, stop_idx=2), 1)
        self.assertEqual(nearest_idx(array, 2, start_idx=0, stop_idx=2), None)
        array = np.array([True, False, False, False, False])
        self.assertEqual(nearest_idx(array, 3), 0)
        array = np.array([False, False, False, False, True])
        self.assertEqual(nearest_idx(array, 1), 4)
        array = np.array([False, True, True, False, False])
        self.assertEqual(nearest_idx(array, 3), 2)


class TestNearestSlice(unittest.TestCase):

    def test_nearest_slice(self):
        self.assertEqual(nearest_slice(np.empty(0, dtype=np.bool), 1), None)
        array = np.zeros(5, dtype=np.bool)
        self.assertEqual(nearest_slice(array, 2), None)
        self.assertEqual(nearest_slice(array, -1), None)
        self.assertEqual(nearest_slice(array, 8), None)
        array = np.array([False, False, False, False, True])
        self.assertEqual(nearest_slice(array, 2), slice(4, 5))
        self.assertEqual(nearest_slice(array, 5), slice(4, 5))
        self.assertEqual(nearest_slice(array, 8), slice(4, 5))
        self.assertEqual(nearest_slice(array, -2), slice(4, 5))
        array = np.array([True, True, False, False, False])
        self.assertEqual(nearest_slice(array, 0), slice(0, 2))
        self.assertEqual(nearest_slice(array, 2), slice(0, 2))
        self.assertEqual(nearest_slice(array, 5), slice(0, 2))
        self.assertEqual(nearest_slice(array, 8), slice(0, 2))
        self.assertEqual(nearest_slice(array, -2), slice(0, 2))
        array = np.array([False, True, True, False, False, True, False, False])
        for idx, sl in [(0, slice(1, 3)), (1, slice(1, 3)), (2, slice(1, 3)), (3, slice(1, 3)),
                        (4, slice(5, 6)), (5, slice(5, 6)), (6, slice(5, 6)), (7, slice(5, 6))]:
            self.assertEqual(nearest_slice(array, idx), sl)


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
        self.assertEqual(repair_mask(self.basic_data,
                                     method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, None, None])
        self.assertEqual(repair_mask(self.basic_data, extrapolate=True,
                                     method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, 30, 30])

    def test_repair_mask_basic_1(self):
        array = np.ma.arange(10)
        array[3] = np.ma.masked
        self.assertTrue(np.ma.is_masked(array[3]))
        array[6:8] = np.ma.masked
        res = repair_mask(array)
        np.testing.assert_array_equal(res.data,range(10))
        # test mask is now unmasked
        self.assertFalse(np.any(res.mask[3:9]))

    def test_repair_mask_too_much_invalid(self):
        array = np.ma.arange(20)
        array[4:15] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(array), array)

    def test_repair_mask_not_at_start(self):
        array = np.ma.arange(10)
        array[0] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(array), array)

    def test_repair_mask_not_at_end(self):
        array = np.ma.arange(10)
        array[9] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(array), array)

    def test_repair_mask_short_sample(self):
        # Very short samples were at one time returned as None, but simply
        # applying the normal "rules" seems more consistent, so this is a
        # test to show that an old function no longer applies.
        array = np.ma.arange(2)
        array[1] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(repair_mask(array), array)

    def test_repair_mask_extrapolate(self):
        array = np.ma.array([2,4,6,7,5,3,1],mask=[1,1,0,0,1,1,1])
        res = repair_mask(array, extrapolate=True)
        expected = np.ma.array([6,6,6,7,7,7,7], mask=False)
        assert_array_equal(res, expected)

    def test_repair_mask_fully_masked_array(self):
        array = np.ma.array(np.arange(10), mask=[1]*10)
        # fully masked raises ValueError
        self.assertRaises(ValueError, repair_mask, array)
        # fully masked returns a masked zero array
        res = repair_mask(array, raise_entirely_masked=False)
        assert_array_equal(res.data, array.data)
        assert_array_equal(res.mask, True)

    @unittest.skip('repair_above has not yet been carried over from analysis_engine.library version')
    def test_repair_mask_above(self):
        array = np.ma.arange(10)
        array[5] = np.ma.masked
        array[7:9] = np.ma.masked
        res = repair_mask(array, repair_above=5)
        np.testing.assert_array_equal(res.data, range(10))
        mask = np.ma.getmaskarray(array)
        # test only array[5] is still masked as is the first
        self.assertFalse(mask[4])
        self.assertTrue(mask[5])
        self.assertFalse(np.any(mask[6:]))


class TestRemoveSmallRuns(unittest.TestCase):
    def test_remove_small_runs(self):
        def call(x, *args, **kwargs):
            return remove_small_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
        T, F = True, False
        self.assertEqual(call([]), [])
        self.assertEqual(call([F,T,F], 0), [F,T,F])
        self.assertEqual(call([F,T,F], 1), [F,F,F])
        self.assertEqual(call([T,T,F], 1), [T,T,F])
        self.assertEqual(call([T,T,F], 2), [F,F,F])
        self.assertEqual(call([T,T,F], 1, 2), [F,F,F])
        self.assertEqual(call([T,T,T], 1), [T,T,T])
        self.assertEqual(call([T,T,T], 3), [F,F,F])
        self.assertEqual(call([T,T,T], 1, 4), [F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T], 2), [F,T,T,T,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 2), [F,T,T,T,F,F,F,F])
        self.assertEqual(call([F,T,T,T,F,T,T,F], 2, 2), [F,F,F,F,F,F,F,F])


class TestRunsOfOnes(unittest.TestCase):
    def test_runs_of_ones(self):
        array = np.ma.array(
            [0,0,1,0,1,1,1,1,1,0,0,1,1,1,0,1,1,1],
            mask=np.concatenate([np.zeros(14, dtype=np.bool), np.ones(4, dtype=np.bool)]),
            dtype=np.bool,
        )
        self.assertEqual(list(runs_of_ones(array)), [slice(2, 3), slice(4, 9), slice(11, 14), slice(15, 18)])
        self.assertEqual(list(runs_of_ones(array, min_samples=2)), [slice(4, 9), slice(11, 14), slice(15, 18)])
        self.assertEqual(list(runs_of_ones(array, min_samples=3)), [slice(4, 9)])


class TestSectionOverlap(unittest.TestCase):
    def test_section_overlap(self):
        def call(x, y):
            return section_overlap(np.array(x, dtype=np.bool),
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
        self.assertEqual(slices_to_array(0, []).tolist(), [])
        self.assertEqual(slices_to_array(0, [slice(0, 1)]).tolist(), [])
        self.assertEqual(slices_to_array(1, []).tolist(), [False])
        self.assertEqual(slices_to_array(1, [slice(0, 1)]).tolist(), [True])
        self.assertEqual(slices_to_array(5, []).tolist(), [False] * 5)
        self.assertEqual(slices_to_array(5, [slice(None, None)]).tolist(), [True] * 5)
        self.assertEqual(slices_to_array(5, [slice(-1, 6)]).tolist(), [True] * 5)
        self.assertEqual(slices_to_array(5, [slice(None, 3)]).tolist(), [1, 1, 1, 0, 0])
        self.assertEqual(slices_to_array(5, [slice(3, None)]).tolist(), [0, 0, 0, 1, 1])
        self.assertEqual(slices_to_array(5, [slice(4, 3)]).tolist(), [False] * 5)
        self.assertEqual(slices_to_array(5, [slice(1, 2), slice(3, 5)]).tolist(), [0, 1, 0, 1, 1])

