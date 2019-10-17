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

# Other replacements

## closest_unmasked_value
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

from flightdatautilities.array import Value
from flightdatautilities.array cimport cython as cy


cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil:
    return (2 ** bit_length) - 1


cpdef bint any_array(array):
    '''
    Q: why do we need this when array.any() exists?
    '''
    cdef:
        Py_ssize_t idx
        np.uint8_t[:] data = array.view(np.uint8)
    for idx in range(data.shape[0]):
        if data[idx]:
            return True
    return False


cpdef bint all_array(array):
    '''
    Q: why do we need this when array.all() exists?
    '''
    cdef:
        Py_ssize_t idx
        np.uint8_t[:] data = array.view(np.uint8)
    for idx in range(data.shape[0]):
        if not data[idx]:
            return False
    return True


cpdef bint entirely_masked(array):
    '''
    Q: Why do we need this when array.mask.all() exists?

    Worst case is 2x faster than np.ma.count, best case (first sample unmasked) is 500x faster on large array.
    '''
    return array.mask if np.isscalar(array.mask) else all_array(array.mask)


cpdef bint entirely_unmasked(array):
    '''
    Q: Why do we need this when not array.mask.any() exists?

    Worst case is 2x faster than np.ma.count, best case (first sample masked) is 500x faster on large array.
    '''
    return not array.mask if np.isscalar(array.mask) else not any_array(array.mask)


cdef object array_idx_value(Py_ssize_t idx, object array):
    return Value(None, None) if idx == -1 else Value(idx, array[idx])


cpdef object idx_none(Py_ssize_t idx):
    '''
    Converts int idx to int or None where -1 is None for converting from Cython-optimised to Python types.
    '''
    return None if idx == -1 else idx


cpdef Py_ssize_t none_idx(idx):
    '''
    Converts int or None idx to int idx where None is -1 for converting from Python to Cython-optimised types.
    '''
    return -1 if idx is None else idx


cpdef nearest_idx(array, Py_ssize_t idx, bint match=True, Py_ssize_t start_idx=0, Py_ssize_t stop_idx=-1):
    return idx_none(cy.nearest_idx(array.view(np.uint8), idx, match=match, start_idx=start_idx, stop_idx=stop_idx))


cpdef nearest_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=0, Py_ssize_t stop_idx=-1):
    cdef Py_ssize_t unmasked_idx = cy.nearest_idx(cy.getmaskarray1d(array), idx, match=False, start_idx=start_idx,
                                                      stop_idx=stop_idx)
    return array_idx_value(array, unmasked_idx)


cpdef prev_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=0):
    cdef Py_ssize_t unmasked_idx = cy.prev_idx(cy.getmaskarray1d(array), idx, match=False, start_idx=start_idx)
    return array_idx_value(array, unmasked_idx)


cpdef next_unmasked_value(array, Py_ssize_t idx, Py_ssize_t stop_idx=-1):
    cdef Py_ssize_t unmasked_idx = cy.next_idx(cy.getmaskarray1d(array), idx, match=False, stop_idx=stop_idx)
    return array_idx_value(array, unmasked_idx)


cpdef first_unmasked_value(array, Py_ssize_t start_idx=0):
    return next_unmasked_value(array, start_idx)


cpdef last_unmasked_value(array, Py_ssize_t stop_idx=-1, Py_ssize_t min_samples=-1):
    cdef np.uint8_t[:] mask = cy.getmaskarray1d(array)
    if min_samples > 0:
        mask = cy.remove_small_runs(mask, <float>min_samples)
    stop_idx = cy.array_stop_idx(stop_idx, mask.shape[0])

    cdef Py_ssize_t idx

    for idx in range(stop_idx, -1, -1):
        if not mask[idx]:
            return array[idx]
    return None


cpdef nearest_slice(array, Py_ssize_t idx, bint match=True):
    cdef np.uint8_t[:] data = array.view(np.uint8)
    cdef Py_ssize_t start_idx, stop_idx, nearest_idx = cy.nearest_idx(data, idx, match=match)

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
    elif nearest_idx > idx:  # nearest slice starts at a later idx, scan forward to find slice stop
        start_idx = nearest_idx
        for stop_idx in range(start_idx + 1, data.shape[0]):
            if data[stop_idx] != match:
                break
        else:
            stop_idx = data.shape[0]

    else:  # nearest slice stops at an earlier idx, scan backwards to find slice start
        stop_idx = nearest_idx + 1
        for start_idx in range(nearest_idx, -1, -1):
            if data[start_idx] != match:
                start_idx += 1
                break
        else:
            start_idx = 0

    return slice(start_idx, stop_idx)


cpdef repair_mask(array, method='interpolate', repair_duration=10, frequency=1, bint copy=False, bint extrapolate=False, bint raise_duration_exceedance=False, bint raise_entirely_masked=True):
    '''
    TODO: find better solution for repair_above kwarg from original.
    '''
    cdef Py_ssize_t length, repair_samples, unmasked_samples

    if array.mask.all():  # XXX: calling all and any is faster than calling np.ma.count once
        if raise_entirely_masked:
            raise ValueError('Array cannot be repaired as it is entirely masked')
        return array
    elif not array.mask.any():
        return array

    dtype = array.dtype
    array = array.astype(np.float64, copy=copy)

    if repair_duration:
        repair_samples = repair_duration * frequency
        if raise_duration_exceedance:
            length = longest_section_uint8(array.mask)
            if length > repair_samples:
                raise ValueError(
                    f"Length of masked section '{length * frequency}' exceeds repair duration '{repair_duration}'.")
    else:
        repair_samples = -1

    cy.repair_mask_float64(
        array.data,
        array.mask.view(np.uint8),
        {'interpolate': cy.RepairMethod.INTERPOLATE, 'fill_start': cy.RepairMethod.FILL_START, 'fill_stop': cy.RepairMethod.FILL_STOP}[method],
        repair_samples,
        extrapolate=extrapolate,
    )
    return array.astype(dtype)


cpdef Py_ssize_t longest_section_uint8(np.uint8_t[:] data, np.uint8_t value=0) nogil:
    '''
    Find the longest section matching value and return the number of samples.
    '''
    cdef Py_ssize_t idx, current_samples = 0, max_samples = 0
    for idx in range(data.shape[0]):
        if data[idx] != value:
            if current_samples > max_samples:
                max_samples = current_samples
            current_samples = 0
        else:
            current_samples += 1
    return max_samples if max_samples > current_samples else current_samples


def aggregate_values(Aggregate mode, np.float64_t[:] data, np.uint8_t[:] mask, np.uint8_t[:] matching):
    if data.shape[0] != mask.shape[0] or data.shape[0] != matching.shape[0]:
        raise ValueError('array lengths do not match')

    cdef:
        Py_ssize_t idx, value_idx = -1
        np.float64_t value
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
        mode, array.data.astype(np.float64, copy=False), cy.getmaskarray1d(array), matching.view(np.uint8))


cpdef max_values(array, matching):
    return _aggregate_values(Aggregate.MAX, array, matching)


cpdef min_values(array, matching):
    return _aggregate_values(Aggregate.MIN, array, matching)


cpdef max_abs_values(array, matching):
    return _aggregate_values(Aggregate.MAX_ABS, array, matching)


cpdef min_abs_values(array, matching):
    return _aggregate_values(Aggregate.MIN_ABS, array, matching)


cpdef slices_to_array(Py_ssize_t size, slices):
    '''
    Convert slices to a boolean array of a specified size. Slice step is ignored.
    '''
    cdef:
        np.uint8_t[:] array = cy.zeros_uint8(size)
        Py_ssize_t start, stop, idx
    for s in slices:
        start = 0 if s.start is None else s.start
        stop = size if s.stop is None else s.stop
        if start < 0:
            start = 0
        if stop > size:
            stop = size
        for idx in range(start, stop):
            array[idx] = 1
    return np.asarray(array).view(np.bool)


cpdef section_overlap(a, b):
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
    cdef np.uint8_t[:] x = a.view(np.uint8), y = b.view(np.uint8)

    if x.shape[0] != y.shape[0]:
        raise ValueError('array lengths do not match')

    cdef:
        np.uint8_t[:] out = cy.zeros_uint8(x.shape[0])
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

    return np.asarray(out).view(np.bool)


cpdef remove_small_runs(array, float seconds=10, float hz=1, bint match=True):
    '''
    Remove small runs of matching values from a boolean array.
    '''
    return np.asarray(cy.remove_small_runs(array.view(np.uint8), seconds, hz, match=match)).view(np.bool)


cpdef contract_runs(array, Py_ssize_t size, bint match=True):
    '''
    Contract runs of matching values within an array, e.g.
    contract_runs([False, True, True, True], 1) == [False, False, True, False]
    '''
    return np.asarray(cy.contract_runs(array.view(np.uint8), size, match=match)).view(np.bool)


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
        np.uint8_t[:] view = array.view(np.uint8)
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


cpdef bint is_constant(data):
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


cpdef bint is_constant_uint8(np.uint8_t[:] data) nogil:
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


cpdef bint is_constant_uint16(np.uint16_t[:] data) nogil:
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


cpdef first_valid_sample(array, Py_ssize_t start_idx=0):
    '''
    Returns the first valid sample of data from a point in an array.
    '''
    cdef:
        np.uint8_t[:] mask = cy.getmaskarray1d(array)
        Py_ssize_t idx

    if start_idx < 0:
        start_idx += mask.shape[0]

    for idx in range(start_idx, mask.shape[0]):
        if not mask[idx]:
            return Value(idx, array[idx])

    return Value(None, None)


cpdef last_valid_sample(array, end_idx=None):
    '''
    Returns the last valid sample of data before a point in an array.
    '''
    cdef:
        np.uint8_t[:] mask = cy.getmaskarray1d(array)
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
        np.uint16_t[:] output = cy.zeros_uint16(<Py_ssize_t>(data.shape[0] // 1.5))
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

