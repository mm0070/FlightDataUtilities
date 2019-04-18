# cython: language_level=3, boundscheck=False
cdef enum RepairMethod:
    FILL_START, FILL_STOP, INTERPOLATE

cdef enum Aggregate:
    MAX, MIN, MAX_ABS, MIN_ABS

cdef object idx_none(long idx)
cdef long none_idx(idx)
cdef long cython_nearest_idx(unsigned char[:] array, long idx, bint match=?, long start_idx=?, long stop_idx=?) nogil
cdef void cython_ma_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil
cdef void cython_ma_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil
cpdef void cython_repair_mask_float64(double[:] data, unsigned char[:] mask, RepairMethod method, long max_samples, bint extrapolate=?) nogil
cdef long longest_zeros_uint8(unsigned char[:] mask) nogil
"""
cpdef void section_overlap_uint8(unsigned char[:] x, unsigned char[:] y, unsigned char[:] out) nogil
cpdef unsigned char[:] remove_small_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cpdef unsigned char[:] contract_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cdef void masked_array_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil
cdef void masked_array_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil
cpdef void repair_mask_float64(double[:] data, unsigned char[:] mask, int mode, long max_samples, bint extrapolate=?) nogil
cdef long longest_zeros_uint8(unsigned char[:] mask) nogil
"""
