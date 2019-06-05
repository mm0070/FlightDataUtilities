# cython: language_level=3, boundscheck=False

'''
# Slice Replacement

## is_index_within_slice() & is_index_within_slices() & find_slices_containing_index()

matching[idx]

## filter_slices_length() & filter_slices_duration()

remove_small_runs(matching, 10, hz=2)

## find_nearest_slice()

find_nearest_slice(matching, idx)

## is_slice_within_slice()

matching[2:5].all()

## find_slices_overlap()

matching1 & matching2

## slices_overlap()

(matching1 & matching2).any()

## slices_overlap_merge()

TODO

## slices_and()

matching1 & matching2

## slices_and_not()

matching1 & ~matching2

## slices_not()

~matching

## slices_or()

matching1 | matching2

## slices_remove_overlap()

TODO

## slices_remove_small_gaps()

remove_small_gaps(matching, 10, hz=1)  # TODO

## slices_find_small_slices()

filter_small_runs(matching, 10, hz=1)  # TODO

## trim_slices()

contract_runs(matching, 10, hz=1)

## valid_slices_within_array()

matching & array.mask

## mask_inside_slices()

slices_to_array(length, slices)

## mask_outside_slices()

~slices_to_array(length, slices)
'''


'''
def masked_array_fill_start(array, max_samples=None):
    cdef long c_max_samples = max_samples if max_samples is None else -1
    if c_max_samples != -1 and c_max_samples <= 0:
        return array
'''

import numpy as np
cimport numpy as np

import scipy

from libc.math cimport ceil, fabs

from collections import namedtuple

from flightdatautilities.type import is_array
from flightdatautilities.byte_aligned import MODES, STANDARD_MODES, SYNC_PATTERNS, WPS  # TODO: move to flightdatautilities


cdef:
    #int FILL_START = 0, FILL_STOP = 1, INTERPOLATE = 2
    int MAX_VALUE = 0, MIN_VALUE = 1, MAX_ABS_VALUE = 2, MIN_ABS_VALUE = 3


Value = namedtuple('Value', 'index value')


cdef object idx_none(Py_ssize_t idx):
    return None if idx == -1 else idx


cdef Py_ssize_t none_idx(idx):
    return -1 if idx is None else idx


cdef Py_ssize_t cython_nearest_idx(unsigned char[:] array, Py_ssize_t idx, bint match=True, Py_ssize_t start_idx=-1, Py_ssize_t stop_idx=-1) nogil:
    if start_idx == -1:
        start_idx = 0
    if stop_idx == -1:
        stop_idx = array.shape[0]

    if idx < 0:
        idx = 0
    elif idx >= array.shape[0]:
        idx = array.shape[0] - 1

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


def nearest_idx(array, long idx, bint match=True, start_idx=None, stop_idx=None):
    return idx_none(cython_nearest_idx(
        array.view(np.uint8), idx, match=match,
        start_idx=none_idx(start_idx),
        stop_idx=none_idx(stop_idx),
    ))


def nearest_slice(array, Py_ssize_t idx, bint match=True):
    cdef unsigned char[:] data = array.view(np.uint8)
    cdef Py_ssize_t start_idx, stop_idx, nearest_idx = cython_nearest_idx(data, idx, match=match)

    if nearest_idx == -1:
        return None

    if nearest_idx == idx:
        for stop_idx in range(idx + 1, data.shape[0]):
            if not data[stop_idx]:
                break
        else:
            stop_idx = data.shape[0]  # end of array (exclusive)

        for start_idx in range(idx - 1, -1, -1):
            if not data[start_idx]:
                start_idx += 1
                break
        else:
            start_idx = 0
    elif nearest_idx > idx:
        # nearest slice starts at a later idx, scan forward to find slice stop
        start_idx = nearest_idx
        for stop_idx in range(start_idx + 1, data.shape[0]):
            if data[stop_idx] != match:
                break
        else:
            stop_idx = data.shape[0]

    else:
        # nearest slice stops at an earlier idx, scan backwards to find slice start
        stop_idx = nearest_idx + 1
        for start_idx in range(nearest_idx, -1, -1):
            if data[start_idx] != match:
                start_idx += 1
                break
        else:
            start_idx = 0

    return slice(start_idx, stop_idx)


cdef void cython_ma_fill_range_float64(double[:] data, unsigned char[:] mask, double value, Py_ssize_t start, Py_ssize_t stop) nogil:
    cdef Py_ssize_t idx
    for idx in range(start, stop):
        data[idx] = value
        mask[idx] = 0


cdef void cython_ma_interpolate_float64(double[:] data, unsigned char[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil:
    cdef:
        double gradient = (data[stop] - data[start]) / (stop - start)
        Py_ssize_t idx
    for idx in range(start + 1, stop):
        data[idx] = data[start] + ((idx - start) * gradient)
        mask[idx] = 0


cpdef void cython_repair_mask_float64(double[:] data, unsigned char[:] mask, RepairMethod method, Py_ssize_t max_samples, bint extrapolate=False) nogil:
    cdef:
        Py_ssize_t idx, last_valid_idx = -1

    for idx in range(data.shape[0]):
        if not mask[idx]:
            if last_valid_idx != idx - 1:

                if last_valid_idx == -1:
                    if (extrapolate or method == FILL_STOP) and (max_samples == -1 or idx <= max_samples):
                        cython_ma_fill_range_float64(data, mask, data[idx], 0, idx)
                else:
                    if max_samples == -1 or idx - last_valid_idx <= max_samples:
                        if method == INTERPOLATE:
                            cython_ma_interpolate_float64(data, mask, last_valid_idx, idx)
                        else:
                            cython_ma_fill_range_float64(
                                data, mask, data[last_valid_idx] if method == FILL_START else data[idx], last_valid_idx + 1, idx)

            last_valid_idx = idx

    if (extrapolate or method == FILL_START) and last_valid_idx != -1 and last_valid_idx != idx and (max_samples == -1 or idx - last_valid_idx <= max_samples):
        cython_ma_fill_range_float64(data, mask, data[last_valid_idx], last_valid_idx + 1, data.shape[0])


def repair_mask(array, method='interpolate', repair_duration=10, frequency=1, bint copy=False, bint extrapolate=False, bint raise_duration_exceedance=False, bint raise_entirely_masked=True):
    '''
    TODO: find better solution for repair_above kwarg from original.
    '''
    cdef Py_ssize_t length, repair_samples, unmasked_samples

    unmasked_samples = np.ma.count(array)
    if unmasked_samples == 0:
        if raise_entirely_masked:
            raise ValueError('Array cannot be repaired as it is entirely masked')
        return array
    elif len(array) == unmasked_samples:
        return array

    dtype = array.dtype
    array = array.astype(np.float64)

    if copy:
        array = array.copy()

    if repair_duration:
        repair_samples = repair_duration * frequency
        if raise_duration_exceedance:
            length = longest_zeros_uint8(array.mask)
            if length > repair_samples:
                raise ValueError("Length of masked section '%s' exceeds repair duration '%s'." %
                                 (length * frequency, repair_duration))
    else:
        repair_samples = -1

    cython_repair_mask_float64(
        array.data,
        array.mask.view(np.uint8),
        {'interpolate': INTERPOLATE, 'fill_start': FILL_START, 'fill_stop': FILL_STOP}[method],
        repair_samples,
        extrapolate=extrapolate,
    )
    return array.astype(dtype)


cdef Py_ssize_t longest_zeros_uint8(unsigned char[:] mask) nogil:
    cdef Py_ssize_t idx, current_samples = 0, max_samples = 0
    for idx in range(mask.shape[0]):
        if mask[idx]:
            if current_samples > max_samples:
                max_samples = current_samples
            current_samples = 0
        else:
            current_samples += 1
    return max_samples


def aggregate_values(Aggregate mode, double[:] data, const unsigned char[:] mask, const unsigned char[:] matching):
    if data.shape[0] != mask.shape[0] or data.shape[0] != matching.shape[0]:
        raise ValueError('array lengths do not match')

    cdef:
        Py_ssize_t idx, value_idx = -1
        double value
        bint matching_section = False, update_value = False

    for idx in range(matching.shape[0]):
        if matching[idx]:
            if not matching_section:
                matching_section = True
            if not mask[idx]:
                update_value = False
                if value_idx == -1:
                    update_value = True
                elif mode == MAX:
                    if data[idx] > value:
                        update_value = True
                elif mode == MIN:
                    if data[idx] < value:
                        update_value = True
                elif mode == MAX_ABS:
                    if fabs(data[idx]) > fabs(data[idx]):
                        update_value = True
                elif mode == MIN_ABS:
                    if fabs(data[idx]) < fabs(data[idx]):
                        update_value = True
                if update_value:
                    value = data[idx]
                    value_idx = idx
        else:
            if matching_section:
                if value_idx != -1:
                    yield value_idx, value
                    value_idx = -1
                matching_section = False

    if matching_section and value_idx != -1:
        yield value_idx, value


cdef _aggregate_values(Aggregate mode, array, matching):
    return aggregate_values(
        mode,
        array.data.astype(np.float64, copy=False),
        np.ma.getmaskarray(array).view(np.uint8),
        matching.view(np.uint8),
    )


def max_values(array, matching):
    return _aggregate_values(Aggregate.MAX, array, matching)


def min_values(array, matching):
    return _aggregate_values(Aggregate.MIN, array, matching)


def max_abs_values(array, matching):
    return _aggregate_values(Aggregate.MAX_ABS, array, matching)


def min_abs_values(array, matching):
    return _aggregate_values(Aggregate.MIN_ABS, array, matching)


def slices_to_array(Py_ssize_t size, slices):
    cdef:
        unsigned char[:] array = np.zeros(size, dtype=np.uint8)
        Py_ssize_t start, stop, idx
    for s in slices:
        start = 0 if s.start is None else s.start
        stop = array.shape[0] if s.stop is None else s.stop
        if start < 0:
            start = 0
        if stop > array.shape[0]:
            stop = array.shape[0]
        for idx in range(start, stop):
            array[idx] = 1
    return np.asarray(array).view(np.uint8)


def section_overlap(a, b):
    '''
    Optimised version of ~O(N^2) (2.5 million times faster)
>>> from analysis_engine.library import runs_of_ones, slices_overlap
>>> T, F = True, False
>>> x = np.array([F,F,T,T,F,T,F,F,F,F,T,T,F] * 8000, dtype=np.bool)
>>> y = np.array([F,T,T,F,F,F,T,F,T,T,T,T,F] * 8000, dtype=np.bool)
>>> def overlap(a, b):
        out = np.zeros(len(a), dtype=np.bool)
        for s1 in runs_of_ones(a):
            for s2 in runs_of_ones(b):
                if slices_overlap(s1, s2):
                    out[s1] = True
                    out[s2] = True
        return out
>>> %timeit overlap(x, y)
1 loop, best of 3: 10min 44s per loop
>>> %timeit section_overlap(x, y)
1000 loops, best of 3: 251 µs per loop
    '''
    cdef unsigned char[:] x = a.view(np.uint8), y = b.view(np.uint8)

    if x.shape[0] != y.shape[0]:
        raise ValueError('array lengths do not match')

    cdef:
        unsigned char[:] out = np.zeros(x.shape[0], dtype=np.uint8)
        Py_ssize_t idx, rev_idx, last_idx = -1
        bint both_true, last_both_true = True, fill_either = False

    for idx in range(x.shape[0]):
        both_true = x[idx] & y[idx]
        if both_true:
            if not last_both_true:
                for rev_idx in range(idx - 1, last_idx, -1):
                    if x[rev_idx] | y[rev_idx]:
                        out[rev_idx] = True
                    else:
                        break
            last_idx = idx
            fill_either = True
            out[idx] = True
        elif x[idx] | y[idx]:
            if fill_either:
                out[idx] = True
                last_idx = idx
        else:
            fill_either = False
        last_both_true = both_true

    return np.asarray(out).view(np.uint8)


def remove_small_runs(array, Py_ssize_t seconds=10, float hz=1):  # TODO: floating point hz
    '''
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
        return array

    cdef:
        unsigned char[:] data = array.view(np.uint8)
        Py_ssize_t idx, fill_idx, samples = 0

    for idx in range(data.shape[0]):
        if data[idx]:
            samples += 1
        else:
            if samples <= size:
                for fill_idx in range(idx - samples, idx):
                    data[fill_idx] = False
            samples = 0

    if samples <= size:
        for fill_idx in range((idx + 1) - samples, (idx + 1)):
            data[fill_idx] = False

    return np.asarray(data).view(np.bool)


def contract_runs(array, Py_ssize_t size):
    '''
    Contract runs of True values within arrays, e.g.
    contract_runs([False, True, True, True], 1) == [False, False, True, False]
    '''
    if not size:
        return array

    cdef:
        unsigned char[:] data = array.view(np.uint8)
        Py_ssize_t idx, fill_idx, contracted = 0

    for idx in range(data.shape[0]):
        if data[idx]:
            if contracted < size:
                data[idx] = False
            contracted += 1
        else:
            if contracted > size:
                for fill_idx in range(idx - size, idx):
                    data[fill_idx] = False
            contracted = 0
    if contracted > size:
        for fill_idx in range(array.shape[0] - size, data.shape[0]):
            data[fill_idx] = False

    return np.asarray(data).view(np.bool)


def runs_of_ones(array, min_samples=None):
    '''
    Create slices where data evaluates to True. Optimised generator version of analysis_engine.library.runs_of_ones.
    ~12x faster for array of 10000 elements.

    :param array: array with 8-bit datatype, e.g. np.bool or np.uint8
    :type array: np.ndarray
    :param min_samples: minimum size of slice (stop - start > min_samples)
    :type min_samples: int or None
    :yields: slices where data evaluates to True
    :ytype: slice
    '''
    cdef:
        unsigned char[:] view = array.view(np.uint8)
        Py_ssize_t idx, min_samples_long = none_idx(min_samples), start_idx = -1

    for idx in range(view.shape[0]):
        if view[idx] and start_idx == -1:
            start_idx = idx
        elif not view[idx] and start_idx != -1:
            if min_samples_long == -1 or idx - start_idx > min_samples_long:
                yield slice(start_idx, idx)
            start_idx = -1

    if start_idx != -1 and (min_samples_long == -1 or view.shape[0] - start_idx > min_samples_long):
        yield slice(start_idx, view.shape[0])


## TODO
#def overlap_merge(x, y, unsigned long extend_start=0, unsigned long extend_stop=0):

    #cdef:
        #unsigned char[:] xv = x.view(np.uint8), yv = y.view(np.uint8)
        #long y_start_idx = -1

    #for idx in range(xv.shape[0]):
        #if xv[idx] and x_start_idx == -1:
            #x_start_idx = idx

        #if yv[idx] and y_start_idx == -1:
            #y_start_idx = idx
        #elif not yv[idx] and yv_start_idx != -1:
            #y_start_idx = -1

        #if xv[idx] and start_idx == -1:
            #start_idx = idx
        #elif not a[idx] and start_idx != -1:
            ## TODO: expand current range from y
            #start_idx = -1


################################################################################
# is_constant


def is_constant(data):
    '''
    Check if an array is constant in value.

    :type data: np.ndarray
    :rtype: bool
    '''
    if data.dtype == np.uint8:
        return is_constant_uint8(data)
    elif data.dtype == np.uint16:
        return is_constant_uint16(data)
    else:
        return (data == data[0]).all()  # type-inspecific fallback (slower)


cpdef bint is_constant_uint8(unsigned char[:] data) nogil:
    '''
    Optimised is_constant check for uint8 datatype.

    Worst case is 6x faster than is_constant, best realistic case is over 1000000x faster.
    '''
    if data.shape[0] <= 1:
        return True

    cdef:
        Py_ssize_t idx
        unsigned char first_value = data[0]

    for idx in range(1, data.shape[0]):
        if data[idx] != first_value:
            return False
    return True


cpdef bint is_constant_uint16(unsigned short[:] data) nogil:
    '''
    Optimised is_constant check for uint16 datatype.

    Worst case is 6x faster than is_constant, best realistic case is over 1000000x faster.
    '''
    if data.shape[0] <= 1:
        return True

    cdef:
        Py_ssize_t idx
        np.uint16_t first_value = data[0]

    for idx in range(1, data.shape[0]):
        if data[idx] != first_value:
            return False
    return True


def first_valid_sample(array, long start_idx=0):
    '''
    Returns the first valid sample of data from a point in an array.
    '''
    cdef:
        unsigned char[:] mask = np.ma.getmaskarray(array).view(np.uint8)
        Py_ssize_t idx

    if start_idx < 0:
        start_idx += mask.shape[0]

    for idx in range(start_idx, mask.shape[0]):
        if not mask[idx]:
            return Value(idx, array[idx])

    return Value(None, None)


def last_valid_sample(array, end_idx=None):
    '''
    Returns the last valid sample of data before a point in an array.
    '''
    cdef:
        unsigned char[:] mask = np.ma.getmaskarray(array).view(np.uint8)
        Py_ssize_t end_idx_long, idx

    if end_idx is None:
        end_idx_long = mask.shape[0] - 1
    else:
        end_idx_long = end_idx
        if end_idx_long < 0:
            end_idx_long = end_idx_long + mask.shape[0]
    if end_idx_long >= mask.shape[0]:
        end_idx_long = mask.shape[0] - 1

    for idx in range(end_idx_long, -1, -1):
        if not mask[idx]:
            return Value(idx, array[idx])

    return Value(None, None)


cdef class Interpolator:

    def __cinit__(self, points):
        '''
        Creates an Interpolator object for applying interpolation points to arrays.
        Extrapolates values outside of the interpolation points.

        Tested against interp1d after being optimized in scipy 0.17.0 (exact same points and data):
        # interp1d
        In [21]: %timeit s(x)
        1 loops, best of 3: 272 ms per loop
        # Interpolator
        In [23]: %timeit i.interpolate(x)
        10 loops, best of 3: 76.6 ms per loop

        References:
         - http://www.zovirl.com/2008/11/04/interpolated-lookup-tables-in-python/
         - http://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-an-extrapolated-result-beyond-the-input-range

        :param points: An iterable of x, y points.
        :type points: [(int, int), ...]
        '''
        cdef:
            Py_ssize_t idx, size = len(points)

        if size < 2:
            raise ValueError('At least 2 interpolation points are required.')

        self._xs = np.empty(size, dtype=np.float64)
        self._ys = np.empty(size, dtype=np.float64)
        for idx, (x, y) in enumerate(sorted(points)):
            self._xs[idx] = x
            self._ys[idx] = y

        self._x_min = self._xs[0]
        self._x_max = self._xs[size - 1]
        self._y_first = self._ys[0]
        self._y_last = self._ys[size - 1]

        self._below_multi = (self._ys[1] - self._y_first) / (self._xs[1] - self._x_min)
        self._above_multi = (self._y_last - self._ys[size - 2]) / (self._x_max - self._xs[size - 2])

        self._size = size

    cdef double _interpolate_value(self, double value) nogil:
        '''
        Interpolate a value according to the Interpolator's interpolation points.

        :param value: Original value.
        :type value: double
        :returns: Interpolated value.
        :rtype: double
        '''
        cdef:
            Py_ssize_t idx

        for idx in range(1, self._size):
            if value <= self._xs[idx]:
                break

        cdef:
            double x_hi = self._xs[idx]
            double x_lo = self._xs[idx - 1]
            double y_hi = self._ys[idx]
            double y_lo = self._ys[idx - 1]
            double slope = (y_hi - y_lo) / (x_hi - x_lo)
        return y_lo + (slope * (value - x_lo))

    cpdef double[:] interpolate(self, double[:] array, bint copy=True):
        '''
        Interpolate (and extrapolate) an array according to the Interpolator's interpolation points.

        :param array: Original value.
        :type array: np.float[:] (memoryview)
        :param copy: Create a copy of the original array to not modify values inplace.
        :type copy: bint
        :returns: Interpolated array.
        :rtype: np.float[:] (memoryview)
        '''
        cdef:
            Py_ssize_t idx
            double value
            double[:] output

        if copy:
            output = np.empty(array.shape[0], dtype=np.float64)
        else:
            output = array

        for idx in range(array.shape[0]):
            value = array[idx]
            if value < self._x_min:
                output[idx] = self._y_first + (value - self._x_min) * self._below_multi
            elif value > self._x_max:
                output[idx] = self._y_last + (value - self._x_max) * self._above_multi
            else:
                output[idx] = self._interpolate_value(value)

        return output


cdef class ByteAligner:
    '''
    Process (filter non-byte-aligned) and identify the words per second of byte-aligned data.
    '''

    # TODO: Return count of synchronised bytes and bytes read from idenfity().
    # TODO: Add a flag for supporting the hfdams format:
    #       - Add support for checking the hdfams nibble bits, e.g. frame marker, etc.
    # TODO: Add a flag for supporting the rose format:
    #       - Automatically add one to each value of WPS.
    #       - Add support for stripping the rose word.
    #       - Perform some sort of check on the value of the rose word.
    def __init__(self, modes=None, wps=None, bint little_endian=True, Py_ssize_t output_buffer=16777216, bint frames_only=False):
        '''
        :param modes: Sync pattern modes as defined within SYNC_PATTERNS. Default is all, running with a limited set is an optimisation.
        :type modes: iterable of str or None
        :param wps: All words per seconds which will be supported during processing. Default is all, running with a limited set is an optimisation.
        :type wps: iterable of str or None
        :param little_endian: Whether or not the byte-order is little_endian.
        :param output_buffer: Approximate number of bytes to store within the output buffer before yielding.
        :param frames_only: Only align complete frames and ignore extra subframes.
        '''
        if modes is None:
            modes = MODES
        if wps is None:
            wps = WPS
        self._wps_array = np.array(sorted(wps), dtype=np.uint16)
        self._min_frame_size = self._wps_array[0] * 4 * 2
        self._max_frame_size = self._wps_array[-1] * 4 * 2
        self.sync_words = sync_words_from_modes(modes)
        self._little_endian = little_endian
        self._output_buffer = output_buffer
        self._frames_only = frames_only
        self.reset()

    cpdef void reset(self):
        '''
        Reset the internal state to prepare for reuse with new data.
        '''
        self._buff = np.empty(0, dtype=np.uint8)
        self._idx = 0
        self._frame_count = 0
        self._output_arrays = []

    cdef unsigned short _get_word(self, Py_ssize_t idx) nogil:
        '''
        Get the word value at specified byte index from the buffer.

        :param idx: byte index of the word within the buffer
        :returns: word value at byte index
        '''
        cdef unsigned short first_byte, second_byte
        if self._little_endian:
            first_byte = self._buff[idx + 1]
            second_byte = self._buff[idx]
        else:
            first_byte = self._buff[idx]
            second_byte = self._buff[idx + 1]
        # Mask out the unused nibble which is populated by HFDAMS:
        return ((first_byte << 8) + second_byte) & 0xfff

    cdef Py_ssize_t _sync_word_idx(self, Py_ssize_t idx) nogil:
        '''
        Find the sync word index of the word within the buffer at specified byte index.

        :param idx: byte index of the word within the buffer
        :returns: sync word index if the word is a sync word, otherwise -1
        '''
        cdef:
            Py_ssize_t sync_word_idx
            unsigned short value = self._get_word(idx)
        for sync_word_idx in range(self.sync_words.shape[0]):
            if self._frames_only and (sync_word_idx % 4) != 0:
                continue
            if value == self.sync_words[sync_word_idx]:
                self._sync_word = value
                break
        else:
            return -1
        return sync_word_idx

    cdef short _frame_wps(self, Py_ssize_t idx) nogil:
        '''
        Find the wps of a frame starting at idx.

        :param idx: start index of potential frame to find wps for
        :returns: words per second if frame matches, otherwise -1
        '''
        cdef Py_ssize_t first_sync_word_idx = self._sync_word_idx(idx)

        if first_sync_word_idx == -1:
            return -1

        cdef:
            Py_ssize_t frame_idx, next_sync_word_idx, offset, wps_array_idx
            unsigned short wps
        for wps_array_idx in range(self._wps_array.shape[0]):
            wps = self._wps_array[wps_array_idx]
            if (idx + wps * 4 * 2) > self._buff.shape[0]:
                continue
            for offset in range(1, 5):
                frame_idx = idx + (wps * offset * 2)
                if frame_idx >= self._buff.shape[0]:
                    continue
                next_sync_word_idx = (first_sync_word_idx // 4 * 4) + ((first_sync_word_idx + offset) % 4)
                if self._get_word(frame_idx) != self.sync_words[next_sync_word_idx]:
                    break
            else:
                return wps
        return -1

    cdef Py_ssize_t _next_frame_idx(self, Py_ssize_t idx) nogil:
        '''
        Find next frame start index within self._buff starting at idx.

        :param idx: index to start searching for frames within self._buff
        :returns: next frame index within self._buff or -1 if frame is not found
        '''
        while True:
            if idx > (self._buff.shape[0] - self._min_frame_size):
                return -1
            self._wps = self._frame_wps(idx)
            if self._wps == -1:
                idx += 1
                continue
            return idx

    def _loop(self, data_gen, func):
        '''
        Find frame start indices and run provided func for each frame providing the start index as an argument.

        :type data_gen: generator yielding arrays or array
        :type func: callable
        :yields: value returned by func for each frame
        '''
        if is_array(data_gen):
            data_gen = (data_gen,)
        cdef Py_ssize_t idx, next_frame_idx, remainder_idx
        for data in data_gen:
            self._buff = np.concatenate((self._buff, data))
            idx = 0
            while True:
                next_frame_idx = self._next_frame_idx(idx)
                if next_frame_idx == -1:
                    remainder_idx = max(self._buff.shape[0] - self._max_frame_size, idx)
                    if remainder_idx <= 0:
                        break
                    self._idx += remainder_idx
                    self._buff = self._buff[remainder_idx:]
                    break
                self._frame_count += 1
                func_return = func(next_frame_idx)
                if func_return is not None:
                    yield func_return
                idx = next_frame_idx + self._wps * 4 * 2
        func_return = func(None) # flush
        if func_return is not None:
            yield func_return

    def process(self, data_gen, start=None, stop=None):
        '''
        Filter byte-aligned data. This version reimplements self._loop to avoid
        concatenating a frame worth of data each time which is ~10x faster for
        64 words per second data.

        :type data_gen: generator yielding arrays or array
        :param start: data start position in seconds if not -1
        :type start: int or None
        :param stop: data stop position in seconds
        :type stop: int or None
        :yields: arrays containing synchronised byte-aligned data
        :ytype: np.array(dtype=np.uint8)
        '''

        if start is not None and stop is not None and stop <= start:
            raise ValueError('stop must be greater than start')
        elif start is not None and start < 0:
            raise ValueError('negative start index not supported')
        elif stop is not None and stop <= 0:
            raise ValueError('negative or zero stop index not supported')

        if is_array(data_gen):
            data_gen = (data_gen,)

        cdef:
            Py_ssize_t frame_start_idx = -1, frame_stop_idx = -1, idx = 0, next_frame_idx, remainder_idx
            Py_ssize_t frame_start = -1 if start is None else start // 4, frame_stop = -1 if stop is None else <int>ceil(stop / 4.)

        for data in data_gen:
            self._buff = np.concatenate((self._buff, data))

            while True:
                next_frame_idx = self._next_frame_idx(idx)

                if next_frame_idx == -1:  # next frame not found
                    if frame_start_idx != -1:  # data has lost sync (possibly end of buffer)
                        yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                        frame_start_idx = -1
                        frame_stop_idx = -1
                    # truncate buffer to remove already processed data
                    remainder_idx = self._buff.shape[0] - self._min_frame_size
                    idx = max(idx - remainder_idx, 0)
                    self._idx += remainder_idx
                    self._buff = self._buff[remainder_idx:]
                    break

                # next frame found
                self._frame_count += 1

                if frame_start != -1 and self._frame_count <= frame_start:
                    # ignore frame before start index
                    idx = next_frame_idx + self._wps * 4 * 2
                    continue

                if frame_stop_idx != -1 and next_frame_idx != frame_stop_idx:
                    # data was in sync, but next frame does not directly follow the previous frame
                    yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                    frame_start_idx = next_frame_idx
                elif frame_start_idx == -1:
                    # data was previously not in sync
                    frame_start_idx = next_frame_idx

                frame_stop_idx = next_frame_idx + self._wps * 4 * 2

                if frame_stop != -1 and frame_stop <= self._frame_count:
                    # reached stop index, stop searching for sync
                    yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                    break

                idx = frame_stop_idx

            if frame_stop != -1 and frame_stop <= self._frame_count:
                break

    def process_slow(self, data_gen, start=None, stop=None):
        '''
        Filter byte-aligned data. This version uses self._loop which is a
        consistent synchronisation implementation, but concatenating one frame
        at a time is ~10x slower at 64 words per second.

        :type data_gen: generator yielding arrays or array
        :param start: data start position in seconds if not -1
        :type start: int or None
        :param stop: data stop position in seconds
        :type stop: int or None
        :yields: arrays containing synchronised byte-aligned data
        :ytype: np.array(dtype=np.uint8)
        '''
        if start is not None and stop is not None and stop <= start:
            raise ValueError('stop must be greater than start')
        cdef:
            Py_ssize_t frame_start = -1 if start is None else start // 4
            Py_ssize_t frame_stop = -1 if stop is None else <int>ceil(stop / 4.)
        def get_data(idx):
            if idx is None:
                return np.concatenate(self._output_arrays) if self._output_arrays else None
            if frame_start != -1 and self._frame_count <= frame_start:
                return
            if frame_stop != -1 and self._frame_count > frame_stop:
                if not self._output_arrays:
                    raise StopIteration
                output_array = np.concatenate(self._output_arrays)
                self._output_arrays = []
                return output_array
            cdef unsigned int frame_size = self._wps * 4 * 2
            self._output_arrays.append(self._buff[idx:idx + frame_size])
            if sum(len(a) for a in self._output_arrays) >= self._output_buffer:
                output_array = np.concatenate(self._output_arrays)
                self._output_arrays = []
                return output_array
        return self._loop(data_gen, get_data)

    def identify(self, data_gen):
        '''
        Identify frame start indices and words per second.

        :type data_gen: generator yielding arrays or array
        :yields: tuples containing index, wps and type of frame starts
        :ytype: (int, int, str)
        '''
        def info(idx):
            if idx is None:
                return
            for mode, sync_words in SYNC_PATTERNS.items():
                if self._sync_word in sync_words:
                    break
            return (self._idx + idx, self._wps, mode)
        return self._loop(data_gen, info)


cpdef unsigned short[:] sync_words_from_modes(modes):
    '''
    Creates an array containing sync words in a contiguous 1d-array.

    e.g. sync_words_from_modes(['717'])
    '''
    cdef:
        unsigned short[:] sync_words = np.empty(len(modes) * 4, dtype=np.uint16)
        Py_ssize_t sync_word_idx = 0
    for mode in modes:
        for sync_word in SYNC_PATTERNS[mode]:
            sync_words[sync_word_idx] = sync_word
            sync_word_idx += 1
    return sync_words


def swap_bytes(array):
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


def unpack(array):
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


def pack(array):
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


def key_value(array, key, delimiter, separator, start=0):
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
    return array[start_idx:stop_idx].tostring().strip()


cpdef Py_ssize_t index_of_subarray_uint8(unsigned char[:] array, unsigned char[:] subarray, Py_ssize_t start=0) nogil:
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


cpdef Py_ssize_t array_index_uint16(unsigned short value, unsigned short[:] array) nogil:
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


def merge_masks(masks):
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


def mask_ratio(mask):
    '''
    Ratio of masked data (1 == all masked).
    '''
    # Handle scalars.
    if np.all(mask):
        return 1
    elif not np.any(mask):
        return 0
    return mask.sum() / float(len(mask))


def percent_unmasked(mask):
    '''
    Percentage of unmasked data.
    '''
    return (1 - mask_ratio(mask)) * 100


def sum_arrays(arrays):
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


def downsample_arrays(arrays):
    '''
    Return arrays downsampled to the size of the smallest.

    :param arrays: Arrays to downsample.
    :type arrays: iterable of np.ma.masked_array
    :returns: Arrays downsampled to the size of the smallest.
    :rtype: iterable of np.ma.masked_array
    '''
    lengths = [len(x) for x in arrays]
    shortest = min(lengths)
    if shortest == max(lengths):
        return arrays

    for length in lengths:
        if length % shortest:
            raise ValueError("Arrays lengths '%s' should be multiples of the shortest." % lengths)
    downsampled_arrays = []
    for array in arrays:
        step = len(array) // shortest
        if step > 1:
            array = array[::step]
        downsampled_arrays.append(array)
    return downsampled_arrays


def upsample_arrays(arrays):
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
            raise ValueError(
                "The largest array length should be a multiple of all others "
                "'%s'." % lengths)

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


def align_arrays(slave_array, master_array):
    '''
    Very basic aligning using repeat to upsample and skipping over samples to
    downsample the slave array to the master frequency

    >>> align(np.arange(10), np.arange(20,30))  # equal length
    array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> align(np.arange(40,80), np.arange(20,40))  # downsample every other
    array([40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,
           74, 76, 78])
    >>> align(np.arange(40,80), np.arange(30,40))  # downsample every 4th
    array([40, 44, 48, 52, 56, 60, 64, 68, 72, 76])
    >>> align(np.arange(10), np.arange(20,40))  # upsample
    array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9])
    '''
    ratio = len(master_array) / float(len(slave_array))
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


def save_compressed(path, array):
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
        raise NotImplementedError("Object of type '%s' cannot be saved." % type(array))


def load_compressed(path):
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
        raise NotImplementedError('Unknown array type with %d components.' % array_count)
    return array


cpdef bint is_power2(number):
    """
    Whether or not a number is a power of two. Forces floats to int.
    Ref: http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/

    ~4x faster than pure python version
    """
    if number % 1:
        return False
    cdef int num = <int>number
    return num > 0 and ((num & (num - 1)) == 0)


cpdef is_power2_fraction(number):
    '''
    TODO: Tests

    :type number: int or float
    :returns: if the number is either a power of 2 or a fraction, e.g. 4, 2, 1, 0.5, 0.25
    :rtype: bool
    '''
    if number < 1:
        number = 1 / number
    return is_power2(number)

