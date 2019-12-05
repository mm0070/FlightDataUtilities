# cython: language_level=3, boundscheck=False
import os
import unittest

import numpy as np

from flightdatautilities.data cimport byte_align as ba, cython as cy
from flightdatautilities.read import reader


FLIGHT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data', 'flight_data')
BYTE_ALIGNED_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'byte_aligned')
TDQAR_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'tdqar')
TDWGL_DATA_PATH = os.path.join(FLIGHT_DATA_PATH, 'tdwgl')


class TestByteAligner(unittest.TestCase):
    def test__get_word(self):
        cdef ba.ByteAligner byte_aligner = ba.ByteAligner()
        byte_aligner._buff = np.zeros(4, dtype=np.uint8)
        self.assertEqual(byte_aligner._get_word(0), 0)
        self.assertEqual(byte_aligner._get_word(1), 0)
        self.assertEqual(byte_aligner._get_word(2), 0)
        byte_aligner._buff[1] = 0x47
        byte_aligner._buff[2] = 0x02
        self.assertEqual(byte_aligner._get_word(1), 583)
        byte_aligner.little_endian = False
        self.assertEqual(byte_aligner._get_word(1), 1794)

    def test__sync_word_idx(self):
        cdef ba.ByteAligner byte_aligner = ba.ByteAligner()
        byte_aligner._buff = np.zeros(4, dtype=np.uint8)
        self.assertEqual(byte_aligner._sync_word_idx(0), cy.NONE_IDX)
        self.assertEqual(byte_aligner._sync_word_idx(1), cy.NONE_IDX)
        self.assertEqual(byte_aligner._sync_word_idx(2), cy.NONE_IDX)
        byte_aligner._buff = np.array([0xab, 0xB8, 0x05, 0xcd], dtype=np.uint8)
        self.assertEqual(byte_aligner._sync_word_idx(0), cy.NONE_IDX)
        self.assertEqual(byte_aligner._sync_word_idx(1), 5)
        self.assertEqual(byte_aligner._sync_word_idx(2), cy.NONE_IDX)
        byte_aligner._buff = np.array([0xab, 0x01, 0xDB, 0xcd], dtype=np.uint8)

    def test__frame_wps(self):
        cdef ba.ByteAligner byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '07', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            byte_aligner._buff = next(data_gen)
            self.assertEqual(byte_aligner._frame_wps(0), -1)
            self.assertEqual(byte_aligner._frame_wps(0x300), 128)

    def test__next_frame_idx(self):
        cdef ba.ByteAligner byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            byte_aligner._buff = next(data_gen)
            self.assertEqual(byte_aligner._next_frame_idx(0), 0x300)
            self.assertEqual(byte_aligner._wps, 128)
            self.assertEqual(byte_aligner._next_frame_idx(0x700), 0x700)
            self.assertEqual(byte_aligner._wps, 128)
            self.assertEqual(byte_aligner._next_frame_idx(0xB00), 0xB00)
            self.assertEqual(byte_aligner._wps, 128)
            self.assertEqual(byte_aligner._next_frame_idx(0xF00), cy.NONE_IDX)

    def test__loop(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        def func(idx):
            return idx
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner._loop(data_gen, func)),
                             [0x300, 0x700, 0xB00])

    def test_identify_1(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])
        # minimum data
        byte_aligner.reset()
        with reader(path, dtype=np.uint8, stop=0x700) as data_gen:
            self.assertEqual(next(byte_aligner.identify(data_gen)), (0x300, 128, '717'))

    def test_identify_2(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '01', 'DAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_3(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDQAR_DATA_PATH, '01', 'QAR.DAT')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(0, 128, '717'), (1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_4(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '02', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_identify_5(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '03', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717')])

    def test_identify_6(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '04', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(1024, 128, '717'), (2048, 128, '717'), (3072, 128, '717'), (4096, 128, '717'),
                              (5120, 128, '717'), (6144, 128, '717'), (7168, 128, '717')])

    def test_identify_7(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        with reader(path, dtype=np.uint8) as data_gen:
            self.assertEqual(list(byte_aligner.identify(data_gen)),
                             [(0x300, 128, '717'), (0x700, 128, '717'), (0xB00, 128, '717')])

    def test_process_1(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(TDWGL_DATA_PATH, '01', 'raw.dat')
        expected = reader(path, dtype=np.uint8, start=0x300, stop=0xF00).first()
        with reader(path, dtype=np.uint8) as data_gen:
            output = np.concatenate(list(byte_aligner.process(data_gen)))
        self.assertTrue(np.all(output == expected))

    def test_process_2(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        arr = reader(path, dtype=np.uint8).first()
        data = arr.tostring()
        self.assertEqual(data, next(byte_aligner.process(arr)).tostring())
        # split into 2 equal parts
        byte_aligner.reset()
        data_gen = byte_aligner.process(iter(np.split(arr, 2)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 4 equal parts
        byte_aligner.reset()
        data_gen = byte_aligner.process(iter(np.split(arr, 4)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())
        # split into 3 unequal parts
        byte_aligner.reset()
        data_gen = byte_aligner.process(iter(np.array_split(arr, 3)))
        self.assertEqual(data, np.concatenate(list(data_gen)).tostring())

    def test_process_3(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        data = reader(path).first()
        offset_data = b'\xFF' * 20 + data + b'\x47\x02' + b'\xFF' * 50
        arr = np.frombuffer(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligner.process(arr)).tostring())
        # odd offset
        byte_aligner.reset()
        offset_data = b'\x47' * 21 + data + b'\x47\x02' + b'\xB8' * 57
        arr = np.frombuffer(offset_data, dtype=np.uint8)
        self.assertEqual(data, next(byte_aligner.process(arr)).tostring())
        # split into 10 unequal parts
        byte_aligner.reset()
        data_gen = iter(np.array_split(arr, 4))
        self.assertEqual(data, np.concatenate(list(byte_aligner.process(data_gen))).tostring())
        # 2 sections of data
        byte_aligner.reset()
        offset_data = b'\xFF' * 537 + data + b'\x47\x02' + b'\x00' * 258 + data + b'\x47\x02' + b'\xFF' * 210
        data_gen = byte_aligner.process(np.frombuffer(offset_data, dtype=np.uint8))
        self.assertEqual(data * 2, np.concatenate(list(data_gen)).tostring())

    def test_process_start_and_stop(self):
        byte_aligner = ba.ByteAligner()
        path = os.path.join(BYTE_ALIGNED_DATA_PATH, '01', 'all_sync.dat')
        data = reader(path).first()
        arr = np.frombuffer(data, dtype=np.uint8)
        def call(expected, array, *args, **kwargs):
            result = list(byte_aligner.process(arr, *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligner.reset()
            # also test split array buffering
            result = list(byte_aligner.process(iter(np.split(arr, 4)), *args, **kwargs))
            if result:
                result = np.concatenate(result).tostring()
            self.assertEqual(result, expected)
            byte_aligner.reset()
        call(data, arr, stop=100)
        call([], arr, start=100)
        call(data[:512], arr, stop=4)
        call(data[:512], arr, stop=2)
        call(data[:1024], arr, stop=6)
        call(data[:1024], arr, start=2, stop=7)
        call(data[512:1024], arr, start=4, stop=8)
        call(data[512:1536], arr, start=6, stop=10)
        call(data[3584:4096], arr, start=28)
        self.assertRaises(ValueError, list, byte_aligner.process(arr, 10, 10))
        self.assertRaises(ValueError, list, byte_aligner.process(arr, 10, 5))
        self.assertRaises(ValueError, list, byte_aligner.process(arr, None, 0))
        self.assertRaises(ValueError, list, byte_aligner.process(arr, None, -1))
        self.assertRaises(ValueError, list, byte_aligner.process(arr, -1, None))
