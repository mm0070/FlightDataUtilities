# cython: language_level=3, boundscheck=False
import unittest

import numpy as np
import os
from binascii import hexlify

from numpy.ma.testutils import assert_array_equal

from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities cimport array
from flightdatautilities.array import contract_runs, nearest_idx, remove_small_runs, repair_mask, runs_of_ones
from flightdatautilities.read import reader


FLIGHT_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'flight_data')
BYTE_ALIGNED_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'byte_aligned')
TDQAR_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'tdqar')
TDWGL_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'tdwgl')


class TestAlignArrays(unittest.TestCase):
    def test_align_arrays(self):
        self.assertEqual(array.align_arrays(np.arange(10), np.arange(20, 30)).tolist(),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(array.align_arrays(np.arange(40, 80), np.arange(20, 40)).tolist(),
                         [40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78])
        self.assertEqual(array.align_arrays(np.arange(40,80), np.arange(30, 40)).tolist(),
                         [40, 44, 48, 52, 56, 60, 64, 68, 72, 76])
        self.assertEqual(array.align_arrays(np.arange(10), np.arange(20, 40)).tolist(),
                         [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9])


class TestAllArray(unittest.TestCase):
    def test_all_array(self):
        def call(x):
            return array.all_array(np.array(x))
        self.assertTrue(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertFalse(call([True, False]))
        self.assertFalse(call([False, True]))


class TestAnyArray(unittest.TestCase):
    def test_any_array(self):
        def call(x):
            return array.any_array(np.array(x))
        self.assertFalse(call([]))
        self.assertTrue(call([True]))
        self.assertFalse(call([False]))
        self.assertTrue(call([True, True]))
        self.assertTrue(call([True, False]))
        self.assertTrue(call([False, True]))


class TestByteAligner(unittest.TestCase):
    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__get_word(self):
        byte_aligned = array.ByteAligner()
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
        byte_aligned = array.ByteAligner()
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
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            byte_aligned._buff = next(data_gen)
            self.assertEqual(byte_aligned._frame_wps(0), -1)
            self.assertEqual(byte_aligned._frame_wps(0x300), 128)

    @unittest.skip('Test requires method gil enabled and cpdef')
    def test__next_frame_idx(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
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
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        def func(idx):
            return idx
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned._loop(data_gen, func)),
                             [0x300, 0x700, 0xB00])

    def test_identify_1(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])
        # minimum data
        byte_aligned.reset()
        with reader(path, dtype=np.uint8, stop=0x700) as data_gen:
            self.assertEqual(next(byte_aligned.identify(data_gen)), (0x300, 128, '717'))

    def test_identify_2(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '01', 'DAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_3(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '01', 'QAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_4(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '02', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_identify_5(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '03', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_6(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '04', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717'), (4096, 128, '717'),
                              (5120, 128, '717'), (6144, 128, '717'), (7168, 128, '717')])

    def test_identify_7(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligned.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_process_1(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        expected = reader(path, dtype=np.uint8, start=0x300, stop=0xF00).first()
        with reader(path, dtype=np.uint8) as data_gen:
            output = np.concatenate(list(byte_aligned.process(data_gen)))
        self.assertTrue(np.all(output == expected))

    def test_process_2(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        arr = reader(path, dtype=np.uint8).first()
        data = arr.tostring()
        self.assertEqual(data, next(byte_aligned.process(arr)).tostring())
        # split into 2 equal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.split(arr, 2)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 4 equal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.split(arr, 4)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 3 unequal parts
        byte_aligned.reset()
        data_gen = byte_aligned.process(iter(np.array_split(arr, 3)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())

    def test_process_3(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        data = reader(path).first()
        offset_data = b'\xFF' * 20 + data + b'\x47\x02' + b'\xFF' * 50
        arr = np.fromstring(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligned.process(arr)).tostring())
        # odd offset
        byte_aligned.reset()
        offset_data = b'\x47' * 21 + data + b'\x47\x02' + b'\xB8' * 57
        arr = np.fromstring(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligned.process(arr)).tostring())
        # split into 10 unequal parts
        byte_aligned.reset()
        data_gen = iter(np.array_split(arr, 4))
        self.assertEqual(data, np.concatenate(list(byte_aligned.process(data_gen))).tostring())
        # 2 sections of data
        byte_aligned.reset()
        offset_data = b'\xFF' * 537 + data + b'\x47\x02' + b'\x00' * 258 + data + b'\x47\x02' + b'\xFF' * 210
        data_gen = byte_aligned.process(np.fromstring(offset_data, dtype=np.uint8))
        self.assertEqual(data * 2, np.concatenate(list(data_gen)).tostring())

    def test_process_start_and_stop(self):
        byte_aligned = array.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        data = reader(path).first()
        arr = np.fromstring(data, dtype=np.uint8)
        def call(expected, array, *args, **kwargs):
            result = list(byte_aligned.process(arr, *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligned.reset()
            # also test split array buffering
            result = list(byte_aligned.process(iter(np.split(arr, 4)), *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligned.reset()
        call(data, arr, stop=100)
        call([], arr, start=100)
        call(data[:512], arr, stop=4)
        call(data[:512], arr, stop=2)
        call(data[:1024], arr, stop=6)
        call(data[:1024], arr, start=2, stop=7)
        call(data[512:1024], arr, start=4, stop=8)
        call(data[512:1536], arr, start=6, stop=10)
        call(data[3584:4096], arr, start=28)
        self.assertRaises(ValueError, list, byte_aligned.process(arr, 10, 10))
        self.assertRaises(ValueError, list, byte_aligned.process(arr, 10, 5))
        self.assertRaises(ValueError, list, byte_aligned.process(arr, None, 0))
        self.assertRaises(ValueError, list, byte_aligned.process(arr, None, -1))
        self.assertRaises(ValueError, list, byte_aligned.process(arr, -1, None))


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


class TestNoneIdx(unittest.TestCase):
    def test_none_idx(self):
        self.assertEqual(array.none_idx(0), 0)
        self.assertEqual(array.none_idx(2), 2)
        self.assertEqual(array.none_idx(None), -1)


class TestIdxNone(unittest.TestCase):
    def test_idx_none(self):
        self.assertEqual(array.idx_none(0), 0)
        self.assertEqual(array.idx_none(2), 2)
        self.assertEqual(array.idx_none(-1), None)


class TestGetmaskarray1d(unittest.TestCase):
    def test_getmaskarray1d(self):
        data = np.ma.empty(3)
        data[1] = np.ma.masked

        mask = np.asarray(array.getmaskarray1d(data))
        self.assertEqual(str(mask.dtype), 'uint8')
        self.assertEqual(mask.tolist(), [0, 1, 0])


class TestTwosComplement(unittest.TestCase):
    def test_twos_complement(self):
        self.assertEqual(array.twos_complement(np.arange(4), 2).tolist(), [0, 1, -2, -1])


class TestReadUint(unittest.TestCase):
    def test_read_uint16_le(self):
        data = np.zeros(4, dtype=np.uint8)
        self.assertEqual(array.read_uint16_le(data, 0), 0)
        self.assertEqual(array.read_uint16_le(data, 1), 0)
        self.assertEqual(array.read_uint16_le(data, 2), 0)
        data = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(array.read_uint16_le(data, 0), 513)
        self.assertEqual(array.read_uint16_le(data, 1), 770)
        self.assertEqual(array.read_uint16_le(data, 2), 1027)

    def test_read_uint16_be(self):
        data = np.zeros(4, dtype=np.uint8)
        self.assertEqual(array.read_uint16_be(data, 0), 0)
        self.assertEqual(array.read_uint16_be(data, 1), 0)
        self.assertEqual(array.read_uint16_be(data, 2), 0)
        data = np.arange(1, 5, dtype=np.uint8)
        self.assertEqual(array.read_uint16_be(data, 0), 258)
        self.assertEqual(array.read_uint16_be(data, 1), 515)
        self.assertEqual(array.read_uint16_be(data, 2), 772)

    def test_read_uint32_le(self):
        data = np.zeros(6, dtype=np.uint8)
        self.assertEqual(array.read_uint32_le(data, 0), 0)
        self.assertEqual(array.read_uint32_le(data, 1), 0)
        self.assertEqual(array.read_uint32_le(data, 2), 0)
        data = np.arange(1, 7, dtype=np.uint8)
        self.assertEqual(array.read_uint32_le(data, 0), 67305985)
        self.assertEqual(array.read_uint32_le(data, 1), 84148994)
        self.assertEqual(array.read_uint32_le(data, 2), 100992003)

    def test_read_uint32_be(self):
        data = np.zeros(6, dtype=np.uint8)
        self.assertEqual(array.read_uint32_be(data, 0), 0)
        self.assertEqual(array.read_uint32_be(data, 1), 0)
        self.assertEqual(array.read_uint32_be(data, 2), 0)
        data = np.arange(1, 7, dtype=np.uint8)
        self.assertEqual(array.read_uint32_be(data, 0), 16909060)
        self.assertEqual(array.read_uint32_be(data, 1), 33752069)
        self.assertEqual(array.read_uint32_be(data, 2), 50595078)


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
