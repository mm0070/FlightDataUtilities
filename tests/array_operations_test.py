import numpy as np
import unittest

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.array_operations import (
    downsample_arrays,
    upsample_arrays,
)


class TestDownsampleArrays(unittest.TestCase):
    def test_downsample_arrays(self):
        array1 = np.ma.arange(10)
        array2 = np.ma.arange(5)
        downsampled_array1, downsampled_array2 = downsample_arrays([array1,
                                                                    array2])
        ma_test.assert_array_equal(downsampled_array1, np.ma.arange(0,10,2))
        ma_test.assert_array_equal(downsampled_array2, array2)
        # With mask.
        array1[5:8] = np.ma.masked
        array2[2:4] = np.ma.masked
        downsampled_array1, downsampled_array2 = downsample_arrays([array1,
                                                                    array2])
        result_array1 = np.ma.arange(0,10,2)
        result_array1[3] = np.ma.masked
        ma_test.assert_array_equal(downsampled_array1, result_array1)
        ma_test.assert_array_equal(downsampled_array2, array2)


class TestUpsampleArrays(unittest.TestCase):
    def test_upsample_arrays(self):
        array1 = np.ma.arange(10)
        array2 = np.ma.arange(5)
        upsampled_array1, upsampled_array2 = upsample_arrays([array1,
                                                              array2])
        ma_test.assert_array_equal(upsampled_array1, array1)
        ma_test.assert_array_equal(upsampled_array2, array2.repeat(2))
        # With mask.
        array1[5:8] = np.ma.masked
        array2[2:4] = np.ma.masked
        upsampled_array1, upsampled_array2 = upsample_arrays([array1,
                                                              array2])
        result_array2 = array2.repeat(2)
        result_array2[4:8] = np.ma.masked
        ma_test.assert_array_equal(upsampled_array1, array1)
        ma_test.assert_array_equal(upsampled_array2, result_array2)

