# cython: language_level=3, boundscheck=False
'''
Scalar functions.
'''
import cython
import numpy as np
cimport numpy as np

from libc.stdlib cimport rand, RAND_MAX


cpdef bint is_power2(number):
    '''
    Whether or not a number is a power of two. Forces floats to int.
    Ref: http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/

    opt: ~4x faster than pure python version
    '''
    if number % 1:
        return False
    cdef int num = <int>number
    return num > 0 and ((num & (num - 1)) == 0)


cpdef bint is_power2_fraction(number):
    '''
    Whether or not a number is a power of two or one divided by a power of two.

    :type number: int or float
    :returns: if the number is either a power of 2 or a fraction, e.g. 4, 2, 1, 0.5, 0.25
    :rtype: bool
    '''
    if 0 < number < 1:
        number = 1 / number
    return is_power2(number)


cdef int randint(int min, int max) nogil:
    '''
    Cython equivalent of random.randint.
    '''
    if min > max:
        min, max = max, min
    return rand() % (max + 1 - min) + min


cdef np.uint64_t saturated_value(np.uint64_t bit_length) nogil:
    return (2 ** bit_length) - 1

