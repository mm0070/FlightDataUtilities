# cython: language_level=3, boundscheck=False
cimport numpy as np

from flightdatautilities.array cimport cython as cy

cpdef bint is_power2(number)
cpdef bint is_power2_fraction(number)
cdef int randint(int min, int max) nogil
cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil


