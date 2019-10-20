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


@cython.wraparound(False)
cdef np.int32_t[:] empty_int32(np.npy_intp size):
    '''
    Return a new one-dimensional np.int32 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:, :] empty2d_int32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int32 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:] zeros_int32(np.npy_intp size):
    '''
    Return a new one-dimensional np.int32 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int32_t[:, :] zeros2d_int32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int32 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.empty (Python call).
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INT32, False)


@cython.wraparound(False)
cdef np.int64_t[:] empty_int64(np.npy_intp size):
    '''
    Return a new one-dimensional np.int64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:, :] empty2d_int64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:] zeros_int64(np.npy_intp size):
    '''
    Return a new one-dimensional np.int64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.int64_t[:, :] zeros2d_int64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.int64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.empty (Python call).
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INT64, False)


@cython.wraparound(False)
cdef np.intp_t[:] empty_intp(np.npy_intp size):
    '''
    Return a new one-dimensional np.intp memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:, :] empty2d_intp(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.intp memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:] zeros_intp(np.npy_intp size):
    '''
    Return a new one-dimensional np.intp memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.intp_t[:, :] zeros2d_intp(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.intp memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_INTP, False)


@cython.wraparound(False)
cdef np.uint8_t[:] empty_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:, :] empty2d_uint8(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint8 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:] zeros_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:, :] zeros2d_uint8(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint8 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT8, False)


@cython.wraparound(False)
cdef np.uint8_t[:] ones_uint8(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint8 memoryview of given size, filled with ones.

    opt: ~2.5x faster than creating a memoryview from np.ones
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT8, False) + 1


@cython.wraparound(False)
cdef np.uint16_t[:] empty_uint16(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint16 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:, :] empty2d_uint16(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint16 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:] zeros_uint16(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint16 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint16_t[:, :] zeros2d_uint16(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint16 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT16, False)


@cython.wraparound(False)
cdef np.uint32_t[:] empty_uint32(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint32 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:, :] empty2d_uint32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint32 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty``
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:] zeros_uint32(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint32 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint32_t[:, :] zeros2d_uint32(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint32 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT32, False)


@cython.wraparound(False)
cdef np.uint64_t[:] empty_uint64(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:, :] empty2d_uint64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty``
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:] zeros_uint64(np.npy_intp size):
    '''
    Return a new one-dimensional np.uint64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.uint64_t[:, :] zeros2d_uint64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.uint64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_UINT64, False)


@cython.wraparound(False)
cdef np.float64_t[:] empty_float64(np.npy_intp size):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_EMPTY(1, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:, :] empty2d_float64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, without initializing entries.

    opt: ~2.5x faster than creating a memoryview from np.empty
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_EMPTY(2, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:] zeros_float64(np.npy_intp size):
    '''
    Return a new one-dimensional np.float64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[1]
    shape[0] = size
    return np.PyArray_ZEROS(1, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.float64_t[:, :] zeros2d_float64(np.npy_intp x, np.npy_intp y):
    '''
    Return a new two-dimensional np.float64 memoryview of given size, filled with zeros.

    opt: ~2.5x faster than creating a memoryview from np.zeros
    '''
    cdef np.npy_intp shape[2]
    shape[0] = x
    shape[1] = y
    return np.PyArray_ZEROS(2, shape, np.NPY_FLOAT64, False)


@cython.wraparound(False)
cdef np.uint16_t read_uint16_le(np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned short from an unsigned byte array.
    '''
    return (data[idx + 1] << 8) + data[idx]


@cython.wraparound(False)
cdef np.uint16_t read_uint16_be(np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a big-endian unsigned short from an unsigned byte array.
    '''
    return (data[idx] << 8) + data[idx + 1]


@cython.wraparound(False)
cdef np.uint32_t read_uint32_le(np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a little-endian unsigned integer from an unsigned byte array.
    '''
    return (data[idx + 3] << 24) + (data[idx + 2] << 16) + (data[idx + 1] << 8) + data[idx]


@cython.wraparound(False)
cdef np.uint32_t read_uint32_be(np.uint8_t[:] data, Py_ssize_t idx) nogil:
    '''
    Read a big-endian unsigned integer from an unsigned byte array.
    '''
    return (data[idx] << 24) + (data[idx + 1] << 16) + (data[idx + 2] << 8) + data[idx + 3]


cdef bint lengths_mismatch(Py_ssize_t x, Py_ssize_t y) nogil:
    if x == y:
        return True
    else:
        fprintf(stderr, 'array length mismatch (%ld != %ld)\n', x, y)
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


cdef Py_ssize_t array_wraparound_idx(Py_ssize_t idx, Py_ssize_t length) nogil:
    '''
    Return the array idx within the length of an array converting negative indices to positive to safely turn off Cython
    wraparound indexing checks. Behaviour for invalid zero or negative lengths is undefined.
    '''
    if idx == NONE_IDX or idx >= length:
        idx = length - 1  # NONE_IDX is assumed to be a stop idx as default start idx is 0
    elif idx < 0:
        idx = length + idx if idx > -length else 0
    return idx


cdef Py_ssize_t array_idx(Py_ssize_t idx, Py_ssize_t length) nogil:
    '''
    Return an index truncated to the bounds of an array. Negative indices are ignored and return 0.
    '''
    if idx <= 0:
        return 0
    elif idx >= length:
        return length - 1
    else:
        return idx


cdef array_idx_value(Py_ssize_t idx, array):
    '''
    Return a Value object created from an array and index. An C-style invalid index of -1 is converted to Nones.
    '''
    return Value(None, None) if idx == -1 else Value(idx, array[idx])


cdef Py_ssize_t array_stop_idx(Py_ssize_t stop_idx, Py_ssize_t length) nogil:
    '''
    Return an array stop index truncated to the length of the array. Ignores negative indices.
    '''
    return length if stop_idx < 0 or stop_idx > length else stop_idx


@cython.wraparound(False)
cdef Py_ssize_t prev_idx(const np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start_idx=0) nogil:
    '''
    Return the previous index within the array which matches a value or -1 if the value is not found.
    '''
    idx = array_idx(idx, array.shape[0])
    start_idx = array_idx(start_idx, array.shape[0])

    cdef Py_ssize_t prev_idx

    for prev_idx in range(idx - 1, start_idx - 1, -1):
        if array[prev_idx] == match:
            return prev_idx
    return -1


@cython.wraparound(False)
cdef Py_ssize_t next_idx(const np.uint8_t[:] array, Py_ssize_t idx=0, bint match=True, Py_ssize_t stop_idx=0) nogil:
    '''
    Return the next index within the array which matches a value or -1 if the value is not found.
    '''
    idx = array_idx(idx, array.shape[0])
    stop_idx = array_stop_idx(stop_idx, array.shape[0])

    cdef Py_ssize_t next_idx

    for next_idx in range(idx, stop_idx):
        if array[next_idx] == match:
            return next_idx
    return -1


cdef Py_ssize_t nearest_idx(np.uint8_t[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start_idx=0,
                            Py_ssize_t stop_idx=-1) nogil:
    if stop_idx < 0:
        stop_idx = array.shape[0]

    idx = array_idx(idx, array.shape[0])

    if not array.shape[0] or idx < start_idx or idx >= stop_idx:
        return -1

    if array[idx] == match:
        return idx

    cdef:
        Py_ssize_t fwd_range = stop_idx - idx, rev_range = idx - start_idx, shift

    for shift in range(1, (fwd_range if fwd_range >= rev_range else rev_range) + 1):
        if shift < fwd_range and array[idx + shift] == match:
            return idx + shift
        if shift <= rev_range and array[idx - shift] == match:
            return idx - shift
    return -1


cdef np.uint8_t[:] contract_runs(np.uint8_t[:] data, Py_ssize_t size, bint match=True) nogil:
    '''
    Contract runs of matching values within an array, e.g.
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


cdef np.uint8_t[:] remove_small_runs(np.uint8_t[:] data, float seconds, float hz=1, bint match=True) nogil:
    '''
    Remove small runs of matching values from a boolean array.

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



"""

cdef np.uint16_t[:] sync_words_from_modes(modes):
    '''
    Creates an array containing sync words in a contiguous 1d-array.

    e.g. sync_words_from_modes(['717'])
    '''
    cdef:
        np.uint16_t[:] sync_words = empty_uint16(len(modes) * 4)
        Py_ssize_t sync_word_idx = 0
    for mode in modes:
        for sync_word in SYNC_PATTERNS[mode]:
            sync_words[sync_word_idx] = sync_word
            sync_word_idx += 1
    return sync_words


cpdef swap_bytes(array):
    '''
    Swap byte-order endianness.

    >>> swap_bytes(np.fromstring(b'\x12\x34\x56\x78')).tostring()
    b'\x34\x12\x78\x56'

    :param array: Array to be byte-swapped.
    :type array: np.ndarray
    :returns: Array after byte-order has been swapped.
    :rtype: np.ndarray
    '''
    return array.byteswap(True)


cpdef unpack(array):
    '''
    Unpack 'packed' flight data into unpacked (byte-aligned) format.

    :type array: np.ndarray(dtype=np.uint8)
    :rtype: np.ndarray(dtype=np.uint8)
    '''
    if len(array) % 3:
        array = array[:len(array) // 3 * 3]
    unpacked = np.empty(len(array) // 3 * 4, dtype=np.uint8)
    unpacked[::4] = array[::3]
    unpacked[1::4] = array[1::3] & 0x0F
    unpacked[2::4] = ((array[2::3] & 0x0F) << 4) + ((array[1::3] & 0xF0) >> 4)
    unpacked[3::4] = (array[2::3] & 0xF0) >> 4
    return unpacked


cpdef np.uint16_t[:] unpack_little_endian(np.uint8_t[:] data):
    '''
    b'24705c' -> b'47025c00'
    '''
    if data.shape[0] % 3 != 0:
        raise ValueError('data length must be a multiple of 3')

    cdef:
        np.uint16_t[:] output = zeros_uint16(<Py_ssize_t>(data.shape[0] // 1.5))
        Py_ssize_t data_idx = 0, output_idx = 0

    while data_idx < data.shape[0]:  # cython range with step is slow
        output[output_idx] = ((data[data_idx] & 0b11110000) << 4) | ((data[data_idx] & 0b1111) << 4) | (data[data_idx + 1] >> 4)
        output[output_idx + 1] = ((data[data_idx + 1] & 0b1111) << 8) | data[data_idx + 2]
        data_idx += 3
        output_idx += 2

    return output


cpdef pack(array):
    '''
    Pack 'unpacked' flight data into packed format.

    :type array: np.ndarray(dtype=np.uint8)
    :rtype: np.ndarray(dtype=np.uint8)
    '''
    packed = np.empty(len(array) // 4 * 3, dtype=np.uint8)
    packed[::3] = array[::4]
    packed[1::3] = array[1::4] + ((array[2::4] & 0x0F) << 4)
    packed[2::3] = (array[3::4] << 4) + ((array[2::4] & 0xF0) >> 4)
    return packed


cpdef bytes key_value(np.uint8_t[:] array, key, delimiter, separator, Py_ssize_t start=0):
    '''
    Find the value of a key in the format:

    <key><delimiter><value><separator>

    :param array: Array in which the key value pair will be searched for.
    :type array: np.array(dtype=np.uint8)
    :param key: Key to find a value for.
    :type key: str
    :param delimiter: Delimiter char(s) which appear between the key and value, e.g. '=' for 'key=value',
    :type delimiter: str
    :param separator: Line separator for key value pairs, e.g. '\x0D' for 'k1=v1\x0Dk2=v2'
    :type separator: str
    :param start: Start index within the array to search from.
    :type start: int
    :returns: The value for the key if found, else None.
    :rtype: str or None
    '''
    key_idx = index_of_subarray_uint8(array, np.fromstring(key, dtype=np.uint8), start=start)
    if key_idx == -1:
        return None
    start_idx = index_of_subarray_uint8(array, np.fromstring(delimiter, dtype=np.uint8), start=key_idx) + len(delimiter)
    stop_idx = index_of_subarray_uint8(array, np.fromstring(separator, dtype=np.uint8), start=start_idx)
    return np.asarray(array[start_idx:stop_idx]).tostring().strip()


cpdef Py_ssize_t index_of_subarray_uint8(np.uint8_t[:] array, np.uint8_t[:] subarray, Py_ssize_t start=0) nogil:
    '''
    Find the first index of a subarray within an array of dtype uint8.

    :param start: start index to search within array (positive integer or 0)
    :returns:
    '''
    cdef Py_ssize_t array_idx, subarray_idx

    if subarray.shape[0] > array.shape[0]:
        # This case is not automatically handled by range on Ubuntu 10.04 32-bit.
        return -1

    for array_idx in range(start, array.shape[0] - subarray.shape[0] + 1):
        for subarray_idx in range(subarray.shape[0]):
            if array[array_idx + subarray_idx] != subarray[subarray_idx]:
                break
        else:
            return array_idx
    return -1


cpdef Py_ssize_t array_index_uint16(unsigned short value, np.uint16_t[:] array) nogil:
    '''
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
    return -1


def extrap1d(interpolator):
    '''
    Extends scipy.interp1d which extrapolates values outside of the interpolation points.
    http://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-a-an-extrapolated-result-beyond-the-input-ran
    Optimised interpolation with extrapolation has been implemented in Interpolator.
    '''
    xs = interpolator.x
    ys = interpolator.y

    def pointwise(x):
        if x < xs[0]:
            return ys[0] + (x - xs[0]) * (ys[1] - ys[0]) / (xs[1] - xs[0])
        elif x > xs[-1]:
            return ys[-1] + (x - xs[-1]) * (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
        else:
            return interpolator(x)

    def ufunclike(xs):
        return scipy.array(map(pointwise, scipy.array(xs)))

    return ufunclike


cpdef merge_masks(masks):
    '''
    ORs multiple masks together. Could this be done in one step with numpy?

    :param masks: Masks to OR together.
    :type masks: iterable of np.ma.masked_array.mask
    :raises IndexError: If masks is empty.
    :returns: Single mask, the result of ORing masks.
    :rtype: np.ma.masked_array.mask
    '''
    merged_mask = np.ma.make_mask(masks[0])
    for mask in masks[1:]:
        merged_mask = np.ma.mask_or(merged_mask, mask)
    return merged_mask


cpdef mask_ratio(mask):
    '''
    Ratio of masked data (1 == all masked).
    '''
    # Handle scalars.
    if np.all(mask):
        return 1
    elif not np.any(mask):
        return 0
    return mask.sum() / float(len(mask))


cpdef percent_unmasked(mask):
    '''
    Percentage of unmasked data.
    '''
    return (1 - mask_ratio(mask)) * 100


cpdef sum_arrays(arrays):
    '''
    Sums multiple numpy arrays together.

    :param arrays: Arrays to sum.
    :type arrays: iterable of np.ma.masked_array
    :raises IndexError: If arrays is empty.
    :returns: The result of summing arrays.
    :rtype: np.ma.masked_array
    '''
    summed_array = arrays[0]
    for array in arrays[1:]:
        summed_array += array
    return summed_array


cpdef downsample_arrays(arrays):
    '''
    Return arrays downsampled to the size of the smallest.

    :param arrays: Arrays to downsample.
    :type arrays: iterable of np.ndarray or np.ma.masked_array
    :returns: Arrays downsampled to the size of the smallest.
    :rtype: iterable of np.ma.masked_array
    '''
    lengths = [len(x) for x in arrays]
    shortest = min(lengths)
    if shortest == max(lengths):
        return arrays

    for length in lengths:
        if length % shortest:
            raise ValueError(f"Arrays lengths '{lengths}' should be multiples of the shortest.")
    downsampled_arrays = []
    for array in arrays:
        step = len(array) // shortest
        if step > 1:
            array = array[::step]
        downsampled_arrays.append(array)
    return downsampled_arrays


cpdef upsample_arrays(arrays):
    '''
    Return arrays upsampled to the size of the largest.

    :param arrays: Arrays to upsample.
    :type arrays: iterable of np.ma.masked_array
    :raises ValueError: If array lengths are not multiples.
    :returns: Arrays upsampled to the size of the largest.
    :rtype: iterable of np.ma.masked_array
    '''
    lengths = [1 if np.isscalar(a) else len(a) for a in arrays]
    largest = max(lengths)
    if largest == min(lengths):
        return arrays

    for length in lengths:
        if largest % length:
            raise ValueError(f"The largest array length should be a multiple of all others '{lengths}'.")

    upsampled_arrays = []
    for array, length in zip(arrays, lengths):
        # XXX: Hack to fix MappedArray values mapping being stripped by repeat.
        values_mapping = getattr(array, 'values_mapping', None)
        repeat = largest // length
        if repeat > 1:
            array = array.repeat(repeat)
            if values_mapping:
                array.values_mapping = values_mapping
        upsampled_arrays.append(array)
    return upsampled_arrays


cpdef align_arrays(slave_array, master_array):
    '''
    Very basic aligning using repeat to upsample and skipping over samples to
    downsample the slave array to the master frequency

    >>> align_arrays(np.arange(10), np.arange(20,30))  # equal length
    array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> align_arrays(np.arange(40,80), np.arange(20,40))  # downsample every other
    array([40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78])
    >>> align_arrays(np.arange(40,80), np.arange(30,40))  # downsample every 4th
    array([40, 44, 48, 52, 56, 60, 64, 68, 72, 76])
    >>> align_arrays(np.arange(10), np.arange(20,40))  # upsample
    array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9])
    '''
    ratio = len(master_array) / len(slave_array)
    if ratio == 1:
        # nothing to do
        return slave_array
    if ratio > 1:
        # repeat slave to upsample
        # Q: Upsample using repeat good enough, or interpolate?
        return slave_array.repeat(ratio)
    else:
        # take every other sample to downsample
        return slave_array[0::int(1 // ratio)]


cpdef save_compressed(path, array):
    '''
    Save either a MappedArray, np.ma.MaskedArray or np.ndarray in a compressed archive.
    '''
    try:
        from flightdataaccessor import MappedArray
    except ImportError:
        pass
    else:
        if isinstance(array, MappedArray):
            np.savez_compressed(
                path,
                np.array(array.values_mapping),
                array.data,
                array.mask,
            )
            return
    if isinstance(array, np.ma.MaskedArray):
        np.savez_compressed(path, array.data, array.mask)
    elif isinstance(array, np.ndarray):
        np.savez_compressed(path, array)
    else:
        raise NotImplementedError(f"Object of type '{type(array)}' cannot be saved.")


cpdef load_compressed(path):
    '''
    Load either a MappedArray, np.ma.MaskedArray or np.ndarray from a compressed archive.
    '''
    array_dict = np.load(path)
    array_count = len(array_dict.keys())
    if array_count == 3:
        from flightdataaccessor import MappedArray
        values_mapping = array_dict['arr_0'].item()
        raw_array = np.ma.masked_array(array_dict['arr_1'], mask=array_dict['arr_2'])
        array = MappedArray(raw_array, values_mapping=values_mapping)
    elif array_count == 2:
        array = np.ma.MaskedArray(array_dict['arr_0'], mask=array_dict['arr_1'])
    elif array_count == 1:
        array = array_dict['arr_0']
    else:
        raise NotImplementedError(f'Unknown array type with {array_count} components.')
    return array


cpdef bint is_power2(number):
    '''
    Whether or not a number is a power of two. Forces floats to int.
    Ref: http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/

    opt: ~4x faster than pure python version
    '''
    if number % 1:
        return False
    cdef int num = <int>number
    return num > 0 and ((num & (num - 1)) == 0)


cpdef is_power2_fraction(number):
    '''
    Whether or not a number is a power of two or one divided by a power of two.

    :type number: int or float
    :returns: if the number is either a power of 2 or a fraction, e.g. 4, 2, 1, 0.5, 0.25
    :rtype: bool
    '''
    if 0 < number < 1:
        number = 1 / number
    return is_power2(number)


cpdef np.ndarray twos_complement(np.ndarray array, np.uint64_t bit_length):
    '''
    Convert the values from "sign bit" notation to "two's complement".
    '''
    array[array > saturated_value(bit_length - 1)] -= saturated_value(bit_length) + 1
    return array
"""