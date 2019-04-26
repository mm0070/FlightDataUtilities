# cython: language_level=3, boundscheck=False
cdef enum RepairMethod:
    FILL_START, FILL_STOP, INTERPOLATE

cdef enum Aggregate:
    MAX, MIN, MAX_ABS, MIN_ABS

cpdef long index_of_subarray_uint8(unsigned char[:] array, unsigned char[:] subarray, unsigned long start=*) nogil
cpdef long array_index_uint16(unsigned short value, unsigned short[:] sync_words) nogil
cdef object idx_none(long idx)
cdef long none_idx(idx)
cdef long cython_nearest_idx(unsigned char[:] array, long idx, bint match=?, long start_idx=?, long stop_idx=?) nogil
cdef void cython_ma_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil
cdef void cython_ma_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil
cpdef void cython_repair_mask_float64(double[:] data, unsigned char[:] mask, RepairMethod method, long max_samples, bint extrapolate=?) nogil
cdef long longest_zeros_uint8(unsigned char[:] mask) nogil
cpdef bint is_constant_uint8(unsigned char[:] data) nogil
cpdef bint is_constant_uint16(unsigned short[:] data) nogil


cdef class Interpolator:
    cdef:
        public double[:] _xs, _ys
        public double _x_min, _x_max, _y_first, _y_last, _below_multi, _above_multi
        public unsigned int _size

    cdef double _interpolate_value(self, double value) nogil
    cpdef double[:] interpolate(self, double[:] array, bint copy=?)


cdef class ByteAligner:
    cdef:
        public long long _idx
        public int _max_frame_size
        public int _min_frame_size
        public unsigned int _frame_count
        public bint _little_endian
        public bint _frames_only
        public unsigned char[:] _buff
        public unsigned short[:] sync_words
        public unsigned short[:] _wps_array
        public list _output_arrays
        public int _output_buffer
        public int _wps
        public short _sync_word

    cpdef void reset(self)
    cdef unsigned short _get_word(self, long long idx) nogil
    cdef int _sync_word_idx(self, long long idx) nogil
    cdef short _frame_wps(self, long long idx) nogil
    cdef long long _next_frame_idx(self, long long idx) nogil


cpdef unsigned short[:] sync_words_from_modes(modes)


"""
cpdef void section_overlap_uint8(unsigned char[:] x, unsigned char[:] y, unsigned char[:] out) nogil
cpdef unsigned char[:] remove_small_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cpdef unsigned char[:] contract_runs_uint8(unsigned char[:] array, unsigned int size) nogil
cdef void masked_array_fill_range_float64(double[:] data, unsigned char[:] mask, double value, long start, long stop) nogil
cdef void masked_array_interpolate_float64(double[:] data, unsigned char[:] mask, long start, long stop) nogil
cpdef void repair_mask_float64(double[:] data, unsigned char[:] mask, int mode, long max_samples, bint extrapolate=?) nogil
cdef long longest_zeros_uint8(unsigned char[:] mask) nogil
"""
