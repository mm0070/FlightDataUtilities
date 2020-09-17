# cython: language_level=3, boundscheck=False
'''
Masked array-specific functions.
'''
cimport cython
from libc.math cimport ceil, fabs, floor
from libc.stdio cimport fprintf, stderr, printf
import numpy as np
cimport numpy as np

from flightdatautilities.data cimport cython as cy, operations as op

np.import_array()  # required for calling PyArray_* functions


cpdef Py_ssize_t first_idx_within_roc(np.float64_t[:] data, np.uint8_t[:] mask, np.float64_t limit,
                                      Py_ssize_t last_stable_idx, Py_ssize_t start_idx, Py_ssize_t stop_idx):
    '''
    Find the first index within rate of change limits.
    '''
    cdef:
        Py_ssize_t idx
        np.float64_t extrapolated_limit

    for idx in range(start_idx, stop_idx):
        if mask[idx]:
            continue
        extrapolated_limit = (idx - last_stable_idx) * limit
        if data[idx] <= data[last_stable_idx] + extrapolated_limit and \
            data[idx] >= data[last_stable_idx] - extrapolated_limit:
            return idx
    return -1


cpdef blend_parameters_weighting(array, np.float64_t wt):
    '''
    A small function to relate masks to weights. Used by
    blend_parameters_cubic above.

    :param array: array to compute weights for
    :type array: numpy masked array
    :param wt: weighting factor =  ratio of sample rates
    :type wt: float
    '''
    cdef:
        np.uint8_t[:] param_weight = (~np.ma.getmaskarray(array)).view(np.uint8)
        Py_ssize_t array_size = <Py_ssize_t>(param_weight.shape[0] * wt)
        np.float64_t[:] result_weight = cy.zeros_float64(array_size), \
            final_weight = cy.zeros_float64(array_size)
        np.float64_t wt_reciprocal = 1.0 / wt
        Py_ssize_t idx, weight_idx

    result_weight[0] = param_weight[0] / wt
    result_weight[-1] = param_weight[-1] / wt

    for idx in range(1, param_weight.shape[0] - 1):
        weight_idx = <Py_ssize_t>(idx * wt)
        if not param_weight[idx]:
            result_weight[weight_idx] = 0.0
            continue

        if not param_weight[idx - 1] or not param_weight[idx + 1]:
            # Low weight to tail of valid data. Non-zero to avoid problems of overlapping invalid sections.
            result_weight[weight_idx] = 0.1
            continue

        result_weight[weight_idx] = wt_reciprocal

    for idx in range(1, result_weight.shape[0] - 1):
        if not result_weight[idx - 1] or not result_weight[idx + 1]:
            final_weight[idx] = result_weight[idx] / 2
        else:
            final_weight[idx] = result_weight[idx]

    final_weight[0] = result_weight[0]
    final_weight[-1] = result_weight[-1]

    return np.ma.masked_array(final_weight)


################################################################################
# Utility functions


cdef np.uint8_t[:] getmaskarray1d(array):
    '''
    Return the mask memoryview from a np.ma.masked_array in a Cython-compatible dtype. Assumes scalar mask is False.

    Note: If mask is a scalar then a new mask array will be created and modifications will not affect the original
          masked array's mask (as is the case with np.ma.getmaskarray()). If creating a masked array with a mutable mask
          is required, pass mask=False into np.ma.masked_array() which overrides the default nomask constant.

    OPT: ~3x faster than np.ma.getmaskarray() when mask is a scalar, ~10% faster when mask is an array
    '''
    return cy.zeros_uint8(len(array)) if np.PyArray_CheckScalar(array.mask) else array.mask


################################################################################
# Mask ratio/percentage


cpdef mask_ratio(mask):
    '''
    Ratio of masked data (1 == all masked).
    '''
    if np.all(mask):  # True scalar
        return 1
    elif not np.any(mask):  # False scalar
        return 0
    else:
        return mask.sum() / float(len(mask))


cpdef percent_unmasked(mask):
    '''
    Percentage of unmasked data.
    '''
    return (1 - mask_ratio(mask)) * 100


################################################################################
# Merge masks


cpdef merge_masks(masks):
    '''
    ORs multiple masks together. Q: Could this be done in one step with numpy?

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


################################################################################
# Find unmasked values


cpdef prev_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start=0):
    return cy.array_idx_value(array, cy.prev_idx(getmaskarray1d(array), idx, match=False, start=start))


cpdef next_unmasked_value(array, Py_ssize_t idx, Py_ssize_t stop=cy.NONE_IDX):
    return cy.array_idx_value(array, cy.next_idx(getmaskarray1d(array), idx, match=False, stop=stop))


cpdef nearest_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start=0, Py_ssize_t stop=cy.NONE_IDX):
    return cy.array_idx_value(array, cy.nearest_idx(getmaskarray1d(array), idx, match=False, start=start,
                                                    stop=stop))


################################################################################
# Fill range

cdef void fill_range(cy.np_types[:] data, np.uint8_t[:] mask, cy.np_types value, Py_ssize_t start, Py_ssize_t stop) nogil:
    '''
    Fill a section of a masked_array's data and mask with a value and unmask.
    '''
    data[start:stop] = value
    mask[start:stop] = 0


################################################################################
# Interpolate range

@cython.cdivision(True)
@cython.wraparound(False)
cdef void interpolate_range_unsafe(cy.np_types[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil:
    '''
    Fill a section of a float64 masked_array's data and mask with values interpolated between start and stop indices
    and unmask.

    OPT: fused type isn't used so that gradient can be calculated once, also interpolation is most useful for
         np.float64_t arrays

    Unsafe:
    - start and stop must be within array bounds and non-negative.
    '''
    cdef:
        cy.np_types gradient = (data[stop] - data[start]) / (stop - start)
        Py_ssize_t idx
    for idx in range(start + 1, stop):
        data[idx] = data[start] + ((idx - start) * gradient)
        mask[idx] = 0


@cython.wraparound(False)
cdef void interpolate_range(cy.np_types[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil:
    '''
    Fill a section of a float64 masked_array's data and mask with values interpolated between start and stop indices
    and unmask.
    '''
    if not cy.lengths_match(data.shape[0], mask.shape[0]):
        return

    start = cy.array_wraparound_idx(start, data.shape[0])
    stop = cy.array_wraparound_idx(stop, data.shape[0])
    if start >= stop:
        return  # avoid divide by zero

    if mask[start] or mask[stop]:
        fprintf(stderr, 'interpolate_range cannot interpolate between masked values (%ld and %ld)\n', start, stop)
        return

    interpolate_range_unsafe(data, mask, start, stop)


################################################################################
# Repair mask


@cython.wraparound(False)
cdef void repair_data_mask(np.float64_t[:] data, np.uint8_t[:] mask, RepairMethod method, Py_ssize_t max_samples=-1,
                           bint extrapolate=False) nogil:
    '''
    Repairs data and mask memoryviews in-place with a specified RepairMethod.
    '''
    if not cy.lengths_match(data.shape[0], mask.shape[0]):
        return

    # XXX: unable to call this function via repair_data_mask[np.float64_t](...) when data is cy.np_types fused type:
    #      Cannot convert 'object (float64_t[:], uint8_t[:], RepairMethod, Py_ssize_t, struct __pyx_fuse_10__pyx_opt_args_19flightdatautilities_5array_12masked_array_repair_data_mask *__pyx_optional_args)' to Python object
    #if cy.np_types is not np.float64_t:  # cannot create more complex condition, otherwise code is not pruned
        #if method == RepairMethod.INTERPOLATE:
            #fprintf(stderr, 'repair_mask cannot INTERPOLATE non-float64 array, FILL_START will be applied instead\n')
            #method = RepairMethod.FILL_START

    cdef Py_ssize_t idx, last_valid_idx = -1

    for idx in range(data.shape[0]):
        if not mask[idx]:
            if last_valid_idx != idx - 1:

                if last_valid_idx == -1:
                    if (extrapolate or method == FILL_STOP) and (max_samples == -1 or idx <= max_samples):
                        fill_range(data, mask, data[idx], 0, idx)
                else:
                    if max_samples == -1 or idx - last_valid_idx <= max_samples:
                        # XXX: cannot create more complex condition, otherwise code is not pruned
                        #if cy.np_types is np.float64_t:
                        if method == RepairMethod.INTERPOLATE:
                            interpolate_range_unsafe(data, mask, last_valid_idx, idx)
                        else:  #if method == RepairMethod.FILL_START or method == RepairMethod.FILL_STOP:
                            fill_range(data, mask, data[last_valid_idx] if method == FILL_START else data[idx],
                                       last_valid_idx + 1, idx)

            last_valid_idx = idx

    if (
        (extrapolate or method == FILL_START) and
        last_valid_idx != -1 and
        last_valid_idx != idx and
        (max_samples == -1 or idx - last_valid_idx <= max_samples)
    ):
        fill_range(data, mask, data[last_valid_idx], last_valid_idx + 1, data.shape[0])


cdef repair_mask(array, RepairMethod method=RepairMethod.INTERPOLATE, repair_duration=10, np.float64_t frequency=1,
                 bint copy=False, bint extrapolate=False, bint raise_duration_exceedance=False,
                 bint raise_entirely_masked=True):
    '''
    TODO: find better solution for repair_above kwarg from original.
    '''
    if array.mask.all():  # OPT: calling all and any is faster than calling np.ma.count once
        if raise_entirely_masked:
            raise ValueError('Array cannot be repaired as it is entirely masked')
        return array
    elif not array.mask.any():
        return array

    cdef Py_ssize_t length, repair_samples

    dtype = array.dtype
    # always convert to np.float64 as calling repair_data_mask with fused type isn't working
    array = array.astype(np.float64, copy=copy)

    if repair_duration:
        repair_samples = <Py_ssize_t>(repair_duration * frequency)
        if raise_duration_exceedance:
            length = op.longest_section[np.uint8_t](array.mask)
            if length > repair_samples:
                raise ValueError(
                    f"Length of masked section '{length * frequency}' exceeds repair duration '{repair_duration}'.")
    else:
        repair_samples = -1

    repair_data_mask(array.data, getmaskarray1d(array), method, repair_samples, extrapolate=extrapolate)
    return array.astype(dtype, copy=False)


################################################################################
# Aggregation


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
    return aggregate_values(mode, cy.astype(array), getmaskarray1d(array), matching)


cpdef max_values(array, matching):
    return _aggregate_values(Aggregate.MAX, array, matching)


cpdef min_values(array, matching):
    return _aggregate_values(Aggregate.MIN, array, matching)


cpdef max_abs_values(array, matching):
    return _aggregate_values(Aggregate.MAX_ABS, array, matching)


cpdef min_abs_values(array, matching):
    return _aggregate_values(Aggregate.MIN_ABS, array, matching)


################################################################################
# Alignment


cpdef align(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
            np.float64_t master_offset=0):
    return np.ma.masked_array(*
        (align_nearest(array, slave_frequency, slave_offset, master_frequency, master_offset)
         if np.PyArray_ISINTEGER(array.data) else
         align_interpolate(array, slave_frequency, slave_offset, master_frequency, master_offset)))


@cython.cdivision(True)
@cython.wraparound(False)
cpdef align_interpolate(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
                        np.float64_t master_offset=0):
    '''
    Align slave array to the master frequency and offset by interpolating values between samples accounting for the frequency and
    offset difference.

    OPT: This is a more efficient version of library.align_args(..., interpolate=False).
    '''
    if slave_frequency <= 0 or master_frequency <= 0:
        raise ValueError('frequencies must be greater than 0')

    cdef:
        np.float64_t[:] array_data = cy.astype(array.data)
        np.uint8_t[:] array_mask = getmaskarray1d(array)  # FIXME: find out why getmaskarray1d(array) segfaults!?

    if slave_frequency == master_frequency and slave_offset == master_offset:
        return array_data, array_mask

    cdef:
        np.float64_t array_pos, idx_multiplier = slave_frequency / master_frequency, \
            frequency_multiplier = master_frequency / slave_frequency, \
            offset = idx_multiplier * (slave_offset - master_offset)
        Py_ssize_t array_prev_idx, array_next_idx, output_idx, \
            output_size = <Py_ssize_t>(array_data.shape[0] * frequency_multiplier)
        np.float64_t[:] output_data = cy.zeros_float64(output_size)
        np.uint8_t[:] output_mask = cy.zeros_uint8(output_size)

    for output_idx in range(output_data.shape[0]):
        array_pos = (output_idx * idx_multiplier) + offset
        array_next_idx = <Py_ssize_t>ceil(array_pos)
        if array_pos < 0 or array_next_idx >= array_data.shape[0]:
            output_mask[output_idx] = True
            continue
        array_prev_idx = <Py_ssize_t>floor(array_pos)
        if array_prev_idx == array_pos:
            if array_mask[array_prev_idx]:
                output_mask[output_idx] = True
            else:
                output_data[output_idx] = array_data[array_prev_idx]
        elif array_mask[array_prev_idx] or array_mask[array_next_idx]:
            output_mask[output_idx] = True
        else:
            output_data[output_idx] = array_data[array_prev_idx] + (
                (array_data[array_next_idx] - array_data[array_prev_idx]) * array_pos - array_prev_idx)

    return output_data, output_mask


@cython.cdivision(True)
@cython.wraparound(False)
cpdef align_nearest(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
                    np.float64_t master_offset=0):
    '''
    Align slave array to the master frequency and offset by selecting the nearest sample based on the midpoint between two
    samples accounting for frequency and offset differences.

           0   1
           V   V
    0--------|--------1
    0s   0.4s 0.6s    1s

    OPT: This is a more efficient version of library.align_args(..., interpolate=True) - worst case ~1000x faster.
    >>> array = fda.MappedArray(np.random.random(1000000).round().astype(np.uint32), values_mapping={1: 'Up', 0: 'Down'})
    >>> %timeit align_args(array, 1, 0.1, 2, 0.2, interpolate=False)
    14 s ± 159 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    >>> %timeit align_nearest(array, 1, 0.1, 2, 0.2)
    8.98 ms ± 21.1 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    '''
    if slave_frequency <= 0 or master_frequency <= 0:
        raise ValueError('frequencies must be greater than 0')

    cdef:
        np.uint32_t[:] array_data = cy.astype(array.data, np.uint32)
        np.uint8_t[:] array_mask = getmaskarray1d(array)

    if slave_frequency == master_frequency and fabs(slave_offset - master_offset) * slave_frequency < 0.5:
        return array_data, array_mask

    cdef:
        np.float64_t idx_multiplier = slave_frequency / master_frequency, \
            frequency_multiplier = master_frequency / slave_frequency, \
            offset = idx_multiplier * (master_offset - slave_offset)
        Py_ssize_t array_idx, output_idx, output_size = <Py_ssize_t>(array_data.shape[0] * frequency_multiplier)
        np.uint32_t[:] output_data = cy.zeros_uint32(output_size)
        np.uint8_t[:] output_mask = cy.empty_uint8(output_size)

    for output_idx in range(output_data.shape[0]):
        array_idx = <Py_ssize_t>floor(0.5 + ((output_idx * idx_multiplier) + offset))
        if array_idx < 0 or array_idx >= array_data.shape[0]:
            output_mask[output_idx] = True
        else:
            output_data[output_idx] = array_data[array_idx]
            output_mask[output_idx] = array_mask[array_idx]

    return output_data, output_mask


cpdef straighten(array, np.float64_t full_range):
    cdef:
        Py_ssize_t idx
        np.float64_t[:] data = cy.astype(array.data)
        np.uint8_t[:] mask = getmaskarray1d(array)
        np.float64_t diff, last_value, offset = 0, threshold = 0.75 * full_range

    if not data.shape[0]:
        return

    for idx in range(data.shape[0]):
        if not mask[idx]:
            last_value = data[idx]
            break
    else:
        return

    for idx in range(idx + 1, data.shape[0]):
        if mask[idx]:
            continue

        diff = data[idx] - last_value
        if diff > threshold:
            offset -= full_range
        elif diff < threshold:
            offset += full_range

        last_value = data[idx]
        data[idx] += offset

    return data, mask

