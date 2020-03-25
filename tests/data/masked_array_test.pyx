# cython: language_level=3, boundscheck=False
from binascii import hexlify
import os
import unittest

cimport cython
import numpy as np
cimport numpy as np
from numpy.ma.testutils import assert_array_equal

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.data cimport masked_array as ma
#from flightdatautilities.data.masked_array import repair_mask


class TestFirstIndexWithinROC(unittest.TestCase):

    def test_first_index_within_roc(self):
        array = np.ma.zeros(20)
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 1, 0, 2, 10), 2)
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 1, 2, 5, 15), 5)

        array = np.ma.arange(20) * 2
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 1, 0, 3, 10), -1)
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 5, 0, 4, 10), 4)

        array = np.ma.array([100, 100, 0, 0, 0, 0, 0, 0])
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 25, 0, 2, 8), 4)
        array = np.ma.array([100, 100, 200, 200, 200, 200, 200, 200])
        self.assertEqual(ma.first_idx_within_roc(array.data, array.mask, 25, 0, 2, 8), 4)


################################################################################
# Utility functions


class TestGetmaskarray1d(unittest.TestCase):
    def test_getmaskarray1d(self):
        array = np.ma.zeros(5)
        self.assertEqual(list(ma.getmaskarray1d(np.ma.zeros(5))), [0] * 5)  # scalar mask
        array.mask = True
        self.assertEqual(list(ma.getmaskarray1d(array)), [1] * 5)  # array mask
        array = np.ma.zeros(5)
        array[1] = np.ma.masked
        self.assertEqual(list(ma.getmaskarray1d(array)), [0, 1, 0, 0, 0])  # array mask


################################################################################
# Mask ratio/percentage


class TestMaskRatio(unittest.TestCase):
    def test_mask_ratio(self):
        self.assertEqual(ma.mask_ratio(np.True_), 1)
        self.assertEqual(ma.mask_ratio(np.False_), 0)
        self.assertEqual(ma.mask_ratio(np.zeros(1, dtype=np.bool)), 0)
        self.assertEqual(ma.mask_ratio(np.ones(1, dtype=np.bool)), 1)
        self.assertEqual(ma.mask_ratio(np.array([0, 1], dtype=np.bool)), 0.5)


class TestPercentMasked(unittest.TestCase):
    def test_percent_masked(self):
        self.assertEqual(ma.percent_unmasked(np.True_), 0)
        self.assertEqual(ma.percent_unmasked(np.False_), 100)
        self.assertEqual(ma.percent_unmasked(np.zeros(1, dtype=np.bool)), 100)
        self.assertEqual(ma.percent_unmasked(np.ones(1, dtype=np.bool)), 0)
        self.assertEqual(ma.percent_unmasked(np.array([0, 1], dtype=np.bool)), 50)


################################################################################
# Fill range


class TestFillRange(unittest.TestCase):
    def test_fill_range(self):
        data = np.arange(5, dtype=np.float64)
        mask = np.ones(5, dtype=np.uint8)
        ma.fill_range[np.float64_t](data, mask, 5, 0, 0)
        expected_data = list(range(5))
        expected_mask = [1] * 5
        self.assertEqual(data.tolist(), expected_data)
        self.assertEqual(mask.tolist(), expected_mask)
        ma.fill_range[np.float64_t](data, mask, 5, 2, 2)
        self.assertEqual(data.tolist(), expected_data)
        self.assertEqual(mask.tolist(), expected_mask)
        ma.fill_range[np.float64_t](data, mask, 5, 2, 0)
        self.assertEqual(data.tolist(), expected_data)
        self.assertEqual(mask.tolist(), expected_mask)
        ma.fill_range[np.float64_t](data, mask, 5, 0, 1)
        expected_data[0] = 5
        expected_mask[0] = 0
        self.assertEqual(data.tolist(), expected_data)
        self.assertEqual(mask.tolist(), expected_mask)
        ma.fill_range[np.float64_t](data, mask, 7, 2, 4)
        expected_data[2:4] = [7] * 2
        expected_mask[2:4] = [0] * 2
        self.assertEqual(data.tolist(), expected_data)
        self.assertEqual(mask.tolist(), expected_mask)


################################################################################
# Interpolate range


class TestInterpolateRangeUnsafe(unittest.TestCase):
    def test_interpolate_range_unsafe(self):
        data = np.zeros(10, dtype=np.float64)
        mask = np.zeros(10, dtype=np.uint8)
        for start, stop in ((0, 0), (2, 4), (0, 9)):
            ma.interpolate_range_unsafe[np.float64_t](data, mask, start, stop)
            self.assertEqual(data.tolist(), [0] * 10)
            self.assertEqual(mask.tolist(), [0] * 10)
        data[9] = 9
        ma.interpolate_range_unsafe[np.float64_t](data, mask, 0, 9)
        self.assertEqual(data.tolist(), list(range(10)))
        self.assertEqual(mask.tolist(), [0] * 10)
        data = np.zeros(10, dtype=np.float64)
        data[9] = -9
        ma.interpolate_range_unsafe[np.float64_t](data, mask, 0, 9)
        self.assertEqual(data.tolist(), list(range(0, -10, -1)))
        self.assertEqual(mask.tolist(), [0] * 10)
        data = np.zeros(10, dtype=np.float64)
        data[9] = -9
        ma.interpolate_range_unsafe[np.float64_t](data, mask, 0, 9)
        self.assertEqual(data.tolist(), list(range(0, -10, -1)))
        self.assertEqual(mask.tolist(), [0] * 10)
        data = np.zeros(10, dtype=np.float64)
        data[2] = 2
        data[6] = 28
        mask[1:3] = True
        mask[8:10] = True
        ma.interpolate_range_unsafe[np.float64_t](data, mask, 2, 6)
        self.assertEqual(data.tolist(), [0, 0, 2, 8.5, 15, 21.5, 28, 0, 0, 0])
        self.assertEqual(mask.tolist(), [0, 1, 1, 0, 0, 0, 0, 0, 1, 1])


class TestInterpolateRange(unittest.TestCase):
    def test_interpolate_range(self):
        data = np.zeros(10, dtype=np.float64)
        mask = np.zeros(10, dtype=np.uint8)
        for start, stop in ((0, 0), (2, 4), (0, 9), (0, 12), (0, -1), (-5, -3)):
            ma.interpolate_range[np.float64_t](data, mask, start, stop)
            self.assertEqual(data.tolist(), [0] * 10)
            self.assertEqual(mask.tolist(), [0] * 10)
        data[9] = 9
        data_copy, mask_copy = data.copy(), mask.copy()
        ma.interpolate_range[np.float64_t](data_copy, mask_copy, 0, 9)
        self.assertEqual(data_copy.tolist(), list(range(10)))
        self.assertEqual(mask_copy.tolist(), [0] * 10)
        data_copy, mask_copy = data.copy(), mask.copy()
        ma.interpolate_range[np.float64_t](data_copy, mask_copy, 0, 12)
        self.assertEqual(data_copy.tolist(), list(range(10)))
        self.assertEqual(mask_copy.tolist(), [0] * 10)
        data = np.zeros(10, dtype=np.float64)
        data[9] = -9
        ma.interpolate_range[np.float64_t](data, mask, 0, 9)
        self.assertEqual(data.tolist(), list(range(0, -10, -1)))
        self.assertEqual(mask.tolist(), [0] * 10)
        data = np.zeros(10, dtype=np.float64)
        data[2] = 2
        data[6] = 28
        mask[1] = True
        mask[3:5] = True
        mask[8:10] = True
        data_copy, mask_copy = data.copy(), mask.copy()
        ma.interpolate_range[np.float64_t](data_copy, mask_copy, 2, 6)
        self.assertEqual(data_copy.tolist(), [0, 0, 2, 8.5, 15, 21.5, 28, 0, 0, 0])
        self.assertEqual(mask_copy.tolist(), [0, 1, 0, 0, 0, 0, 0, 0, 1, 1])
        data_copy, mask_copy = data.copy(), mask.copy()
        ma.interpolate_range[np.float64_t](data_copy, mask_copy, -8, -4)
        self.assertEqual(data_copy.tolist(), [0, 0, 2, 8.5, 15, 21.5, 28, 0, 0, 0])
        self.assertEqual(mask_copy.tolist(), [0, 1, 0, 0, 0, 0, 0, 0, 1, 1])
        # cannot interpolate using masked start value, but cannot raise due to nogil
        mask[2] = True
        ma.interpolate_range[np.float64_t](data, mask, 2, 6)
        self.assertEqual(data.tolist(), [0, 0, 2, 0, 0, 0, 28, 0, 0, 0])
        self.assertEqual(mask.tolist(), [0, 1, 1, 1, 1, 0, 0, 0, 1, 1])


# TODO: change to next_unmasked_value
#class TestFirstValidSample(unittest.TestCase):
    #def test_first_valid_sample(self):
        #data = np.arange(11, 15)
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (1, 12))
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=True)), (None, None))
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 2), (3, 14))
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 1), (1, 12))
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (None, None))
        #self.assertEqual(op.first_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (3, 14))


#class TestLastValidSample(unittest.TestCase):
    #def test_last_valid_sample(self):
        #data = np.arange(11, 15)
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=[1,0,1,0])), (3, 14))
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=True)), (None, None))
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -2), (1, 12))
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), -3), (1, 12))
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=[1,0,1,0]), 9), (3, 14))
        #self.assertEqual(op.last_valid_sample(np.ma.array(data, mask=[0,0,0,1])), (2, 13))


################################################################################
# Repair mask


#class TestRepairMask(unittest.TestCase):
    #def setUp(self):
        #self.basic_data = np.ma.array(
            #[0, 0, 10, 0, 0, 20, 23, 26, 30, 0, 0],
            #mask=[1,1,0,1,1,0,0,0,0,1,1])

    #def test_repair_mask_basic_fill_start(self):
        #self.assertEqual(repair_mask(self.basic_data,
                                           #method='fill_start').tolist(),
                         #[None, None, 10, 10, 10, 20, 23, 26, 30, 30, 30])
        #self.assertEqual(repair_mask(self.basic_data, extrapolate=True,
                                           #method='fill_start').tolist(),
                         #[10, 10, 10, 10, 10, 20, 23, 26, 30, 30, 30])

    #def test_repair_mask_basic_fill_stop(self):
        #self.assertEqual(repair_mask(self.basic_data, method='fill_stop').tolist(),
                         #[10, 10, 10, 20, 20, 20, 23, 26, 30, None, None])
        #self.assertEqual(repair_mask(self.basic_data, extrapolate=True, method='fill_stop').tolist(),
                         #[10, 10, 10, 20, 20, 20, 23, 26, 30, 30, 30])

    #def test_repair_mask_basic_1(self):
        #data = np.ma.arange(10)
        #data[3] = np.ma.masked
        #data[6:8] = np.ma.masked
        #res = repair_mask(data)
        #np.testing.assert_array_equal(res.data,range(10))
        ## test mask is now unmasked
        #self.assertFalse(np.any(res.mask[3:9]))

    #def test_repair_mask_too_much_invalid(self):
        #data = np.ma.arange(20)
        #data[4:15] = np.ma.masked
        #ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    #def test_repair_mask_not_at_start(self):
        #data = np.ma.arange(10)
        #data[0] = np.ma.masked
        #ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    #def test_repair_mask_not_at_end(self):
        #data = np.ma.arange(10)
        #data[9] = np.ma.masked
        #ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    #def test_repair_mask_short_sample(self):
        ## Very short samples were at one time returned as None, but simply
        ## applying the normal "rules" seems more consistent, so this is a
        ## test to show that an old function no longer applies.
        #data = np.ma.arange(2)
        #data[1] = np.ma.masked
        #ma_test.assert_masked_array_approx_equal(repair_mask(data), data)

    #def test_repair_mask_extrapolate(self):
        #data = np.ma.array([2,4,6,7,5,3,1], mask=[1,1,0,0,1,1,1])
        #res = repair_mask(data, extrapolate=True)
        #expected = np.ma.array([6,6,6,7,7,7,7], mask=False)
        #assert_array_equal(res, expected)

    #def test_repair_mask_fully_masked_array(self):
        #data = np.ma.array(np.arange(10), mask=[1]*10)
        ## fully masked raises ValueError
        #self.assertRaises(ValueError, repair_mask, data)
        ## fully masked returns a masked zero array
        #res = repair_mask(data, raise_entirely_masked=False)
        #assert_array_equal(res.data, data.data)
        #assert_array_equal(res.mask, True)

    ##@unittest.skip('repair_above has not yet been carried over from analysis_engine.library version')
    ##def test_repair_mask_above(self):
        ##data = np.ma.arange(10)
        ##data[5] = np.ma.masked
        ##data[7:9] = np.ma.masked
        ##res = repair_mask(data, repair_above=5)
        ##np.testing.assert_array_equal(res.data, range(10))
        ##mask = np.ma.getmaskarray(data)
        ### test only array[5] is still masked as is the first
        ##self.assertFalse(mask[4])
        ##self.assertTrue(mask[5])
        ##self.assertFalse(np.any(mask[6:]))


################################################################################
# Aggregation


# TODO: fix crash
#class TestMaxValues(unittest.TestCase):
    #def test_max_values(self):
        #self.assertEqual(list(ma.max_values(np.ma.empty(0, dtype=np.float64), np.empty(0, dtype=np.bool))), [])
        #self.assertEqual(list(ma.max_values(np.ma.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        #self.assertEqual(list(ma.max_values(np.ma.zeros(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 0)])
        #self.assertEqual(list(ma.max_values(np.ma.ones(1, dtype=np.float64), np.zeros(1, dtype=np.bool))), [])
        #self.assertEqual(list(ma.max_values(np.ma.ones(1, dtype=np.float64), np.ones(1, dtype=np.bool))), [(0, 1)])
        #arr = np.ma.arange(10, dtype=np.float64)
        #matching = np.zeros(10, dtype=np.bool)
        #self.assertEqual(list(ma.max_values(arr, matching)), [])
        #matching[0] = True
        #self.assertEqual(list(ma.max_values(arr, matching)), [(0, 0)])
        #matching[1] = True
        #self.assertEqual(list(ma.max_values(arr, matching)), [(1, 1)])
        #matching[3] = True
        #self.assertEqual(list(ma.max_values(arr, matching)), [(1, 1), (3, 3)])
        #matching[7:] = True
        #self.assertEqual(list(ma.max_values(arr, matching)), [(1, 1), (3, 3), (9, 9)])
        #arr[1] = np.ma.masked
        #self.assertEqual(list(ma.max_values(arr, matching)), [(0, 0), (3, 3), (9, 9)])
        #arr[0] = np.ma.masked
        #self.assertEqual(list(ma.max_values(arr, matching)), [(3, 3), (9, 9)])


################################################################################
# Alignment


class TestAlign(unittest.TestCase):
    def test_align_basic(self):
        aligned = ma.align(np.ma.arange(0, 5), 1, 1, 4, 0.5)
        np.testing.assert_array_equal(
            aligned,
            [0, 0, 0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4],
        )