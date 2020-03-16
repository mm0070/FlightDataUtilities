# cython: language_level=3, boundscheck=False
cimport numpy as np

from flightdatautilities.data cimport cython as cy

################################################################################
# Slice operations
cpdef nearest_slice(array, Py_ssize_t idx, bint match=?)
cpdef slices_to_array(Py_ssize_t size, slices)
################################################################################
# Type-inspecific array operations
cpdef align_arrays(slave_array, master_array)
cpdef concatenate(memviews)
cpdef bint is_constant(cy.np_types[:] data) nogil
cpdef bint is_constant_uint8(const np.uint8_t[:] data) nogil
cpdef Py_ssize_t longest_section(cy.np_types[:] data, cy.np_types value=?) nogil
cpdef straighten(array, np.float64_t full_range)
cpdef sum_arrays(arrays)
cpdef swap_bytes(array)
cpdef np.ndarray twos_complement(np.ndarray array, np.uint64_t bit_length)
cpdef value_idx(cy.np_types[:] array, cy.np_types value)
################################################################################
# Boolean array operations
cpdef contract_runs(array, Py_ssize_t size, bint match=?)
cpdef remove_small_runs(array, Py_ssize_t size, bint match=?)
cpdef remove_small_runs_hz(array, np.float64_t seconds, np.float64_t hz=?, bint match=?)
cpdef section_overlap(const np.uint8_t[:] x, const np.uint8_t[:] y)
################################################################################
# Uint8 array (bytes) operations
cpdef bytes key_value(const np.uint8_t[:] array, const np.uint8_t[:] key, const np.uint8_t[:] delimiter, const np.uint8_t[:] separator, Py_ssize_t start=?)
cpdef np.uint8_t[:] merge_bool_arrays(masks)
cpdef np.uint8_t[:] merge_bool_arrays_upsample(masks)
cpdef bint subarray_exists_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=?) nogil
cpdef subarray_idx_uint8(const np.uint8_t[:] array, const np.uint8_t[:] subarray, Py_ssize_t start=*)
################################################################################
# Resample operations
cpdef downsample_arrays(arrays)
cpdef upsample_arrays(arrays)
################################################################################
# Array serialisation
cpdef save_compressed(path, array)
cpdef load_compressed(path)
################################################################################
# Alignment
cpdef np.float64_t[:] align_interpolate(np.float64_t[:] input, np.float64_t slave_frequency,
                                        np.float64_t slave_offset, np.float64_t master_frequency,
                                        np.float64_t master_offset=?)
#cpdef np.uint8_t[:] align_bool(np.uint8_t[:] slave, master)
################################################################################
# Flight Data Recorder data operations
cpdef np.uint8_t[:] pack(const np.uint8_t[:] array)
cpdef np.uint8_t[:] unpack(const np.uint8_t[:] array)
cpdef np.uint16_t[:] unpack_little_endian(const np.uint8_t[:] data)
