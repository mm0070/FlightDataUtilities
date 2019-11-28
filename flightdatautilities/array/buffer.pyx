# cython: language_level=3, boundscheck=False
from collections import deque

import numpy as np


cdef class Buffer:

    def __init__(self, dtype=None):
        self._array = bool(dtype)
        self._empty = np.zeros(0, dtype=dtype) if self._array else b''
        self._chunks = deque()

    cdef _join(self, chunks):
        return np.concatenate(chunks) if self._array else b''.join(chunks)

    cpdef clear(self):
        self._chunks.clear()
        self.size = 0

    cpdef add(self, data):
        cdef Py_ssize_t data_size = len(data)
        if not data_size:
            return
        self.size += data_size
        self._chunks.append(data)

    cpdef truncate(self, Py_ssize_t size):
        if size <= 0 or not self.size:
            return
        elif size >= self.size:
            self.clear()
            return
        cdef Py_ssize_t chunk_size
        while True:
            chunk_size = len(self._chunks[0])
            if size >= chunk_size:
                self._chunks.popleft()
                self.size -= chunk_size
                size -= chunk_size
            else:
                if size:
                    self._chunks[0] = self._chunks[0][size:]
                    self.size -= size
                break

    cpdef peek(self, Py_ssize_t size):
        if size <= 0 or not self.size:
            return self._empty
        elif size >= self.size:
            return self._join(self._chunks)

        cdef Py_ssize_t chunk_size = len(self._chunks[0])
        if size < chunk_size:
            return self._chunks[0][:size]

        peek_chunks = []
        for chunk in self._chunks:
            if not peek_chunks:
                peek_chunks.append(chunk)
                size -= chunk_size
                continue
            chunk_size = len(chunk)
            if size >= chunk_size:
                peek_chunks.append(chunk)
                if size == chunk_size:
                    break
                size -= chunk_size
            elif size:
                peek_chunks.append(chunk[:size])
                break

        return self._join(peek_chunks)

    cpdef read(self, Py_ssize_t size):
        if size <= 0 or not self.size:
            return self._empty
        elif size >= self.size:
            data = self._join(self._chunks)
            self.clear()
            return data

        cdef Py_ssize_t chunk_size = len(self._chunks[0])
        if size < chunk_size:
            data = self._chunks[0][:size]
            self._chunks[0] = self._chunks[0][size:]
            self.size -= size
            return data

        read_chunks = []
        while True:
            if size >= chunk_size:
                read_chunks.append(self._chunks.popleft())
                self.size -= chunk_size
                if size == chunk_size:
                    break
                size -= chunk_size
            elif size:
                read_chunks.append(self._chunks[0][:size])
                self._chunks[0] = self._chunks[0][size:]
                self.size -= size
                break
            chunk_size = len(self._chunks[0])

        return self._join(read_chunks)


def chunk(data_gen, Py_ssize_t size, dtype=None, slices=None, bint flush=False):
    '''
    Split the data into even size chunks. Optionally slice within the data. Convenient, but not efficient.

    TODO: Possibly create a Chunk generator class which stores the args and kwargs as attributes to avoid re-chunking and unnecessary copying.

    :param data_gen: Generator yielding data.
    :type data_gen: generator or iterable
    :param size: Size to chunk the data into.
    :param slices: Slices to apply to each chunk, e.g. header and footer data.
    :type slices: iterable or slice or None
    :param flush: Flush remaining data. Will result in incomplete slices.
    :yields: List of sliced data chunks if slices else entire data chunks based on size.
    '''
    if size <= 0:
        raise ValueError('size must be greater than 0')
    if slices is None:
        output = lambda x: x  # return data unchanged
    elif isinstance(slices, slice):
        output = lambda x: x[slices]  # return slice
    else:
        output = lambda x: [x[s] for s in slices]  # return list of slices

    buff = Buffer(dtype=dtype)
    for data in data_gen:
        buff.add(data)

        while buff.size >= size:
            yield output(buff.read(size))

    if flush and buff.size:
        yield output(buff.read(size))