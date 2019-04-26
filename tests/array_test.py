import unittest

import numpy as np
import os

from numpy.ma.testutils import assert_array_equal

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.array import (
    ByteAligner,
    array_index_uint16,
    contract_runs,
    first_valid_sample,
    key_value,
    Interpolator,
    index_of_subarray_uint8,
    is_constant,
    is_constant_uint8,
    is_constant_uint16,
    last_valid_sample,
    max_values,
    nearest_idx,
    nearest_slice,
    pack,
    remove_small_runs,
    repair_mask,
    runs_of_ones,
    section_overlap,
    slices_to_array,
    swap_bytes,
    unpack,
)
from flightdatautilities.read import reader


class TestByteAligner(unittest.TestCase):
    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__get_word(self):
        byte_aligned = ByteAligner()
        byte_aligned._buff = np.zeros(4, dtype=np.uint8)
        self.assertEqual(byte_aligned._get_word(0), 0)
        self.assertEqual(byte_aligned._get_word(1), 0)
        self.assertEqual(byte_aligned._get_word(2), 0)
        byte_aligned._buff[1] = 0x47
        byte_aligned._buff[2] = 0x02
        self.assertEqual(byte_aligned._get_word(1), 583)
        byte_aligned._little_endian = False
        self.assertEqual(byte_aligned._get_word(1), 18178)

    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__sync_word_idx(self):
        byte_aligned = ByteAligner()
        byte_aligned._buff = np.zeros(4, dtype=np.uint8)
        self.assertEqual(byte_aligned._sync_word_idx(0), -1)
        self.assertEqual(byte_aligned._sync_word_idx(1), -1)
        self.assertEqual(byte_aligned._sync_word_idx(2), -1)
        byte_aligned._buff = np.array([0xab, 0xB8, 0x05, 0xcd], dtype=np.uint8)
        self.assertEqual(byte_aligned._sync_word_idx(0), -1)
        self.assertEqual(byte_aligned._sync_word_idx(1), 5)
        self.assertEqual(byte_aligned._sync_word_idx(2), -1)
        byte_aligned._buff = np.array([0xab, 0x01, 0xDB, 0xcd], dtype=np.uint8)

    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__frame_wps(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            byte_aligned._buff = next(data_gen)
            self.assertEqual(byte_aligned._frame_wps(0), -1)
            self.assertEqual(byte_aligned._frame_wps(0x300), 128)

    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__next_frame_idx(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            byte_aligned._buff = next(data_gen)
            self.assertEqual(byte_aligned._next_frame_idx(0), 0x300)
            self.assertEqual(byte_aligned._wps, 128)
            self.assertEqual(byte_aligned._next_frame_idx(0x700), 0x700)
            self.assertEqual(byte_aligned._wps, 128)
            self.assertEqual(byte_aligned._next_frame_idx(0xB00), 0xB00)
            self.assertEqual(byte_aligned._wps, 128)
            self.assertEqual(byte_aligned._next_frame_idx(0xF00), -1)

    def test__loop(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        def func(idx):
            return idx
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned._loop(data_gen, func)),
                             [0x300, 0x700, 0xB00])

    def test_identify_1(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])
        # minimum data
        byte_aligned.reset()
        with reader(path, dtype=np.uint8, stop=0x700) as data_gen:
            self.assertEqual(next(byte_aligned.identify(data_gen)), (0x300, 128, '717'))

    def test_identify_2(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '09', 'DAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_3(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '09', 'QAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_4(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '03', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_identify_5(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '05', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_6(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '06', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717'), (4096, 128, '717'),
                              (5120, 128, '717'), (6144, 128, '717'), (7168, 128, '717')])

    def test_identify_7(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_process_1(self):
        byte_aligned = ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        expected = reader(path, dtype=np.uint8, start=0x300, stop=0xF00).first()
        with reader(path, dtype=np.uint8) as data_gen:
            output = np.concatenate(list(byte_aligned.process(data_gen)))
        self.assertTrue(np.all(output == expected))

    def test_process_2(self):
        byte_aligned = ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, 'all_sync.dat')
        array = reader(path, dtype=np.uint8).first()
        data = array.tostring()
        self.assertEqual(data, next(byte_aligned.process(array)).tostring())
        # split into 2 equal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.split(array, 2)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 4 equal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.split(array, 4)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 3 unequal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.array_split(array, 3)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())

    def test_process_3(self):
        byte_aligned = ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, 'all_sync.dat')
        data = reader(path).first()
        offset_data = b'\xFF' * 20 + data + b'\x47\x02' + b'\xFF' * 50
        array = np.fromstring(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligned.process(array)).tostring())
        # odd offset
        byte_aligned.reset()
        offset_data = b'\x47' * 21 + data + b'\x47\x02' + b'\xB8' * 57
        array = np.fromstring(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligned.process(array)).tostring())
        # split into 10 unequal parts
        byte_aligned.reset()
        data_gen = iter(np.array_split(array, 4))
        self.assertEqual(data, np.concatenate(list(byte_aligned.process(data_gen))).tostring())
        # 2 sections of data
        byte_aligned.reset()
        offset_data = b'\xFF' * 537 + data + b'\x47\x02' + b'\x00' * 258 + data + b'\x47\x02' + b'\xFF' * 210
        data_gen = byte_aligned.process(np.fromstring(offset_data, dtype=np.uint8))
        self.assertEqual(data * 2, np.concatenate(list(data_gen)).tostring())

    def test_process_start_and_stop(self):
        byte_aligned = ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, 'all_sync.dat')
        data = reader(path).first()
        array = np.fromstring(data, dtype=np.uint8)
        def call(expected, array, *args, **kwargs):
            result = list(byte_aligned.process(array, *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligned.reset()
            # also test split array buffering
            result = list(byte_aligned.process(iter(np.split(array, 4)), *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligned.reset()
        call(data, array, stop=100)
        call([], array, start=100)
        call(data[:512], array, stop=4)
        call(data[:512], array, stop=2)
        call(data[:1024], array, stop=6)
        call(data[:1024], array, start=2, stop=7)
        call(data[512:1024], array, start=4, stop=8)
        call(data[512:1536], array, start=6, stop=10)
        call(data[3584:4096], array, start=28)
        self.assertRaises(ValueError, list, byte_aligned.process(array, 10, 10))
        self.assertRaises(ValueError, list, byte_aligned.process(array, 10, 5))
        self.assertRaises(ValueError, list, byte_aligned.process(array, None, 0))
        self.assertRaises(ValueError, list, byte_aligned.process(array, None, -1))
        self.assertRaises(ValueError, list, byte_aligned.process(array, -1, None))


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


class TestKeyValue(unittest.TestCase):
    def test_key_value(self):
        data = np.fromstring(b'***\x0ATAILNUM=G-FDSL\x0ASERIALNUM=10344\x0A***', dtype=np.uint8)
        delimiter = b'='
        separator = b'\x0A'
        self.assertEqual(key_value(data, 'TAILNUM', delimiter, separator), b'G-FDSL')
        self.assertEqual(key_value(data, 'SERIALNUM', delimiter, separator), b'10344')


class TestSwapBytes(unittest.TestCase):
    def test_swap_bytes(self):
        arr = np.ones(0, dtype=np.uint16)
        self.assertEqual(len(swap_bytes(arr)), 0)
        data = b'\xAF'
        arr = np.fromstring(data, dtype=np.uint8)
        self.assertEqual(swap_bytes(arr).tostring(), data)
        data = b'\x12\xAB\xCD\xEF'
        arr = np.fromstring(data, dtype=np.uint8)
        self.assertEqual(swap_bytes(arr).tostring(), data)
        arr = np.fromstring(data, dtype=np.uint16)
        self.assertEqual(swap_bytes(arr).tostring(), b'\xAB\x12\xEF\xCD')


class TestPack(unittest.TestCase):
    def test_pack(self):
        self.assertEqual(
            pack(np.fromstring(b'\x47\x02\xAB\x0C', dtype=np.uint8)).tostring(),
            np.fromstring(b'\x47\xB2\xCA', dtype=np.uint8).tostring())


class TestUnpack(unittest.TestCase):
    def test_unpack(self):
        self.assertEqual(
            unpack(np.fromstring(b'\x47\xB2\xCA', dtype=np.uint8)).tostring(),
            np.fromstring(b'\x47\x02\xAB\x0C', dtype=np.uint8).tostring())


class TestArrayIndexUint16(unittest.TestCase):
    def test_array_index_uint16(self):
        self.assertEqual(array_index_uint16(10, np.empty(0, dtype=np.uint16)), -1)
        self.assertEqual(array_index_uint16(10, np.array([2,4,6,8], dtype=np.uint16)), -1)
        self.assertEqual(array_index_uint16(10, np.array([10], dtype=np.uint16)), 0)
        self.assertEqual(array_index_uint16(10, np.array([2,4,6,8,10], dtype=np.uint16)), 4)


class TestIndexOfSubarray(unittest.TestCase):
    def test_index_of_subarray(self):
        array = np.zeros(16, dtype=np.uint8)
        subarray = np.array([1, 2, 3, 4], dtype=np.uint8)
        self.assertEqual(index_of_subarray_uint8(array, subarray), -1)
        self.assertEqual(index_of_subarray_uint8(array, subarray, start=5), -1)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        array[3] = 4
        self.assertEqual(index_of_subarray_uint8(array, subarray), 0)
        self.assertEqual(index_of_subarray_uint8(array, subarray, start=1), -1)
        array[1] = 5
        self.assertEqual(index_of_subarray_uint8(array, subarray), -1)
        array[12] = 1
        array[13] = 2
        array[14] = 3
        array[15] = 4
        self.assertEqual(index_of_subarray_uint8(array, subarray), 12)
        self.assertEqual(index_of_subarray_uint8(array, subarray, start=10), 12)
        self.assertEqual(index_of_subarray_uint8(array, subarray, start=14), -1)
        self.assertEqual(index_of_subarray_uint8(subarray, array), -1)
        self.assertEqual(index_of_subarray_uint8(subarray, array, start=10000), -1)