# cython: language_level=3, boundscheck=False
cimport numpy as np

cdef class Interpolator:
    cdef:
        np.float64_t[:] _xs, _ys
        np.float64_t _x_min, _x_max, _y_first, _y_last, _below_multi, _above_multi
        Py_ssize_t _size

    cdef np.float64_t _interpolate_value(self, np.float64_t value) nogil
    cpdef np.float64_t[:] interpolate(self, np.float64_t[:] array, bint copy=?)

