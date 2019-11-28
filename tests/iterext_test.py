# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Flight Data Utilities: Iter Extensions: Unit Tests
'''

##############################################################################
# Imports


import logging
import numpy as np
import unittest

from flightdatautilities import iterext


##############################################################################
# Module Setup


def setUpModule():
    logging.disable(logging.CRITICAL)


##############################################################################
# Test Cases


class TestBatch(unittest.TestCase):

    def test_batch(self):
        self.assertEqual(list(iterext.batch(0, 5, 2)), [(0, 2), (2, 4), (4, 5)])
        self.assertEqual(list(iterext.batch(1, 5, 2)), [(1, 3), (3, 5)])
        self.assertEqual(list(iterext.batch(0, 10, 5)), [(0, 5), (5, 10)])
        self.assertEqual(list(iterext.batch(0, 11, 5)), [(0, 5), (5, 10), (10, 11)])


class TestDropLast(unittest.TestCase):

    def test_droplast(self):
        self.assertEqual(list(iterext.droplast(1, range(10))), list(range(9)))
        self.assertEqual(list(iterext.droplast(5, range(10))), list(range(5)))
        self.assertEqual(list(iterext.droplast(10, range(10))), [])
        self.assertEqual(list(iterext.droplast(20, range(10))), [])


class TestJoin(unittest.TestCase):

    def test_join(self):
        self.assertEqual(iterext.join([]), b'')
        joined = iterext.join([], dtype=np.uint8)
        self.assertEqual(joined.tolist(), [])
        self.assertEqual(joined.dtype, np.uint8)
        self.assertEqual(iterext.join([b'abc', b'def']), b'abcdef')
        self.assertEqual(iterext.join([np.array([1, 2]), np.array([3, 4])]).tolist(), [1, 2, 3, 4])
        joined = iterext.join([np.array([1, 2]), np.array([3, 4])], dtype=np.uint8)
        self.assertEqual(joined.tolist(), [1, 2, 3, 4])
        self.assertEqual(joined.dtype, np.uint8)


class TestIterDataStartIdx(unittest.TestCase):
    def test_iter_data_start_idx(self):
        data = []
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0)), data)
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 5)), data)
        data = [b'a']
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0)), data)
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 1)), [])
        data = [b'abc']
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0)), data)
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0, count=2)), [b'ab', b'c'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 1)), [b'bc'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 2)), [b'c'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 2, byte=True)), [b'c'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 3)), [])
        data = [b'a', b'b', b'c']
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0)), data)
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 1)), [b'b', b'c'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 2)), [b'c'])
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 3)), [])
        data = [np.array([1, 2]), np.array([3, 4, 5])]
        self.assertEqual(list(iterext.iter_data_start_idx((d for d in data), 0)), data)
        expected = [[1, 2], [3, 4], [5]]
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d for d in data), 0, count=2)], expected)
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d for d in data), 0, count=2, byte=True)], expected)
        expected = [[2], [3, 4, 5]]
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d for d in data), 1)], expected)
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d.astype(np.uint8) for d in data), 1, byte=True)], expected)
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d.astype(np.uint32) for d in data), 4, byte=True)], expected)
        expected = [[2, 3], [4, 5]]
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d.astype(np.uint32) for d in data), 4, count=2, byte=True)], expected)
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d for d in data), 1, count=2)], expected)
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d.astype(np.uint32) for d in data), 16, count=2, byte=True)], [[5]])
        # starting at a non-itemsize byte offset effectively byte shifts
        self.assertEqual([x.tolist() for x in iterext.iter_data_start_idx((d.astype(np.uint32) for d in data), 3, count=2, byte=True)], [[512, 768], [1024, 1280]])
        self.assertRaises(ValueError, iterext.iter_data_start_idx, (d.astype(np.uint32) for d in data), 3, byte=True)


class TestIterDataStopIdx(unittest.TestCase):
    def test_iter_data_stop_idx(self):
        data = []
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 0)), data)
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 5)), data)
        data = [b'a']
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 0)), [])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 1)), data)
        data = [b'abc']
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 0)), [])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 1)), [b'a'])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 2)), [b'ab'])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 3)), data)
        data = [b'a', b'b', b'c']
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 0)), [])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 1)), [b'a'])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 2)), [b'a', b'b'])
        self.assertEqual(list(iterext.iter_data_stop_idx((d for d in data), 3)), [b'a', b'b', b'c'])


class TestNestedGroupby(unittest.TestCase):

    @unittest.skip('Not implemented.')
    def test_nested_groupby(self):
        pass


class TestIterData(unittest.TestCase):
    def test_iter_data(self):
        data_gen = []
        self.assertEqual(list(iterext.iter_data(data_gen)), data_gen)
        data_gen = [b'abc']
        self.assertEqual(list(iterext.iter_data(data_gen)), data_gen)
        data_gen = [b'a', b'', b'c']
        self.assertEqual(list(iterext.iter_data(data_gen)), data_gen)
        data_gen = [b'a', None, b'c']
        self.assertEqual(list(iterext.iter_data(data_gen)), [b'a', b'c'])
        array1 = np.arange(4)
        array2 = np.arange(4, 8)
        data_gen = [array1, None, array2]
        self.assertEqual(list(iterext.iter_data(data_gen)), [array1, array2])


class TestIterDtype(unittest.TestCase):
    def test_iter_dtype(self):
        for iterable in [[], [b'abc'], [b'a', b'b', b'c']]:
            self.assertEqual(list(iterext.iter_dtype(iterable)), iterable)
        array = np.arange(3)
        self.assertEqual(list(iterext.iter_dtype([array])), [array.tostring()])
        self.assertEqual(list(iterext.iter_dtype([array], dtype=None)), [array.tostring()])
        dtype = np.uint8
        result = list(iterext.iter_dtype([array], dtype=dtype))
        self.assertEqual(len(result), 1)
        self.assertTrue(np.all(result[0] == array.view(dtype)))
        result = list(iterext.iter_dtype([array], dtype=dtype, cast=True))
        self.assertEqual(len(result), 1)
        self.assertTrue(np.all(result[0] == array.astype(dtype)))
        data = b'abc'
        result = list(iterext.iter_dtype([data], dtype=dtype))
        self.assertEqual(len(result), 1)
        self.assertTrue(np.all(result[0] == np.frombuffer(data, dtype=dtype)))

