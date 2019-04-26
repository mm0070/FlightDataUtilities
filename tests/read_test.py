import numpy as np
import os
import unittest

from flightdatautilities.iterext import chunk
from flightdatautilities.read import data_reader, file_reader, generator_reader, reader

from flightdataprocessing.common.test import TEST_DATA_PATH


class ReaderImplementationTest(object):
    def setUp(self):
        self.filepath = os.path.join(TEST_DATA_PATH, 'l3uqar', '01', 'serial_num_7_digits.dat')
        with open(self.filepath, 'rb') as f:
            self.data = f.read()

    def test_reader(self):
        with self.cls(self.input) as data_gen:
            self.assertEqual(list(data_gen), [self.data])
        with self.cls(self.input, dtype=np.uint8) as data_gen:
            chunks = list(data_gen)
            self.assertEqual(chunks[0].dtype, np.uint8)
            self.assertEqual([c.tostring() for c in chunks], [self.data])
        with self.cls(self.input, count=0x4000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[:0x4000], self.data[0x4000:]])
        with self.cls(self.input, count=0x2000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[x*0x2000:(x+1)*0x2000] for x in range(4)])
        with self.cls(self.input, stop=0x2000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[:0x2000]])
        with self.cls(self.input, start=0x6000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[0x6000:]])
        with self.cls(self.input, start=0x2000, stop=0x4000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[0x2000:0x4000]])
        with self.cls(self.input, start=0x2000, stop=0x4000, count=0x1000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[0x2000:0x3000], self.data[0x3000:0x4000]])
        with self.cls(self.input, start=0x2500, stop=0x4000, count=0x1000) as data_gen:
            self.assertEqual(list(data_gen), [self.data[0x2500:0x3500], self.data[0x3500:0x4000]])

    def test_all(self):
        self.assertEqual(self.cls(self.input).all(), self.data)
        self.assertEqual(self.cls(self.input, count=0x2000).all(), self.data)
        self.assertEqual(self.cls(self.input, count=1).all(), self.data)
        self.assertEqual(self.cls(self.input, dtype=np.uint8).all().tostring(), self.data)
        self.assertEqual(self.cls(self.input, start=0x2000, stop=0x4000).all(), self.data[0x2000:0x4000])
        self.assertEqual(self.cls(self.input, dtype=np.uint32, start=0x2000, stop=0x4000).all().tostring(), self.data[0x2000:0x4000])
        self.assertEqual(self.cls(self.input, dtype=np.uint32, start=2048, stop=4096, byte=False).all().tostring(), self.data[0x2000:0x4000])

    def test_first(self):
        self.assertEqual(self.cls(self.input).first(), self.data)
        self.assertEqual(self.cls(self.input, dtype=np.uint8).first().tostring(), self.data)
        self.assertEqual(self.cls(self.input, count=0x2000).first(), self.data[:0x2000])
        self.assertEqual(self.cls(self.input, stop=0x1000).first(), self.data[:0x1000])
        self.assertEqual(self.cls(self.input, start=0x6000).first(), self.data[0x6000:])
        self.assertEqual(self.cls(self.input, start=0x3000, stop=0x4000).first(), self.data[0x3000:0x4000])


class TestFileReader(ReaderImplementationTest, unittest.TestCase):
    def setUp(self):
        super(TestFileReader, self).setUp()
        self.cls = file_reader
        self.input = self.filepath


class TestDataReader(ReaderImplementationTest, unittest.TestCase):
    def setUp(self):
        super(TestDataReader, self).setUp()
        self.cls = data_reader
        self.input = np.fromstring(self.data)


class TestGeneratorReader(ReaderImplementationTest, unittest.TestCase):
    def setUp(self):
        super(TestGeneratorReader, self).setUp()
        self.cls = generator_reader

    @property
    def input(self):
        return chunk([self.data], 4096)


class TestReader(unittest.TestCase):
    def test_reader_path(self):
        path = u'path'
        r = reader(path)
        self.assertTrue(isinstance(r, file_reader))
        self.assertEqual(r.path, path)

    def test_reader_data(self):
        data = b'data'
        r = reader(data)
        # assumes filepath by default
        self.assertTrue(isinstance(r, file_reader))
        self.assertEqual(r.path, data)
        r = reader(data, data=True)
        self.assertTrue(isinstance(r, data_reader))
        self.assertEqual(r.data, data)

    def test_reader_array(self):
        array = np.arange(1)
        r = reader(array)
        self.assertTrue(isinstance(r, data_reader))
        self.assertEqual(r.data, array.tostring())

    def test_reader_generator(self):
        data_gen = (x for x in [1])
        r = reader(data_gen)
        self.assertTrue(isinstance(r, generator_reader))
        self.assertEqual(r.data_gen, data_gen)

    def test_reader_reader(self):
        data = b'data'
        reader_input = reader(data, data=True)
        reader_output = reader(reader_input)
        self.assertEqual(reader_input.data, reader_output.data)
        stop = 10
        reader_output = reader(reader_input, stop=stop)
        self.assertEqual(reader_output.stop, stop)

