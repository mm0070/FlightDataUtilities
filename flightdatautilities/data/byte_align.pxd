# cython: language_level=3, boundscheck=False
cimport numpy as np


cdef np.uint16_t[:] sync_words_from_modes(modes)

cdef class ByteAligner:
    cdef:
        public bint little_endian
        Py_ssize_t _idx
        Py_ssize_t _max_frame_size
        Py_ssize_t _min_frame_size
        Py_ssize_t _frame_count
        bint _frames_only
        np.uint8_t[:] _buff
        np.uint16_t[:] sync_words
        np.uint16_t[:] _wps_array
        list _output_arrays
        Py_ssize_t _output_buffer
        np.int16_t _wps
        np.uint16_t _sync_word

    cpdef void reset(self)
    cdef np.uint16_t _get_word(self, Py_ssize_t idx) nogil
    cdef Py_ssize_t _sync_word_idx(self, Py_ssize_t idx) nogil
    cdef np.int16_t _frame_wps(self, Py_ssize_t idx) nogil
    cdef Py_ssize_t _next_frame_idx(self, Py_ssize_t idx) nogil

