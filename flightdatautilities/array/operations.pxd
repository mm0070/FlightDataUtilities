# cython: language_level=3, boundscheck=False
cimport numpy as np

from flightdatautilities.array cimport cython as cy


cpdef bint any_array(array)
cpdef bint all_array(array)
cpdef bint entirely_masked(array)
cpdef bint entirely_unmasked(array)
cpdef subarray_idx_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=*)
cpdef bint subarray_exists_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=?) nogil
cpdef value_idx(cy.np_types[:] array, cy.np_types value)
cpdef merge_masks(masks)
cpdef np.uint8_t[:] merge_masks_uint8(masks)
cpdef mask_ratio(mask)
cpdef percent_unmasked(mask)
cpdef sum_arrays(arrays)
cpdef downsample_arrays(arrays)
cpdef upsample_arrays(arrays)
cpdef align_arrays(slave_array, master_array)
cpdef save_compressed(path, array)
cpdef load_compressed(path)
cpdef np.ndarray twos_complement(np.ndarray array, np.uint64_t bit_length)
cpdef Py_ssize_t longest_section(cy.np_types[:] data, cy.np_types value=?) nogil
cpdef slices_to_array(Py_ssize_t size, slices)
cpdef section_overlap(a, b)
cpdef remove_small_runs(array, np.float64_t seconds=?, np.float64_t hz=?, bint match=?)
cpdef contract_runs(array, Py_ssize_t size, bint match=?)
cpdef bint is_constant(cy.np_types[:] data) nogil
cpdef nearest_slice(array, Py_ssize_t idx, bint match=?)
cpdef swap_bytes(array)
cpdef np.uint16_t[:] unpack_little_endian(const np.uint8_t[:] data)
cpdef np.uint8_t[:] unpack(const np.uint8_t[:] array)
cpdef np.uint8_t[:] pack(const np.uint8_t[:] array)
cpdef bytes key_value(const np.uint8_t[:] array, const np.uint8_t[:] key, const np.uint8_t[:] delimiter, const np.uint8_t[:] separator, Py_ssize_t start=?)
