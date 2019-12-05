# cython: language_level=3, boundscheck=False
'''
Functions for data iterables.
'''

##############################################################################
# Imports


import itertools

cimport cython
import numpy as np

from flightdatautilities.data cimport buffer as bf, types


##############################################################################
# Functions


def chunk(data_iter, Py_ssize_t size, bint flush=False):
    '''
    Unlike chunk_dtype and chunk_uint8 an iterator is required as the dtype of the underlying buffer is inferred from
    the first element of the iterator.

    :dtype data_iter: iterator
    '''
    if size <= 0:
        raise ValueError('size must be greater than 0')

    data_iter = iter(data_iter)

    try:
        first_data = next(data_iter)
    except StopIteration:
        return

    dtype = types.get_dtype(first_data)
    if dtype in {None, np.uint8}:
        yield from chunk_uint8(itertools.chain((first_data,), data_iter), size, flush=flush)  # OPT: ~8x faster
        return

    cdef bf.Buffer buff = bf.Buffer(dtype=dtype)

    def chunk_data(data):
        buff.add(data)
        while buff.size >= size:
            yield buff.read(size)

    yield from chunk_data(first_data)
    for data in data_iter:
        yield from chunk_data(data)

    if flush and buff.size:
        yield buff.read(size)


def chunk_dtype(data_iter, Py_ssize_t size, dtype=None, bint flush=False):
    if dtype is np.uint8:
        yield from chunk_uint8(data_iter, size, flush=flush)  # OPT: ~8x faster
        return

    if size <= 0:
        raise ValueError('size must be greater than 0')

    cdef bf.Buffer buff = bf.Buffer(dtype=dtype)

    for data in data_iter:
        buff.add(data)
        while buff.size >= size:
            yield buff.read(size)

    if flush and buff.size:
        yield buff.read(size)


def chunk_uint8(data_iter, Py_ssize_t size, bint flush=False):
    if size <= 0:
        raise ValueError('size must be greater than 0')

    from uuid import uuid4
    x = str(uuid4())

    cdef bf.DataBufferUint8 buff = bf.DataBufferUint8()
    for data in data_iter:
        buff.add(data)
        while buff.size >= size:
            d = buff.read(size)
            yield d

    if flush and buff.size:
        d = buff.read(size)
        yield d


def join(chunks, dtype=None):
    '''
    Join chunks of the same type of data together.

    :param chunks: Chunks of data to join together.
    :type chunks: iterable of str or array
    :param dtype: dtype to return if chunks is empty.
    :type dtype: np.dtype or None
    :returns: Chunks of data joined into a single object.
    :rtype: str or np.ndarray
    '''
    chunks = tuple(iter_data(chunks))
    if chunks:
        return types.as_dtype(np.concatenate([memoryview(c) for c in chunks]), types.get_dtype(chunks[0]))
    else:
        return np.empty(0, dtype=dtype) if dtype else b''


def iter_as_dtype(data_iter, dtype):
    return (types.as_dtype(data, dtype) for data in data_iter)


def iter_data(data_iter):
    '''
    Iterate over an iterable and yield only data.

    :type data_iter: iterable
    :rtype: iterable
    '''
    return (d for d in data_iter if types.is_data(d))


def iter_data_slice(data_iter, slice):
    return (data[slice] for data in data_iter)


def iter_data_slices(data_iter, slices):
    return ([data[s] for s in slices] for data in data_iter)


def iter_data_start_idx(data_iter, Py_ssize_t start):
    if start <= 0:
        yield from data_iter
        return

    cdef Py_ssize_t data_size, pos = 0, next_pos

    for data in data_iter:
        data_size = len(data)
        next_pos = pos + data_size
        if next_pos == start:
            break
        elif next_pos > start:
            yield from chunk(itertools.chain((data[start - pos:],), data_iter), data_size, flush=True)
            return
        pos = next_pos

    yield from data_iter


#def iter_data_byte_range(data_iter, Py_ssize_t start=0, Py_ssize_t stop=0):
    #data_iter = it.chunk_uint8(it.iter_view_dtype(self.data_iter, np.uint8))
    #if start:
        #data_iter = it.iter_data_start_idx(data_iter, start)
    #if stop:
        #data_iter = it.iter_data_stop_idx(data_iter, stop)
    #return data_iter


#@cython.cdivision(True)
#def iter_data_start_byte(data_iter, Py_ssize_t start):
    #if start <= 0:
        #yield from data_iter

    #cdef Py_ssize_t data_size, itemsize = 0, pos = 0, next_pos

    #for data in data_iter:
        #if not itemsize:
            #itemsize = types.get_itemsize(data)
            #dtype = types.get_dtype(data)
        #data_size = len(data)
        #next_pos = pos + data_size * itemsize
        #if next_pos == start:
            #break
        #elif next_pos > start:
            #if (start - pos) % itemsize:
                #if dtype is not np.uint8:
                    #data_iter = iter_as_dtype(data_iter, np.uint8)
                    #data = types.as_dtype(data, np.uint8)
                #data_iter = chunk_uint8(itertools.chain((data[start - pos:],), data_iter), data_size * itemsize,
                                        #flush=True)
                #if dtype is not np.uint8:
                    #data_iter = iter_as_dtype(data_iter, dtype)
                #break
            #else:
                #yield from chunk_dtype(itertools.chain((data[(start - pos) // itemsize:],), data_iter), data_size,
                                       #dtype=dtype, flush=True)
                #return
        #pos = next_pos

    #yield from data_iter


def iter_data_stop_idx(data_iter, Py_ssize_t stop):
    if stop <= 0:
        return
    cdef Py_ssize_t pos = 0, next_pos
    for data in data_iter:
        next_pos = pos + len(data)
        if next_pos > stop:
            yield data[:stop - pos]
            return
        yield data
        if next_pos == stop:
            return
        pos = next_pos


#@cython.cdivision(True)
#def iter_data_stop_byte(data_iter, Py_ssize_t stop):
    #cdef Py_ssize_t itemsize = 0, pos = 0, next_pos

    #for data in data_iter:
        #if not itemsize:
            #itemsize = types.get_itemsize(data)
        #next_pos = pos + len(data) * itemsize
        #if next_pos > stop:
            #yield data[:(stop - pos) // itemsize]
            #return
        #elif next_pos == stop:
            #yield data
            #return
        #else:
            #yield data
        #pos = next_pos


def iter_view_dtype(data_iter, dtype):
    return (types.view_dtype(data, dtype) for data in data_iter)


#def tolist(array):
    #'''
    #'''
    #return [a.tolist() if hasattr(a, 'tolist') else tolist(a) for a in array]

