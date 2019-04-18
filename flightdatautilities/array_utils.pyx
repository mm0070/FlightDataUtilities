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

from libc.math cimport fabs
from libc.stdio cimport printf


cdef:
    #int FILL_START = 0, FILL_STOP = 1, INTERPOLATE = 2
    int MAX_VALUE = 0, MIN_VALUE = 1, MAX_ABS_VALUE = 2, MIN_ABS_VALUE = 3


cdef object idx_none(long idx):
    return None if idx == -1 else idx


cdef long none_idx(idx):
    return -1 if idx is None else idx


cdef long cython_nearest_idx(unsigned char[:] array, long idx, bint match=True, long start_idx=-1, long stop_idx=-1) nogil:
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
        long fwd_range = stop_idx - idx, rev_range = idx - start_idx, shift

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


def nearest_slice(array, long idx, bint match=True):
    cdef unsigned char[:] data = array.view(np.uint8)
    cdef long start_idx, stop_idx, nearest_idx = cython_nearest_idx(data, idx, match=match)

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


cdef void cython_ma_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil:
    cdef long idx
    for idx in range(start, stop):
        data[idx] = value
        mask[idx] = 0


cdef void cython_ma_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil:
    cdef:
        double gradient = (data[stop] - data[start]) / (stop - start)
        long idx
    for idx in range(start + 1, stop):
        data[idx] = data[start] + ((idx - start) * gradient)
        mask[idx] = 0


cpdef void cython_repair_mask_float64(double[:] data, unsigned char[:] mask, RepairMethod method, long max_samples, bint extrapolate=False) nogil:
    cdef:
        long idx, last_valid_idx = -1

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
    cdef long length, repair_samples, unmasked_samples

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


cdef long longest_zeros_uint8(unsigned char[:] mask) nogil:
    cdef long idx, current_samples = 0, max_samples = 0
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
        long idx, value_idx = -1
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


def slices_to_array(long size, slices):
    cdef:
        unsigned char[:] array = np.zeros(size, dtype=np.uint8)
        long start, stop, idx
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
        long long idx, rev_idx, last_idx = -1
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


def remove_small_runs(array, unsigned long seconds=10, unsigned long hz=1):
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
    cdef unsigned long size = seconds * hz
    if not size:
        return array

    cdef:
        unsigned char[:] data = array.view(np.uint8)
        long long idx, fill_idx, samples = 0

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


def contract_runs(array, unsigned long size):
    '''
    Contract runs of True values within arrays, e.g.
    contract_runs([False, True, True, True], 1) == [False, False, True, False]
    '''
    if not size:
        return array

    cdef:
        unsigned char[:] data = array.view(np.uint8)
        long long idx, fill_idx, contracted = 0

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


def runs_of_ones(array):
    '''
    Create slices where data is True. Optimised generator version of analysis_engine.library.runs_of_ones.
    ~12x faster for array of 10000 elements.
    '''
    cdef:
        unsigned char[:] view = array.view(np.uint8)
        long idx, start_idx = -1

    for idx in range(view.shape[0]):
        if view[idx] and start_idx == -1:
            start_idx = idx
        elif not view[idx] and start_idx != -1:
            yield slice(start_idx, idx)
            start_idx = -1

    if start_idx != -1:
        yield slice(start_idx, view.shape[0])


# TODO
def overlap_merge(x, y, unsigned long extend_start=0, unsigned long extend_stop=0):

    cdef:
        unsigned char[:] xv = x.view(np.uint8), yv = y.view(np.uint8)
        long y_start_idx = -1

    for idx in range(xv.shape[0]):
        if xv[idx] and x_start_idx == -1:
            x_start_idx = idx

        if yv[idx] and y_start_idx == -1:
            y_start_idx = idx
        elif not yv[idx] and yv_start_idx != -1:
            y_start_idx = -1

        if xv[idx] and start_idx == -1:
            start_idx = idx
        elif not a[idx] and start_idx != -1:
            # TODO: expand current range from y
            start_idx = -1


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
        return (arr == arr[0]).all()  # type-inspecific fallback (slower)


@cython.boundscheck(False)
cpdef bint is_constant_uint8(unsigned char[:] data) nogil:
    '''
    Optimised is_constant check for uint8 datatype.

    Worst case is 6x faster than is_constant, best realistic case is over 1000000x faster.
    '''
    if data.shape[0] <= 1:
        return True

    cdef:
        unsigned int idx
        unsigned char first_value = data[0]

    for idx in range(1, data.shape[0]):
        if data[idx] != first_value:
            return False
    return True


@cython.boundscheck(False)
cpdef bint is_constant_uint16(unsigned short[:] data) nogil:
    '''
    Optimised is_constant check for uint16 datatype.

    Worst case is 6x faster than is_constant, best realistic case is over 1000000x faster.
    '''
    if data.shape[0] <= 1:
        return True

    cdef:
        unsigned int idx
        np.uint16_t first_value = data[0]

    for idx in range(1, data.shape[0]):
        if data[idx] != first_value:
            return False
    return True

