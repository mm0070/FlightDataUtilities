# cython: language_level=3, boundscheck=False
'''
TODO:
- change mask memoryview types to np.bool when supported by Cython and remove .view(np.uint8) from calls
- add const to fused type functions when supported by Cython for immutable buffers
'''
cimport cython
cimport numpy as np

'''
A fused type allows for a 'statically' typed function to accept multiple different types, e.g.
cpdef operation(np_types[:] data, np_types value)
https://cython.readthedocs.io/en/latest/src/userguide/fusedtypes.html

Limitations:
- Fused types do not currenty support the const keyword for numpy types, either within the ctypedef fused section, the
  cython.fused_type(...) function or within function signatures, e.g. cdef func(const np_types x). This is a shame as it precludes
  compatibility with constant buffers, e.g. bytes objects.
- Fused types do not allow numpy types to be conformed into C types. Whereas cdef func(unsigned char value) will automatically
  conform np.uint8_t into the corresponding C type, a fused type containing unsigned char does not accept np.uint8_t.
- Fused types do not support multiple types which represent the same underlying C type, e.g. a fused type is not usable if it
  contains both np.uint8_t and unsigned char.
- When calling a function from Python, the type of a fused type variable is inferred automatically. When calling from Cython,
  input variables must be statically typed, otherwise compilation will fail due to the underlying C function call being ambiguous.
- If multiple different type signatures of the same function must be called within the same scope, the specific signature must
  be specified, e.g. myfunc[double](<double>value); myfunc[float](<float>value)
'''
ctypedef fused np_types:
    np.uint8_t
    np.uint16_t
    np.uint32_t
    np.uint64_t
    np.int8_t
    np.int16_t
    np.int32_t
    np.int64_t
    np.intp_t
    np.float32_t
    np.float64_t

cdef Py_ssize_t NONE_IDX

cdef np.int32_t[:] empty_int32(np.npy_intp psize)
cdef np.int32_t[:, :] empty2d_int32(np.npy_intp x, np.npy_intp y)
cdef np.int32_t[:] zeros_int32(np.npy_intp psize)
cdef np.int32_t[:, :] zeros2d_int32(np.npy_intp x, np.npy_intp y)
cdef np.int64_t[:] empty_int64(np.npy_intp psize)
cdef np.int64_t[:, :] empty2d_int64(np.npy_intp x, np.npy_intp y)
cdef np.int64_t[:] zeros_int64(np.npy_intp psize)
cdef np.int64_t[:, :] zeros2d_int64(np.npy_intp x, np.npy_intp y)
cdef np.intp_t[:] empty_intp(np.npy_intp psize)
cdef np.intp_t[:, :] empty2d_intp(np.npy_intp x, np.npy_intp y)
cdef np.intp_t[:] zeros_intp(np.npy_intp psize)
cdef np.intp_t[:, :] zeros2d_intp(np.npy_intp x, np.npy_intp y)
cdef np.uint8_t[:] empty_uint8(np.npy_intp size)
cdef np.uint8_t[:, :] empty2d_uint8(np.npy_intp x, np.npy_intp y)
cdef np.uint8_t[:] zeros_uint8(np.npy_intp size)
cdef np.uint8_t[:, :] zeros2d_uint8(np.npy_intp x, np.npy_intp y)
cdef np.uint8_t[:] ones_uint8(np.npy_intp size)
cdef np.uint16_t[:] empty_uint16(np.npy_intp size)
cdef np.uint16_t[:, :] empty2d_uint16(np.npy_intp x, np.npy_intp y)
cdef np.uint16_t[:] zeros_uint16(np.npy_intp size)
cdef np.uint16_t[:, :] zeros2d_uint16(np.npy_intp x, np.npy_intp y)
cdef np.uint32_t[:] empty_uint32(np.npy_intp size)
cdef np.uint32_t[:, :] empty2d_uint32(np.npy_intp x, np.npy_intp y)
cdef np.uint32_t[:] zeros_uint32(np.npy_intp size)
cdef np.uint32_t[:, :] zeros2d_uint32(np.npy_intp x, np.npy_intp y)
cdef np.uint64_t[:] empty_uint64(np.npy_intp size)
cdef np.uint64_t[:, :] empty2d_uint64(np.npy_intp x, np.npy_intp y)
cdef np.uint64_t[:] zeros_uint64(np.npy_intp size)
cdef np.uint64_t[:, :] zeros2d_uint64(np.npy_intp x, np.npy_intp y)
cdef np.float64_t[:] empty_float64(np.npy_intp size)
cdef np.float64_t[:, :] empty2d_float64(np.npy_intp x, np.npy_intp y)
cdef np.float64_t[:] zeros_float64(np.npy_intp size)
cdef np.float64_t[:, :] zeros2d_float64(np.npy_intp x, np.npy_intp y)
cdef np.uint16_t read_uint16_le(np.uint8_t[:] data, Py_ssize_t idx) nogil
cdef np.uint16_t read_uint16_be(np.uint8_t[:] data, Py_ssize_t idx) nogil
cdef np.uint32_t read_uint32_le(np.uint8_t[:] data, Py_ssize_t idx) nogil
cdef np.uint32_t read_uint32_be(np.uint8_t[:] data, Py_ssize_t idx) nogil
cdef bint lengths_mismatch(Py_ssize_t x, Py_ssize_t y) nogil
cdef idx_none(Py_ssize_t idx)
cdef Py_ssize_t none_idx(idx)
cdef Py_ssize_t array_wraparound_idx(Py_ssize_t idx, Py_ssize_t length) nogil
cdef Py_ssize_t array_idx(Py_ssize_t idx, Py_ssize_t length) nogil
cdef array_idx_value(Py_ssize_t idx, array)
cdef Py_ssize_t array_stop_idx(Py_ssize_t stop_idx, Py_ssize_t length) nogil
cdef Py_ssize_t prev_idx(const np.uint8_t[:] array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?) nogil
cdef Py_ssize_t next_idx(const np.uint8_t[:] array, Py_ssize_t idx=?, bint match=?, Py_ssize_t stop_idx=?) nogil
cdef Py_ssize_t nearest_idx(np.uint8_t[:] array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?,
                            Py_ssize_t stop_idx=?) nogil
cdef np.uint8_t[:] contract_runs(np.uint8_t[:] data, Py_ssize_t size, bint match=?) nogil
cdef np.uint8_t[:] remove_small_runs(np.uint8_t[:] data, float seconds, float hz=?, bint match=?) nogil


"""
cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil

cpdef bint any_array(array)
cpdef bint all_array(array)
cpdef bint entirely_masked(array)
cpdef bint entirely_unmasked(array)
cpdef Py_ssize_t index_of_subarray_uint8(np.uint8_t[:] array, np.uint8_t[:] subarray, Py_ssize_t start=*) nogil
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
cpdef object idx_none(Py_ssize_t idx)
cpdef Py_ssize_t none_idx(idx)
cdef Py_ssize_t cython_nearest_idx(np.uint8_t[:] array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?, Py_ssize_t stop_idx=?) nogil
cdef void cython_ma_fill_range_float64(np.float64_t[:] data, np.uint8_t[:] mask, double value, Py_ssize_t start, Py_ssize_t stop) nogil
cdef void cython_ma_interpolate_float64(np.float64_t[:] data, np.uint8_t[:] mask, Py_ssize_t start, Py_ssize_t stop) nogil
cpdef void cython_repair_mask_float64(np.float64_t[:] data, np.uint8_t[:] mask, RepairMethod method, Py_ssize_t max_samples, bint extrapolate=?) nogil
cpdef Py_ssize_t longest_section_uint8(np.uint8_t[:] data, np.uint8_t value=?) nogil
cpdef repair_mask(array, method=?, repair_duration=?, frequency=?, bint copy=?, bint extrapolate=?, bint raise_duration_exceedance=?, bint raise_entirely_masked=?)
cpdef max_values(array, matching)
cpdef min_values(array, matching)
cpdef max_abs_values(array, matching)
cpdef min_abs_values(array, matching)
cpdef slices_to_array(Py_ssize_t size, slices)
cpdef section_overlap(a, b)
cpdef remove_small_runs(array, float seconds=?, float hz=?, bint match=?)
cpdef contract_runs(array, Py_ssize_t size, bint match=?)
cpdef bint is_constant(data)
cpdef bint is_constant_uint8(np.uint8_t[:] data) nogil
cpdef bint is_constant_uint16(np.uint16_t[:] data) nogil
cpdef first_valid_sample(array, long start_idx=?)
cpdef last_valid_sample(array, end_idx=?)
cdef Py_ssize_t cython_prev_idx(np.uint8_t[:] array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?) nogil
cdef Py_ssize_t cython_next_idx(np.uint8_t[:] array, Py_ssize_t idx=?, bint match=?, Py_ssize_t stop_idx=?) nogil
cpdef nearest_idx(array, Py_ssize_t idx, bint match=?, Py_ssize_t start_idx=?, Py_ssize_t stop_idx=?)
cpdef nearest_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=?, Py_ssize_t stop_idx=?)
cpdef prev_unmasked_value(array, Py_ssize_t idx, Py_ssize_t start_idx=?)
cpdef next_unmasked_value(array, Py_ssize_t idx, Py_ssize_t stop_idx=?)
cpdef first_unmasked_value(array, Py_ssize_t start_idx=?)
cpdef last_unmasked_value(array, Py_ssize_t stop_idx=?, Py_ssize_t min_samples=?)
cpdef nearest_slice(array, Py_ssize_t idx, bint match=?)
cpdef is_power2_fraction(number)

cdef class Interpolator:
    cdef:
        public np.float64_t[:] _xs, _ys
        public np.float64_t _x_min, _x_max, _y_first, _y_last, _below_multi, _above_multi
        public Py_ssize_t _size

    cdef np.float64_t _interpolate_value(self, np.float64_t value) nogil
    cpdef np.float64_t[:] interpolate(self, np.float64_t[:] array, bint copy=?)


cdef class ByteAligner:
    cdef:
        public Py_ssize_t _idx
        public Py_ssize_t _max_frame_size
        public Py_ssize_t _min_frame_size
        public Py_ssize_t _frame_count
        public bint _little_endian
        public bint _frames_only
        public np.uint8_t[:] _buff
        public np.uint16_t[:] sync_words
        public np.uint16_t[:] _wps_array
        public list _output_arrays
        public Py_ssize_t _output_buffer
        public np.int16_t _wps
        public np.uint16_t _sync_word

    cpdef void reset(self)
    cdef np.uint16_t _get_word(self, Py_ssize_t idx) nogil
    cdef Py_ssize_t _sync_word_idx(self, Py_ssize_t idx) nogil
    cdef np.int16_t _frame_wps(self, Py_ssize_t idx) nogil
    cdef Py_ssize_t _next_frame_idx(self, Py_ssize_t idx) nogil


cdef np.uint16_t[:] sync_words_from_modes(modes)
cpdef swap_bytes(array)
cpdef np.uint16_t[:] unpack_little_endian(np.uint8_t[:] data)
cpdef unpack(array)
cpdef pack(array)
cpdef bytes key_value(np.uint8_t[:] array, key, delimiter, separator, Py_ssize_t start=?)
"""