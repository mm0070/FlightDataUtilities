# cython: language_level=3, boundscheck=False
'''
Cython-specific functions intended for optimal performance.
'''
import cython
from libc.limits cimport LLONG_MIN
from libc.stdio cimport fprintf, stderr
import numpy as np
cimport numpy as np

from flightdatautilities.array import Value

np.import_array()  # required for calling PyArray_* functions

'''
NONE_IDX is a C integer constant used to represent None/no index. This is used instead of Python None where performance is
critical or the Global Interpreter Lock is turned off. While -1 would be the traditional value representing no index in C, since
negative indexing is Pythonic the minimum value of Py_ssize_t (-9223372036854775808) is used as this is not a feasible index for
any practical purpose (instantiating a char array of this size would require 8 exabytes of memory). The operating system
independent C type corresponding to Py_ssize_t is long long as this is consistently 8 bytes (Py_ssize_t size) on both Windows and
Unix.
'''
NONE_IDX = LLONG_MIN


################################################################################
# Memory Allocation

@cython.wraparound(False)
cdef np.int32_t[:] empty_int32(np.npy_intp size):
    '''
    Return a new one-dimensional np.int32 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:, :] empty2d_int32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int32 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:] zeros_int32(np.npy_intp size):
    '''
    Return a new one-dimensional np.int32 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:, :] zeros2d_int32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int32 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.empty (Python call).
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int64_t[:] empty_int64(np.npy_intp size):
    '''
    Return a new one-dimensional np.int64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:, :] empty2d_int64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:] zeros_int64(np.npy_intp size):
    '''
    Return a new one-dimensional np.int64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:, :] zeros2d_int64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.empty (Python call).
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.intp_t[:] empty_intp(np.npy_intp size):
    '''
    Return a new one-dimensional np.intp memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:, :] empty2d_intp(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.intp memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:] zeros_intp(np.npy_intp size):
    '''
    Return a new one-dimensional np.intp memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:, :] zeros2d_intp(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.intp memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.uint8_t[:] empty_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:, :] empty2d_uint8(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint8 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:] zeros_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:, :] zeros2d_uint8(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint8 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:] ones_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, filled with ones.

    OPT: ~2.5x faster than creating a memoryview from np.ones
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    cdef np.uint8_t[:] data = np.PyArray_ZEROS(1, shape, np.NPY_UINT8, False)
    data[...] = 1
    return data


@cython.wraparound(False)
cdef np.uint16_t[:] empty_uint16(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint16 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:, :] empty2d_uint16(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint16 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:] zeros_uint16(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint16 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:, :] zeros2d_uint16(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint16 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint32_t[:] empty_uint32(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint32 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:, :] empty2d_uint32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint32 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty``
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:] zeros_uint32(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint32 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:, :] zeros2d_uint32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint32 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint64_t[:] empty_uint64(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:, :] empty2d_uint64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty``
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:] zeros_uint64(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:, :] zeros2d_uint64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.float64_t[:] empty_float64(np.npy_intp size):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:, :] empty2d_float64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, without initializing entries.

    OPT: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:] zeros_float64(np.npy_intp size):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:, :] zeros2d_float64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.float64 memoryview of given size, filled with zeros.

    OPT: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_FLOAT64, False)


################################################################################
# Unpacking data types

@cython.wraparound(False)
cdef np.uint16_t unpack_uint16_le_unsafe(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.

    Unsafe:
    - idx must be within array bounds and non-negative
    '''
    return (data[idx + 1] << 8) + data[idx]


@cython.wraparound(False)
cdef np.uint16_t unpack_uint16_le(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.
    '''
    idx = array_wraparound_idx(idx, data.shape[0])
    if not within_bounds(idx, data.shape[0] - sizeof(np.uint16_t) + 1):
        return 0
    return unpack_uint16_le_unsafe(data, idx)


@cython.wraparound(False)
cdef np.uint16_t unpack_uint16_be_unsafe(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a big-endian unsigned short from an unsigned byte array.

    Unsafe:
    - idx must be within array bounds and non-negative
    '''
    return (data[idx] << 8) + data[idx + 1]


@cython.wraparound(False)
cdef np.uint16_t unpack_uint16_be(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.
    '''
    idx = array_wraparound_idx(idx, data.shape[0])
    if not within_bounds(idx, data.shape[0] - sizeof(np.uint16_t) + 1):
        return 0
    return unpack_uint16_be_unsafe(data, idx)


@cython.wraparound(False)
cdef np.uint32_t unpack_uint32_le_unsafe(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned integer from an unsigned byte array.

    Unsafe:
    - idx must be within array bounds and non-negative
    '''
    return (data[idx + 3] << 24) + (data[idx + 2] << 16) + (data[idx + 1] << 8) + data[idx]


@cython.wraparound(False)
cdef np.uint32_t unpack_uint32_le(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.
    '''
    idx = array_wraparound_idx(idx, data.shape[0])
    if not within_bounds(idx, data.shape[0] - sizeof(np.uint32_t) + 1):
        return 0
    return unpack_uint32_le_unsafe(data, idx)


@cython.wraparound(False)
cdef np.uint32_t unpack_uint32_be_unsafe(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a big-endian unsigned integer from an unsigned byte array.

    Unsafe:
    - idx must be within array bounds and non-negative
    '''
    return (data[idx] << 24) + (data[idx + 1] << 16) + (data[idx + 2] << 8) + data[idx + 3]


@cython.wraparound(False)
cdef np.uint32_t unpack_uint32_be(const np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.
    '''
    idx = array_wraparound_idx(idx, data.shape[0])
    if not within_bounds(idx, data.shape[0] - sizeof(np.uint32_t) + 1):
        return 0
    return unpack_uint32_be_unsafe(data, idx)


################################################################################
# Array helpers


cdef astype(data, dtype=np.float64, copy=False):
    '''
    Casts array or memoryview as dtype.
    '''
    return np.asarray(data).astype(dtype, copy=copy)


cdef bint lengths_match(Py_ssize_t x, Py_ssize_t y) nogil:
    '''
    Returns whether or not two array lengths match. To be called from nogil contexts where the array lengths are
    expected to match, e.g. data and mask of the same masked array, and a Python exception cannot be raised.
    '''
    if x == y:
        return True
    else:
        fprintf(stderr, 'array length mismatch: %ld != %ld\n', x, y)
        return False


cdef bint within_bounds(Py_ssize_t idx, Py_ssize_t length) nogil:
    '''
    Returns whether or not an index is within the bounds of an array length.
    '''
    if 0 <= idx < length:
        return True
    else:
        fprintf(stderr, 'idx %ld outside of bounds for length %ld\n', idx, length)
        return False


cdef idx_none(Py_ssize_t idx):
    '''
    Converts idx to int or None where NONE_IDX is None for converting from Cython-optimised to Python types.
    '''
    return None if idx == NONE_IDX else idx


cdef Py_ssize_t none_idx(idx):
    '''
    Converts int or None idx to int idx where None is NONE_IDX for converting from Python to Cython-optimised types.
    '''
    return NONE_IDX if idx is None else idx


cdef Py_ssize_t array_wraparound_idx(Py_ssize_t idx, Py_ssize_t length, bint stop=False) nogil:
    '''
    Return the array idx within the length of an array converting negative indices to positive to safely turn off Cython
    wraparound indexing checks. Behaviour for invalid zero or negative lengths is undefined.
    '''
    if idx == NONE_IDX or idx >= length:
        idx = length
        if not stop:
            idx -= 1  # NONE_IDX is assumed to be a stop idx as default start idx is 0
    elif idx < 0:
        idx = length + idx if idx > -length else 0
    return idx


cdef array_idx_value(Py_ssize_t idx, array):
    '''
    Return a Value object created from an array and index. An C-style invalid index of -1 is converted to Nones.
    '''
    return Value(None, None) if idx == -1 else Value(idx, array[idx])


################################################################################
# Array index finders

@cython.wraparound(False)
cdef Py_ssize_t prev_idx_unsafe(const np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start=0) nogil:
    '''
    Return the previous index within the array which matches a value or -1 if the value is not found.
    '''
    cdef Py_ssize_t prev_idx
    for prev_idx in range(idx - 1, start - 1, -1):
        if array[prev_idx] == match:
            return prev_idx
    return NONE_IDX


@cython.wraparound(False)
cdef Py_ssize_t prev_idx(const np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start=0) nogil:
    '''
    Return the previous index within the array which matches a value or -1 if the value is not found.
    '''
    return prev_idx_unsafe(array, array_wraparound_idx(idx, array.shape[0]), match=match,
                           start=array_wraparound_idx(start, array.shape[0]))


@cython.wraparound(False)
cdef Py_ssize_t next_idx_unsafe(const np.uint8_t[:] array, Py_ssize_t idx=0, bint match=True,
                                Py_ssize_t stop=NONE_IDX) nogil:
    '''
    Return the next index within the array which matches a value or -1 if the value is not found.
    '''
    cdef Py_ssize_t next_idx
    for next_idx in range(idx, array.shape[0] if stop == NONE_IDX else stop):
        if array[next_idx] == match:
            return next_idx
    return NONE_IDX


@cython.wraparound(False)
cdef Py_ssize_t next_idx(const np.uint8_t[:] array, Py_ssize_t idx=0, bint match=True, Py_ssize_t stop=NONE_IDX) nogil:
    '''
    Return the next index within the array which matches a value or -1 if the value is not found.
    '''
    return next_idx_unsafe(array, array_wraparound_idx(idx, array.shape[0]), match=match,
                           stop=array_wraparound_idx(stop, array.shape[0], stop=True))


@cython.wraparound(False)
cdef Py_ssize_t nearest_idx_unsafe(np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start=0,
                                   Py_ssize_t stop=NONE_IDX) nogil:
    stop = array_wraparound_idx(stop, array.shape[0], stop=True)
    if not array.shape[0]:
        return NONE_IDX
    if start > idx:
        fprintf(stderr, 'warning: nearest_idx_unsafe start %ld > idx %ld\n', start, idx)
        return NONE_IDX
    if stop <= idx:
        fprintf(stderr, 'warning: nearest_idx_unsafe stop %ld <= idx %ld\n', stop, idx)
        return NONE_IDX

    if array[idx] == match:
        return idx

    cdef Py_ssize_t fwd_range = (array.shape[0] if stop == NONE_IDX else stop) - idx, rev_range = idx - start, shift

    for shift in range(1, (fwd_range if fwd_range >= rev_range else rev_range) + 1):
        if shift < fwd_range and array[idx + shift] == match:
            return idx + shift
        if shift <= rev_range and array[idx - shift] == match:
            return idx - shift
    return NONE_IDX


@cython.wraparound(False)
cdef Py_ssize_t nearest_idx(np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start=0,
                            Py_ssize_t stop=NONE_IDX) nogil:

    return nearest_idx_unsafe(array, array_wraparound_idx(idx, array.shape[0]), match=match,
                              start=array_wraparound_idx(start, array.shape[0]), stop=stop)


@cython.wraparound(False)
cdef Py_ssize_t subarray_idx_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray,
                                   Py_ssize_t start=0) nogil:
    '''
    Find the first index of a subarray within an array of dtype uint8.

    TODO: change to cy.np_types fused type once Cython supports const with fused types
    '''
    if subarray.shape[0] > array.shape[0]:
        return NONE_IDX  # this case is not automatically handled by range on Ubuntu 10.04 32-bit

    cdef Py_ssize_t array_idx, subarray_idx
    start = array_wraparound_idx(start, array.shape[0])

    for array_idx in range(array_wraparound_idx(start, array.shape[0]), array.shape[0] - subarray.shape[0] + 1):
        for subarray_idx in range(subarray.shape[0]):
            if array[array_idx + subarray_idx] != subarray[subarray_idx]:
                break
        else:
            return array_idx
    return NONE_IDX


@cython.wraparound(False)
cdef Py_ssize_t value_idx(np_types[:] array, np_types value) nogil:
    '''
    Return the first array index which matches value.

    Can be much faster than numpy operations which check the entire array.

    >>> x = np.zeros(1000000000, dtype=np.uint16)
    >>> x[100000] = 1
    >>> %timeit np.any(x == 1)
    1 loops, best of 3: 419 ms per loop
    >>> %timeit array_index_uint16(1, x) != -1
    10000 loops, best of 3: 64.2 µs per loop
    '''
    cdef Py_ssize_t idx
    for idx in range(array.shape[0]):
        if value == array[idx]:
            return idx
    return NONE_IDX


################################################################################
# Array operations

@cython.wraparound(False)
cdef np_types arrays_continuous_value(np_types[:] data1, np_types[:] data2, Py_ssize_t idx) nogil:
    '''
    Get the value of an index within the two arrays as if they were concatenated.

    :param data1: first array
    :param data2: second array concatenated after the first
    :param idx: index within the concatenated array
    :returns: value sampled from idx within the concatenated array
    '''
    return data2[idx - data1.shape[0]] if idx >= data1.shape[0] else data1[idx]


cdef np.uint8_t[:] contract_runs(np.uint8_t[:] data, Py_ssize_t size, bint match=True) nogil:
    '''
    Contract runs of matching values within an array modifying data in-place, e.g.
    contract_runs([False, True, True, True], 1) == [False, False, True, False]
    '''
    if not size:
        return data

    cdef Py_ssize_t idx, fill_idx, contracted = 0

    for idx in range(data.shape[0]):
        if data[idx] == match:
            if contracted < size:
                data[idx] = not match
            contracted += 1
        else:
            if contracted > size:
                for fill_idx in range(idx - size, idx):
                    data[fill_idx] = not match
            contracted = 0
    if contracted > size:
        for fill_idx in range(data.shape[0] - size, data.shape[0]):
            data[fill_idx] = not match

    return data


cdef np.uint8_t[:] remove_small_runs(np.uint8_t[:] data, np.float64_t seconds, np.float64_t hz=1,
                                     bint match=True) nogil:
    '''
    Remove small runs of matching values from a boolean array modifying data in-place.

    Optimised version of slices_remove_small_slices (330 times faster):
>>> from analysis_engine.library import runs_of_ones, slices_remove_small_gaps
>>> T, F = True, False
>>> x = np.array([F ,T,T,T,F,T,T,F] * 100000, dtype=np.bool)
>>> def slice_version(x):
        y = np.empty_like(x)
        for s in slices_remove_small_gaps(runs_of_ones(x), 2):
            y[s] = False
        return y
>>> %timeit slice_version(x, 2)
1 loop, best of 3: 321 ms per loop
>>> %timeit section_overlap(x, y)
1000 loops, best of 3: 954 µs per loop
    '''
    cdef Py_ssize_t size = <Py_ssize_t>(seconds * hz)
    if not size:
        return data

    cdef Py_ssize_t idx, fill_idx, samples = 0

    for idx in range(data.shape[0]):
        if data[idx] == match:
            samples += 1
        else:
            if samples <= size:
                for fill_idx in range(idx - samples, idx):
                    data[fill_idx] = not match
            samples = 0

    if samples <= size:
        for fill_idx in range((idx + 1) - samples, (idx + 1)):
            data[fill_idx] = not match

    return data
