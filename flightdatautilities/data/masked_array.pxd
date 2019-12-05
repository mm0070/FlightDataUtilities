# cython: language_level=3, boundscheck=False
cimport cython
cimport numpy as np

from flightdatautilities.data cimport cython as cy

cdef enum Aggregate:
    MAX, MIN, MAX_ABS, MIN_ABS

cdef enum RepairMethod:
    FILL_START, FILL_STOP, INTERPOLATE

################################################################################
# Utility functions
cdef np.uint8_t[:] getmaskarray1d(array)
################################################################################
# Mask ratio/percentage
cpdef mask_ratio(mask)
cpdef percent_unmasked(mask)
################################################################################
# Merge masks
cpdef merge_masks(masks)
cpdef np.uint8_t[:] merge_masks_uint8(masks)
cpdef np.uint8_t[:] merge_masks_upsample_uint8(masks)
################################################################################
# Find unmasked values
cpdef prev_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start=?)
cpdef next_unmasked_value(array, Py_ssize_t idx, Py_ssize_t stop=?)
cpdef nearest_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start=?, Py_ssize_t stop=?)
################################################################################
# Fill range
cdef void fill_range(cy.np_types[:] data, np.uint8_t[:] mask, cy.np_types value, Py_ssize_t start,
                     Py_ssize_t stop) nogil
################################################################################
# Interpolate range
cdef void interpolate_range_unsafe(cy.np_types[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil
cdef void interpolate_range(cy.np_types[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil
################################################################################
# Repair mask
cdef void repair_data_mask(np.float64_t[:] data, np.uint8_t[:] mask, RepairMethod method, Py_ssize_t max_samples,
                           bint extrapolate=?) nogil
cdef repair_mask(array, RepairMethod method=?, repair_duration=?, np.float64_t frequency=?, bint copy=?, bint extrapolate=?,
                  bint raise_duration_exceedance=?, bint raise_entirely_masked=?)
################################################################################
# Aggregate functions
cpdef max_values(array, matching)
cpdef min_values(array, matching)
cpdef max_abs_values(array, matching)
cpdef min_abs_values(array, matching)
################################################################################
# Alignment
cpdef align(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
            np.float64_t master_offset=?)
cpdef align_interpolate(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
                        np.float64_t master_offset=?)
cpdef align_nearest(array, np.float64_t slave_frequency, np.float64_t slave_offset, np.float64_t master_frequency,
                    np.float64_t master_offset=?)
