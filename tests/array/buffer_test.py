import unittest
import numpy as np

from flightdatautilities.array import buffer as bf
from flightdatautilities import iterext


class TestBuffer(unittest.TestCase):

    def test_buffer_bytes(self):
        buff = bf.Buffer()
        self.assertEqual(buff.size, 0)
        self.assertEqual(buff.read(10), b'')
        buff.truncate(10)
        self.assertEqual(buff.size, 0)
        buff.clear()
        self.assertEqual(buff.size, 0)
        buff.add(b'')
        self.assertEqual(buff.size, 0)
        buff.add(b'a')
        self.assertEqual(buff.size, 1)
        self.assertEqual(buff.read(0), b'')
        self.assertEqual(buff.read(-1), b'')
        self.assertEqual(buff.size, 1)
        self.assertEqual(buff.peek(1), b'a')
        self.assertEqual(buff.size, 1)
        self.assertEqual(buff.read(1), b'a')
        self.assertEqual(buff.size, 0)
        buff.add(b'a')
        buff.add(b'b')
        self.assertEqual(buff.size, 2)
        buff.truncate(0)
        self.assertEqual(buff.size, 2)
        buff.truncate(-5)
        self.assertEqual(buff.size, 2)
        buff.truncate(1)
        self.assertEqual(buff.size, 1)
        buff.truncate(5)
        self.assertEqual(buff.size, 0)
        buff.add(b'testing')
        buff.add(b'the')
        buff.add(b'buffer')
        self.assertEqual(buff.size, 16)
        self.assertEqual(buff.peek(2), b'te')
        self.assertEqual(buff.size, 16)
        self.assertEqual(buff.read(2), b'te')
        self.assertEqual(buff.size, 14)
        buff.truncate(7)
        self.assertEqual(buff.size, 7)
        self.assertEqual(buff.peek(5), b'ebuff')
        self.assertEqual(buff.size, 7)
        self.assertEqual(buff.read(5), b'ebuff')
        self.assertEqual(buff.size, 2)

    def test_buffer_array(self):
        buff = bf.Buffer(dtype=np.uint8)
        self.assertEqual(buff.size, 0)
        data = buff.read(10)
        self.assertEqual(data.dtype, np.uint8)
        self.assertEqual(len(data), 0)
        buff.add(np.zeros(0, dtype=np.uint8))
        self.assertEqual(buff.size, 0)
        buff.add(np.array([5], dtype=np.uint8))
        self.assertEqual(buff.size, 1)
        self.assertEqual(buff.peek(1).tolist(), [5])
        self.assertEqual(buff.size, 1)
        self.assertEqual(buff.read(1).tolist(), [5])
        self.assertEqual(buff.size, 0)
        buff.add(np.array([3], dtype=np.uint8))
        buff.add(np.array([8], dtype=np.uint8))
        self.assertEqual(buff.size, 2)
        buff.truncate(0)
        self.assertEqual(buff.size, 2)
        buff.truncate(1)
        self.assertEqual(buff.size, 1)
        buff.truncate(5)
        self.assertEqual(buff.size, 0)
        buff.add(np.arange(0, 7, dtype=np.uint8))
        buff.add(np.arange(20, 23, dtype=np.uint8))
        buff.add(np.arange(30, 36, dtype=np.uint8))
        self.assertEqual(buff.size, 16)
        self.assertEqual(buff.peek(2).tolist(), [0, 1])
        self.assertEqual(buff.size, 16)
        self.assertEqual(buff.read(2).tolist(), [0, 1])
        self.assertEqual(buff.size, 14)
        buff.truncate(7)
        self.assertEqual(buff.size, 7)
        self.assertEqual(buff.peek(5).tolist(), [22, 30, 31, 32, 33])
        self.assertEqual(buff.size, 7)
        self.assertEqual(buff.read(5).tolist(), [22, 30, 31, 32, 33])
        self.assertEqual(buff.size, 2)


class TestChunk(unittest.TestCase):
    def test_chunk_bytes_without_slices(self):
        data = [b'123', b'45', b'6', b'', b'789']
        self.assertRaises(ValueError, list, bf.chunk(data, 0))
        self.assertEqual(list(bf.chunk(data, 1)), [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9'])
        self.assertEqual(list(bf.chunk(data, 2)), [b'12', b'34', b'56', b'78'])
        self.assertEqual(list(bf.chunk(data, 2, flush=True)), [b'12', b'34', b'56', b'78', b'9'])
        self.assertEqual(list(bf.chunk(data, 3)),  [b'123', b'456', b'789'])
        self.assertEqual(list(bf.chunk(data, 3, flush=True)),  [b'123', b'456', b'789'])
        self.assertEqual(list(bf.chunk(data, 20)), [])
        self.assertEqual(list(bf.chunk(data, 20, flush=True)), [b''.join(data)])

    def test_chunk_array_without_slices(self):
        data = [np.array([1,2,3]), np.array([4,5]), np.array([6]), np.array([]), np.array([7,8,9])]
        self.assertEqual(iterext.tolist(bf.chunk(data, 3, dtype=np.int64)), [[1,2,3], [4,5,6], [7,8,9]])
        self.assertEqual(iterext.tolist(bf.chunk(data, 20, dtype=np.int64)), [])
        self.assertEqual(iterext.tolist(bf.chunk(data, 20, dtype=np.int64, flush=True)), iterext.tolist([np.concatenate(data)]))

    def test_chunk_bytes_with_slices(self):
        data = [b'123', b'45', b'6', b'', b'789']
        slices = [slice(0, 2), slice(2, 3)]
        self.assertRaises(ValueError, list, bf.chunk(data, 0, slices=slices))
        self.assertEqual(list(bf.chunk(data, 3, slices=slices)), [[b'12', b'3'], [b'45', b'6'], [b'78', b'9']])
        self.assertEqual(list(bf.chunk(data, 3, slices=slices, flush=True)), [[b'12', b'3'], [b'45', b'6'], [b'78', b'9']])
        self.assertEqual(list(bf.chunk(data, 8, slices=slices)), [[b'12', b'3']])
        self.assertEqual(list(bf.chunk(data, 8, slices=slices, flush=True)), [[b'12', b'3'], [b'9', b'']])
        self.assertEqual(list(bf.chunk(data, 20, slices=slices)), [])
        self.assertEqual(list(bf.chunk(data, 20, slices=slices, flush=True)), [[b'12', b'3']])

    def test_chunk_array_with_slices(self):
        data = [np.array([1,2,3]), np.array([4,5]), np.array([6]), np.array([]), np.array([7,8,9])]
        slices = [slice(0, 2), slice(2, 3)]
        self.assertEqual(iterext.tolist(bf.chunk(data, 3, dtype=np.int64, slices=slices, flush=True)), [[[1,2], [3]], [[4,5], [6]], [[7,8], [9]]])
        self.assertEqual(iterext.tolist(bf.chunk(data, 8, dtype=np.int64, slices=slices)), [[[1,2], [3]]])
        self.assertEqual(iterext.tolist(bf.chunk(data, 8, dtype=np.int64, slices=slices, flush=True)), [[[1,2], [3]], [[9], []]])
        self.assertEqual(iterext.tolist(bf.chunk(data, 20, dtype=np.int64, slices=slices)), [])
        self.assertEqual(iterext.tolist(bf.chunk(data, 20, dtype=np.int64, slices=slices, flush=True)), [[[1,2], [3]]])
