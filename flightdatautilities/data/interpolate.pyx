# cython: language_level=3, boundscheck=False
import numpy as np
cimport numpy as np
import scipy

from flightdatautilities.data cimport cython as cy


cdef class Interpolator:
    '''
    Interpolator object for applying interpolation points to arrays.
    Extrapolates values outside of the interpolation points.

    Tested against interp1d after being optimized in scipy 0.17.0 (exact same points and data):
    # interp1d
    In [21]: %timeit s(x)
    1 loops, best of 3: 272 ms per loop
    # Interpolator
    In [23]: %timeit i.interpolate(x)
    10 loops, best of 3: 76.6 ms per loop

    References:
     - http://www.zovirl.com/2008/11/04/interpolated-lookup-tables-in-python/
     - http://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-an-extrapolated-result-beyond-the-input-range
    '''

    def __cinit__(self, points):
        '''
        :param points: An iterable of x, y points.
        :type points: [(int, int), ...]
        '''
        cdef:
            Py_ssize_t idx, size = len(points)

        if size < 2:
            raise ValueError('At least 2 interpolation points are required.')

        self._xs = cy.empty_float64(size)
        self._ys = cy.empty_float64(size)
        for idx, (x, y) in enumerate(sorted(points)):
            self._xs[idx] = x
            self._ys[idx] = y

        self._x_min = self._xs[0]
        self._x_max = self._xs[size - 1]
        self._y_first = self._ys[0]
        self._y_last = self._ys[size - 1]

        self._below_multi = (self._ys[1] - self._y_first) / (self._xs[1] - self._x_min)
        self._above_multi = (self._y_last - self._ys[size - 2]) / (self._x_max - self._xs[size - 2])

        self._size = size

    cdef np.float64_t _interpolate_value(self, np.float64_t value) nogil:
        '''
        Interpolate a value according to the Interpolator's interpolation points.

        :param value: Original value.
        :type value: double
        :returns: Interpolated value.
        :rtype: double
        '''
        cdef:
            Py_ssize_t idx = 1

        for idx in range(idx, self._size):
            if value <= self._xs[idx]:
                break

        cdef:
            np.float64_t x_hi = self._xs[idx], x_lo = self._xs[idx - 1], \
                y_hi = self._ys[idx], y_lo = self._ys[idx - 1], slope = (y_hi - y_lo) / (x_hi - x_lo)
        return y_lo + (slope * (value - x_lo))

    cpdef np.float64_t[:] interpolate(self, np.float64_t[:] array, bint copy=True):
        '''
        Interpolate (and extrapolate) an array according to the Interpolator's interpolation points.

        :param array: Original value.
        :type array: np.float[:] (memoryview)
        :param copy: Create a copy of the original array to not modify values inplace.
        :type copy: bint
        :returns: Interpolated array.
        :rtype: np.float[:] (memoryview)
        '''
        cdef:
            Py_ssize_t idx
            np.float64_t value
            np.float64_t[:] output

        if copy:
            output = cy.empty_float64(array.shape[0])
        else:
            output = array

        for idx in range(array.shape[0]):
            value = array[idx]
            if value < self._x_min:
                output[idx] = self._y_first + (value - self._x_min) * self._below_multi
            elif value > self._x_max:
                output[idx] = self._y_last + (value - self._x_max) * self._above_multi
            else:
                output[idx] = self._interpolate_value(value)

        return output


def extrap1d(interpolator):
    '''
    Extends scipy.interp1d which extrapolates values outside of the interpolation points.
    http://stackoverflow.com/questions/2745329/how-to-make-scipy-interpolate-give-a-an-extrapolated-result-beyond-the-input-ran
    Optimised interpolation with extrapolation has been implemented in Interpolator.
    '''
    xs = interpolator.x
    ys = interpolator.y

    def pointwise(x):
        if x < xs[0]:
            return ys[0] + (x - xs[0]) * (ys[1] - ys[0]) / (xs[1] - xs[0])
        elif x > xs[-1]:
            return ys[-1] + (x - xs[-1]) * (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
        else:
            return interpolator(x)

    def ufunclike(xs):
        return scipy.array(map(pointwise, scipy.array(xs)))

    return ufunclike

