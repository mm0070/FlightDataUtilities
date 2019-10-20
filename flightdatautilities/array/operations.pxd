# cython: language_level=3, boundscheck=False
cimport numpy as np

from flightdatautilities.array cimport cython as cy


cdef enum Aggregate:
    MAX, MIN, MAX_ABS, MIN_ABS

cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil

cpdef bint any_array(array)
cpdef bint all_array(array)
cpdef bint entirely_masked(array)
cpdef bint entirely_unmasked(array)
cpdef Py_ssize_t index_of_subarray_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=*) nogil
cpdef bint subarray_exists_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=?) nogil
cpdef Py_ssize_t array_index_uint16(unsigned short value, np.uint16_t[:] sync_words) nogil
cpdef merge_masks(masks)
cpdef mask_ratio(mask)
cpdef percent_unmasked(mask)
cpdef sum_arrays(arrays)
cpdef downsample_arrays(arrays)
cpdef upsample_arrays(arrays)
cpdef align_arrays(slave_array, master_array)
cpdef save_compressed(path, array)
cpdef load_compressed(path)
cpdef bint is_power2(number)
cpdef is_power2_fraction(number)
cpdef np.ndarray twos_complement(np.ndarray array, np.uint64_t bit_length)
cpdef Py_ssize_t longest_section(cy.np_types[:] data, cy.np_types value=?) nogil
cpdef max_values(array, matching)
cpdef min_values(array, matching)
cpdef max_abs_values(array, matching)
cpdef min_abs_values(array, matching)
cpdef slices_to_array(Py_ssize_t size, slices)
cpdef section_overlap(a, b)
cpdef remove_small_runs(array, float seconds=?, float hz=?, bint match=?)
cpdef contract_runs(array, Py_ssize_t size, bint match=?)
cpdef bint is_constant(cy.np_types[:] data) nogil
cpdef first_valid_sample(array, Py_ssize_t start_idx=?)
cpdef last_valid_sample(array, end_idx=?)
cpdef nearest_idx(array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?, Py_ssize_t stop_idx=?)
cpdef nearest_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=?, Py_ssize_t stop_idx=?)
cpdef prev_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=?)
cpdef next_unmasked_value(array, Py_ssize_t idx, Py_ssize_t stop_idx=?)
cpdef first_unmasked_value(array, Py_ssize_t start_idx=?)
cpdef last_unmasked_value(array, Py_ssize_t stop_idx=?, Py_ssize_t min_samples=?)
cpdef nearest_slice(array, Py_ssize_t idx, bint match=?)
cpdef is_power2_fraction(number)
cpdef swap_bytes(array)
cpdef np.uint16_t[:] unpack_little_endian(const np.uint8_t[:] data)
cpdef np.uint8_t[:] unpack(const np.uint8_t[:] array)
cpdef np.uint8_t[:] pack(const np.uint8_t[:] array)
cpdef bytes key_value(const np.uint8_t[:] array, const np.uint8_t[:] key, const np.uint8_t[:] delimiter, const np.uint8_t[:] separator, Py_ssize_t start=?)


"""
cpdef void section_overlap_uint8(unsigned char[:] x, unsigned char[:] y, unsigned char[:] out) nogil
cpdef unsigned char[:] remove_small_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cpdef unsigned char[:] contract_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cdef void masked_array_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil
cdef void masked_array_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil
cpdef void repair_mask_float64(double[:] data, unsigned char[:] mask, int mode, long max_samples, bint extrapolate=?) nogil
cdef long longest_zeros_uint8(unsigned char[:] mask) nogil
"""
