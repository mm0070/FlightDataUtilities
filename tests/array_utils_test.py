import numpy as np
import unittest

from numpy.ma.testutils import assert_array_equal

from flightdatautilities import array_utils as au
from flightdatautilities import masked_array_testutils as ma_test


class TestNearestSlice(unittest.TestCase):

    def test_nearest_slice(self):
        self.assertEqual(au.nearest_slice(np.empty(0, dtype=np.bool), 1), None)
        array = np.zeros(5, dtype=np.bool)
        self.assertEqual(au.nearest_slice(array, 2), None)
        self.assertEqual(au.nearest_slice(array, -1), None)
        self.assertEqual(au.nearest_slice(array, 8), None)
        array = np.array([False, False, False, False, True])
        self.assertEqual(au.nearest_slice(array, 2), slice(4, 5))
        self.assertEqual(au.nearest_slice(array, 5), slice(4, 5))
        self.assertEqual(au.nearest_slice(array, 8), slice(4, 5))
        self.assertEqual(au.nearest_slice(array, -2), slice(4, 5))
        array = np.array([True, True, False, False, False])
        self.assertEqual(au.nearest_slice(array, 0), slice(0, 2))
        self.assertEqual(au.nearest_slice(array, 2), slice(0, 2))
        self.assertEqual(au.nearest_slice(array, 5), slice(0, 2))
        self.assertEqual(au.nearest_slice(array, 8), slice(0, 2))
        self.assertEqual(au.nearest_slice(array, -2), slice(0, 2))
        array = np.array([False, True, True, False, False, True, False, False])
        for idx, sl in [(0, slice(1, 3)), (1, slice(1, 3)), (2, slice(1, 3)), (3, slice(1, 3)),
                        (4, slice(5, 6)), (5, slice(5, 6)), (6, slice(5, 6)), (7, slice(5, 6))]:
            self.assertEqual(au.nearest_slice(array, idx), sl)


class TestNearestIdx(unittest.TestCase):

    def test_nearest_idx(self):
        self.assertEqual(au.nearest_idx(np.empty(0, dtype=np.bool), 0), None)
        self.assertEqual(au.nearest_idx(np.array([False], dtype=np.bool), 0), None)
        self.assertEqual(au.nearest_idx(np.array([True], dtype=np.bool), 0), 0)
        array = np.zeros(5, dtype=np.bool)
        self.assertEqual(au.nearest_idx(array, 0), None)
        self.assertEqual(au.nearest_idx(array, 3), None)
        self.assertEqual(au.nearest_idx(array, -2), None)
        self.assertEqual(au.nearest_idx(array, 5), None)
        array = np.ones(5, dtype=np.bool)
        self.assertEqual(au.nearest_idx(array, 0), 0)
        self.assertEqual(au.nearest_idx(array, 3), 3)
        self.assertEqual(au.nearest_idx(array, -2), 0)
        self.assertEqual(au.nearest_idx(array, 5), 4)
        self.assertEqual(au.nearest_idx(array, 0, start_idx=2), None)
        self.assertEqual(au.nearest_idx(array, 4, start_idx=2), 4)
        self.assertEqual(au.nearest_idx(array, 4, stop_idx=2), None)
        self.assertEqual(au.nearest_idx(array, 1, stop_idx=2), 1)
        self.assertEqual(au.nearest_idx(array, 1, start_idx=0, stop_idx=2), 1)
        self.assertEqual(au.nearest_idx(array, 2, start_idx=0, stop_idx=2), None)
        array = np.array([True, False, False, False, False])
        self.assertEqual(au.nearest_idx(array, 3), 0)
        array = np.array([False, False, False, False, True])
        self.assertEqual(au.nearest_idx(array, 1), 4)
        array = np.array([False, True, True, False, False])
        self.assertEqual(au.nearest_idx(array, 3), 2)


class TestRepairMask(unittest.TestCase):
    def setUp(self):
        self.basic_data = np.ma.array(
            [0, 0, 10, 0, 0, 20, 23, 26, 30, 0, 0],
            mask=[1,1,0,1,1,0,0,0,0,1,1])

    def test_repair_mask_basic_fill_start(self):
        self.assertEqual(au.repair_mask(self.basic_data,
                                     method='fill_start').tolist(),
                         [None, None, 10, 10, 10, 20, 23, 26, 30, 30, 30])
        self.assertEqual(au.repair_mask(self.basic_data, extrapolate=True,
                                     method='fill_start').tolist(),
                         [10, 10, 10, 10, 10, 20, 23, 26, 30, 30, 30])

    def test_repair_mask_basic_fill_stop(self):
        self.assertEqual(au.repair_mask(self.basic_data,
                                     method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, None, None])
        self.assertEqual(au.repair_mask(self.basic_data, extrapolate=True,
                                     method='fill_stop').tolist(),
                         [10, 10, 10, 20, 20, 20, 23, 26, 30, 30, 30])

    def test_repair_mask_basic_1(self):
        array = np.ma.arange(10)
        array[3] = np.ma.masked
        self.assertTrue(np.ma.is_masked(array[3]))
        array[6:8] = np.ma.masked
        res = au.repair_mask(array)
        np.testing.assert_array_equal(res.data,range(10))
        # test mask is now unmasked
        self.assertFalse(np.any(res.mask[3:9]))

    def test_repair_mask_too_much_invalid(self):
        array = np.ma.arange(20)
        array[4:15] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(au.repair_mask(array), array)

    def test_repair_mask_not_at_start(self):
        array = np.ma.arange(10)
        array[0] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(au.repair_mask(array), array)

    def test_repair_mask_not_at_end(self):
        array = np.ma.arange(10)
        array[9] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(au.repair_mask(array), array)

    def test_repair_mask_short_sample(self):
        # Very short samples were at one time returned as None, but simply
        # applying the normal "rules" seems more consistent, so this is a
        # test to show that an old function no longer applies.
        array = np.ma.arange(2)
        array[1] = np.ma.masked
        ma_test.assert_masked_array_approx_equal(au.repair_mask(array), array)

    def test_repair_mask_extrapolate(self):
        array = np.ma.array([2,4,6,7,5,3,1],mask=[1,1,0,0,1,1,1])
        res = au.repair_mask(array, extrapolate=True)
        expected = np.ma.array([6,6,6,7,7,7,7], mask=False)
        assert_array_equal(res, expected)

    def test_repair_mask_fully_masked_array(self):
        array = np.ma.array(np.arange(10), mask=[1]*10)
        # fully masked raises ValueError
        self.assertRaises(ValueError, au.repair_mask, array)
        # fully masked returns a masked zero array
        res = au.repair_mask(array, raise_entirely_masked=False)
        assert_array_equal(res.data, array.data)
        assert_array_equal(res.mask, True)

    def test_repair_mask_above(self):
        array = np.ma.arange(10)
        array[5] = np.ma.masked
        array[7:9] = np.ma.masked
        res = au.repair_mask(array, repair_above=5)
        np.testing.assert_array_equal(res.data, range(10))
        mask = np.ma.getmaskarray(array)
        # test only array[5] is still masked as is the first
        self.assertFalse(mask[4])
        self.assertTrue(mask[5])
        self.assertFalse(np.any(mask[6:]))


class TestMaxValues(unittest.TestCase):
    def test_max_values(self):
        self.assertEqual(list(au.max_values(np.ma.empty(0, dtype=np.float64), np.empty(0, dtype=np.bool))), [])
        self.assertEqual(list(au.max_values(np.ma.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(au.max_values(np.ma.zeros(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 0)])
        self.assertEqual(list(au.max_values(np.ma.ones(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        self.assertEqual(list(au.max_values(np.ma.ones(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 1)])
        array = np.ma.arange(10, dtype=np.float64)
        matching = np.zeros(10, dtype=np.bool)
        self.assertEqual(list(au.max_values(array, matching)), [])
        matching[0] = True
        self.assertEqual(list(au.max_values(array, matching)), [(0, 0)])
        matching[1] = True
        self.assertEqual(list(au.max_values(array, matching)), [(1, 1)])
        matching[3] = True
        self.assertEqual(list(au.max_values(array, matching)), [(1, 1), (3, 3)])
        matching[7:] = True
        self.assertEqual(list(au.max_values(array, matching)), [(1, 1), (3, 3), (9, 9)])
        array[1] = np.ma.masked
        self.assertEqual(list(au.max_values(array, matching)), [(0, 0), (3, 3), (9, 9)])
        array[0] = np.ma.masked
        self.assertEqual(list(au.max_values(array, matching)), [(3, 3), (9, 9)])


class TestSlicesToArray(unittest.TestCase):
    def test_slices_to_array(self):
        self.assertEqual(au.slices_to_array(0, []).tolist(), [])
        self.assertEqual(au.slices_to_array(0, [slice(0, 1)]).tolist(), [])
        self.assertEqual(au.slices_to_array(1, []).tolist(), [False])
        self.assertEqual(au.slices_to_array(1, [slice(0, 1)]).tolist(), [True])
        self.assertEqual(au.slices_to_array(5, []).tolist(), [False] * 5)
        self.assertEqual(au.slices_to_array(5, [slice(None, None)]).tolist(), [True] * 5)
        self.assertEqual(au.slices_to_array(5, [slice(-1, 6)]).tolist(), [True] * 5)
        self.assertEqual(au.slices_to_array(5, [slice(None, 3)]).tolist(), [1, 1, 1, 0, 0])
        self.assertEqual(au.slices_to_array(5, [slice(3, None)]).tolist(), [0, 0, 0, 1, 1])
        self.assertEqual(au.slices_to_array(5, [slice(4, 3)]).tolist(), [False] * 5)
        self.assertEqual(au.slices_to_array(5, [slice(1, 2), slice(3, 5)]).tolist(), [0, 1, 0, 1, 1])


class TestIsConstant(unittest.TestCase):
    def test_is_constant(self):
        self.assertTrue(au.is_constant(np.empty(0, dtype=np.uint16)))
        self.assertTrue(au.is_constant(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(au.is_constant(np.zeros(10, dtype=np.uint16)))
        self.assertRaises(NotImplementedError, au.is_constant, np.zeros(10, dtype=np.uint32))


class TestIsConstantUint16(unittest.TestCase):
    def test_is_constant_uint16(self):
        self.assertTrue(au.is_constant_uint16(np.empty(0, dtype=np.uint16)))
        self.assertTrue(au.is_constant_uint16(np.zeros(1, dtype=np.uint16)))
        self.assertTrue(au.is_constant_uint16(np.zeros(10, dtype=np.uint16)))
        self.assertTrue(au.is_constant_uint16(np.ones(10, dtype=np.uint16)))
        self.assertFalse(au.is_constant_uint16(np.arange(10, dtype=np.uint16)))


class TestIsConstantUint8(unittest.TestCase):
    def test_is_constant_uint8(self):
        self.assertTrue(au.is_constant_uint8(np.empty(0, dtype=np.uint8)))
        self.assertTrue(au.is_constant_uint8(np.zeros(1, dtype=np.uint8)))
        self.assertTrue(au.is_constant_uint8(np.zeros(10, dtype=np.uint8)))
        self.assertTrue(au.is_constant_uint8(np.ones(10, dtype=np.uint8)))
        self.assertFalse(au.is_constant_uint8(np.arange(10, dtype=np.uint8)))


class TestRemoveSmallRuns(unittest.TestCase):
    def test_remove_small_runs(self):
        def call(x, *args, **kwargs):
            return au.remove_small_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
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


class TestSectionOverlap(unittest.TestCase):
    def test_section_overlap(self):
        def call(x, y):
            return au.section_overlap(np.array(x, dtype=np.bool),
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


class TestContractRuns(unittest.TestCase):
    def test_contract_runs(self):
        def call(x, *args, **kwargs):
            return au.contract_runs(np.array(x, dtype=np.bool), *args, **kwargs).tolist()
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

