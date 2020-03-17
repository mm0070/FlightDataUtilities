# cython: language_level=3, boundscheck=False
cimport numpy as np

################################################################################
# Power of 2
cpdef bint is_power2(number)
cpdef bint is_power2_fraction(number)
################################################################################
# Random
cdef int randint(int min, int max) nogil
################################################################################
# Bits
cdef np.uint64_t full_range(np.uint64_t bit_length) nogil
cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil
################################################################################
# Unit conversion
cdef np.float64_t degrees_to_radians(np.float64_t degrees) nogil
cdef np.float64_t radians_to_degrees(np.float64_t radians) nogil

