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


import cython
import numpy as np
cimport numpy as np

from flightdatautilities.array import Value
from flightdatautilities.array cimport cython as cy, scalar as sc


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


cpdef nearest_slice(array, Py_ssize_t idx, bint match=True):
    cdef np.uint8_t[:] data = array.view(np.uint8)
    idx = cy.array_wraparound_idx(idx, data.shape[0])
    cdef Py_ssize_t start_idx, stop_idx, nearest_idx = cy.nearest_idx_unsafe(data, idx, match=match)
    if nearest_idx == cy.NONE_IDX:
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


cpdef Py_ssize_t longest_section(cy.np_types[:] data, cy.np_types value=0) nogil:
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


cpdef remove_small_runs(array, np.float64_t seconds=10, np.float64_t hz=1, bint match=True):
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
        Py_ssize_t idx, min_samples_long = cy.none_idx(min_samples), start_idx = -1

    for idx in range(view.shape[0]):
        if view[idx] and start_idx == -1:
            start_idx = idx
        elif not view[idx] and start_idx != -1:
            if min_samples_long == cy.NONE_IDX or idx - start_idx > min_samples_long:
                yield slice(start_idx, idx)
            start_idx = -1

    if start_idx != -1 and (min_samples_long == cy.NONE_IDX or view.shape[0] - start_idx > min_samples_long):
        yield slice(start_idx, view.shape[0])


## TODO
#def overlap_merge(x, y, Py_ssize_t extend_start=0, Py_ssize_t extend_stop=0):

    #cdef:
        #np.uint8_t[:] xv = x.view(np.uint8), yv = y.view(np.uint8)
        #Py_ssize_t y_start_idx = -1

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


@cython.wraparound(False)
cpdef bint is_constant(cy.np_types[:] data) nogil:
    '''
    Return whether or not an array is constant in value.
    '''
    if data.shape[0] <= 1:
        return True

    cdef Py_ssize_t idx

    for idx in range(1, data.shape[0]):
        if data[idx] != data[0]:
            return False
    return True


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


cpdef np.uint16_t[:] unpack_little_endian(const np.uint8_t[:] data):
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


@cython.cdivision(True)
@cython.wraparound(False)
cpdef np.uint8_t[:] unpack(const np.uint8_t[:] packed):
    '''
    Unpack 'packed' flight data into unpacked (byte-aligned) format.

    opt: ~3x faster than numpy array version

    :type array: np.ndarray(dtype=np.uint8)
    :rtype: np.ndarray(dtype=np.uint8)
    '''
    cdef:
        np.uint8_t[:] unpacked = cy.empty_uint8(packed.shape[0] // 3 * 4)
        Py_ssize_t packed_idx = 0, unpacked_idx

    for unpacked_idx in range(0, unpacked.shape[0], 4):
        unpacked[unpacked_idx] = packed[packed_idx]
        unpacked[unpacked_idx + 1] = packed[packed_idx + 1] & 0x0F
        unpacked[unpacked_idx + 2] = ((packed[packed_idx + 2] & 0x0F) << 4) + ((packed[packed_idx + 1] & 0xF0) >> 4)
        unpacked[unpacked_idx + 3] = (packed[packed_idx + 2] & 0xF0) >> 4
        packed_idx += 3

    return unpacked


@cython.cdivision(True)
@cython.wraparound(False)
cpdef np.uint8_t[:] pack(const np.uint8_t[:] unpacked):
    '''
    Pack 'unpacked' flight data into packed format.

    opt: ~8x faster than numpy array version

    :type array: np.ndarray(dtype=np.uint8)
    :rtype: np.ndarray(dtype=np.uint8)
    '''
    cdef:
        np.uint8_t[:] packed = cy.empty_uint8(unpacked.shape[0] // 4 * 3)
        Py_ssize_t unpacked_idx = 0, packed_idx

    for packed_idx in range(0, packed.shape[0], 3):
        packed[packed_idx] = unpacked[unpacked_idx]
        packed[packed_idx + 1] = unpacked[unpacked_idx + 1] + ((unpacked[unpacked_idx + 2] & 0x0F) << 4)
        packed[packed_idx + 2] = (unpacked[unpacked_idx + 3] << 4) + ((unpacked[unpacked_idx + 2] & 0xF0) >> 4)
        unpacked_idx += 4

    return packed


cpdef bytes key_value(const np.uint8_t[:] array, const np.uint8_t[:] key, const np.uint8_t[:] delimiter,
                      const np.uint8_t[:] separator, Py_ssize_t start=0):
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
    key_idx = cy.subarray_idx_uint8(array, key, start=start)
    if key_idx == cy.NONE_IDX:
        return None
    start_idx = cy.subarray_idx_uint8(array, delimiter, start=key_idx) + len(delimiter)
    stop_idx = cy.subarray_idx_uint8(array, separator, start=start_idx)
    return bytes(array[start_idx:stop_idx]).strip()


cpdef subarray_idx_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=0):
    '''
    Find the first index of a subarray within an array of dtype uint8.

    TODO: change to cy.np_types fused type once Cython supports const with fused types

    :param start: start index to search within array (positive integer or 0)
    :returns:
    '''
    return cy.idx_none(cy.subarray_idx_uint8(array, subarray, start=start))


cpdef bint subarray_exists_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=0) nogil:
    '''
    Return whether or not the subarray exists within the array.

    TODO: change to cy.np_types fused type once Cython supports const with fused types
    '''
    return cy.subarray_idx_uint8(array, subarray, start=start) != cy.NONE_IDX


@cython.wraparound(False)
cpdef value_idx(cy.np_types[:] array, cy.np_types value):
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
    return cy.idx_none(cy.value_idx(array, value))


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


@cython.cdivision(True)
@cython.wraparound(False)
cpdef np.uint8_t[:] merge_masks_upsample_uint8(masks):
    '''
    opt: upsampling 10 memoryviews to 10,000 elements: ~5x faster than merge_masks(upsample_arrays(masks))
    '''
    lengths = [len(m) for m in masks]
    cdef:
        # can't use generator in max - "closures inside cpdef functions not yet supported"
        Py_ssize_t max_length = max(lengths), min_length = min(lengths), output_idx
        np.uint8_t[:] mask, output = cy.zeros_uint8(max_length)
        np.float64_t step

    for mask in masks:
        if mask.shape[0] == max_length:  # opt: ~5x faster than applying step
            for output_idx in range(output.shape[0]):
                output[output_idx] |= mask[output_idx]
        elif mask.shape[0] % min_length:
            raise ValueError('mask lengths should be multiples of the shortest')
        else:
            step = <np.float64_t>mask.shape[0] / <np.float64_t>max_length
            for output_idx in range(output.shape[0]):
                output[output_idx] |= mask[<Py_ssize_t>(output_idx * step)]

    return output


@cython.cdivision(True)
@cython.wraparound(False)
cpdef np.uint8_t[:] merge_masks_uint8(masks):
    '''
    opt: for 10 arrays of 10,000 elements: ~8x faster than merge_masks(masks), ~5x faster than np.vstack(masks).any(0)
    '''
    cdef:
        np.uint8_t[:] mask, output = cy.zeros_uint8(len(masks[0]))
        Py_ssize_t idx

    for mask in masks:
        for idx in range(output.shape[0]):
            output[idx] |= mask[idx]

    return output



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

    opt: this approach is efficient since it slices the arrays and therefore the data is not copied

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

cpdef np.ndarray twos_complement(np.ndarray array, np.uint64_t bit_length):
    '''
    Convert the values from "sign bit" notation to "two's complement".
    '''
    array[array > sc.saturated_value(bit_length - 1)] -= sc.saturated_value(bit_length) + 1
    return array

