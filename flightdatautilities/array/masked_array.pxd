# cython: language_level=3, boundscheck=False
cimport cython
cimport numpy as np

from flightdatautilities.array cimport cython as cy

cdef enum RepairMethod:
    FILL_START, FILL_STOP, INTERPOLATE

cdef np.uint8_t[:] getmaskarray1d(array)
cdef void fill_range_unsafe(cy.np_types[:] data, np.uint8_t[:] mask, cy.np_types value, Py_ssize_t start_idx,
                            Py_ssize_t stop_idx) nogil
cdef void fill_range(cy.np_types[:] data, np.uint8_t[:] mask, cy.np_types value, Py_ssize_t start,  # TODO
                     Py_ssize_t stop) nogil
cdef void interpolate_range_unsafe(np.float64_t[:] data, np.uint8_t[:] mask, Py_ssize_t start_idx, Py_ssize_t stop_idx) nogil
cdef void interpolate_range(np.float64_t[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil
cdef void repair_data_mask(np.float64_t[:] data, np.uint8_t[:] mask, RepairMethod method, Py_ssize_t max_samples,
                           bint extrapolate=?) nogil
cdef repair_mask(array, RepairMethod method=?, repair_duration=?, np.float64_t frequency=?, bint copy=?, bint extrapolate=?,
                  bint raise_duration_exceedance=?, bint raise_entirely_masked=?)