import numpy as np
import unittest

from flightdatautilities.iterext import iter_data, iter_dtype
from flightdatautilities.type import (
    as_dtype,
    as_int,
    as_sequence,
    is_array,
    is_data,
    is_data_iterable,
)


class TestAsDtype(unittest.TestCase):
    def test_as_dtype(self):
        data = b'abc'
        self.assertEqual(as_dtype(data), data)
        self.assertEqual(as_dtype(data, dtype=None), data)
        dtype = np.uint8
        self.assertTrue(np.all(as_dtype(data, dtype=dtype) == np.fromstring(data, dtype=dtype)))
        data = np.arange(3)
        self.assertEqual(as_dtype(data), data.tostring())
        self.assertEqual(as_dtype(data, dtype=None), data.tostring())
        self.assertTrue(np.all(as_dtype(data, dtype=dtype) == data.view(dtype)))


class TestAsInt(unittest.TestCase):
    def test_as_int(self):
        self.assertEqual(as_int(1), 1)
        self.assertEqual(as_int(1.5), 1)
        self.assertEqual(as_int([10]), 10)
        self.assertEqual(as_int((64,)), 64)
        self.assertRaises(ValueError, as_int, [])
        self.assertRaises(ValueError, as_int, [10, 20])
        self.assertRaises(ValueError, as_int, (10, 20, 30))


class TestAsSequence(unittest.TestCase):
    def test_as_sequence(self):
        self.assertEqual(as_sequence(None), None)
        self.assertEqual(as_sequence(3), [3])
        self.assertEqual(as_sequence(2.4), [2.4])
        self.assertEqual(as_sequence([]), [])
        self.assertEqual(as_sequence([5]), [5])
        self.assertEqual(as_sequence([7, 9]), [7, 9])
        self.assertEqual(as_sequence(tuple()), tuple())
        self.assertEqual(as_sequence((1,)), (1,))
        self.assertEqual(as_sequence((1, 2, 3)), (1, 2, 3))


class TestIsArray(unittest.TestCase):
    def test_is_array(self):
        self.assertTrue(is_array(np.arange(10)))
        self.assertFalse(is_array({}))


class TestIsData(unittest.TestCase):
    def test_is_data(self):
        # TODO: memoryview
        self.assertTrue(is_data(np.arange(10)))
        self.assertTrue(is_data(b'abc'))
        self.assertFalse(is_data(u'abc'))
        self.assertFalse(is_data(7))
        self.assertFalse(is_data(None))


class TestIsDataIterable(unittest.TestCase):
    def test_is_data(self):
        # TODO: memoryview
        self.assertFalse(is_data_iterable(np.arange(10)))
        self.assertFalse(is_data_iterable(b'abc'))
        self.assertFalse(is_data_iterable(u'abc'))
        self.assertFalse(is_data_iterable(7))
        self.assertFalse(is_data_iterable(None))
        self.assertTrue(is_data_iterable([b'abc']))
        self.assertTrue(is_data_iterable([np.arange(10)]))
        self.assertTrue(is_data_iterable(tuple(np.arange(10),)))
        self.assertTrue(is_data_iterable(d for d in [b'abc']))


class TestIterData(unittest.TestCase):
    def test_iter_data(self):
        data_gen = []
        self.assertEqual(list(iter_data(data_gen)), data_gen)
        data_gen = [b'abc']
        self.assertEqual(list(iter_data(data_gen)), data_gen)
        data_gen = [b'a', b'', b'c']
        self.assertEqual(list(iter_data(data_gen)), data_gen)
        data_gen = [b'a', None, b'c']
        self.assertEqual(list(iter_data(data_gen)), [b'a', b'c'])
        array1 = np.arange(4)
        array2 = np.arange(4, 8)
        data_gen = [array1, None, array2]
        self.assertEqual(list(iter_data(data_gen)), [array1, array2])


class TestIterDtype(unittest.TestCase):
    def test_iter_dtype(self):
        for iterable in [[], [b'abc'], [b'a', b'b', b'c']]:
            self.assertEqual(list(iter_dtype(iterable)), iterable)
        array = np.arange(3)
        self.assertEqual(list(iter_dtype([array])), [array.tostring()])
        self.assertEqual(list(iter_dtype([array], dtype=None)), [array.tostring()])
        dtype = np.uint8
        result = list(iter_dtype([array], dtype=dtype))
        self.assertEqual(len(result), 1)
        self.assertTrue(np.all(result[0] == array.view(dtype)))
        data = b'abc'
        result = list(iter_dtype([data], dtype=dtype))
        self.assertEqual(len(result), 1)
        self.assertTrue(np.all(result[0] == np.fromstring(data, dtype=dtype)))

