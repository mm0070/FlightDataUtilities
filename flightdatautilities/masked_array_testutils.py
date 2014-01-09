# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Additional functions for testing masked arrays.

These build on the functions provided in the ``numpy.ma.testutils`` module.
'''

##############################################################################
# Imports


from numpy.ma.testutils import *  # noqa


##############################################################################
# Functions


def assert_masked_array_approx_equal(x, y, decimal=6, err_msg='', verbose=True):
    '''
    Checks the elementwise equality of two masked arrays, up to a given
    number of decimals. Also checks that the masks are equivalent.
    '''
    compare = lambda x, y: approx(x, y, rtol=10. ** -decimal)
    assert_array_compare(compare, x, y, err_msg=err_msg, verbose=verbose,
                         header='Arrays are not approx equal')
    assert_mask_equivalent(x.mask, y.mask, err_msg='Masks are not equivalent')


def assert_masked_array_almost_equal(x, y, decimal=6, err_msg='', verbose=True):
    '''
    Checks the elementwise equality of two masked arrays, up to a given
    number of decimals. Also checks that the masks are equivalent.
    '''
    compare = lambda x, y: almost(x, y, decimal)
    assert_array_compare(compare, x, y, err_msg=err_msg, verbose=verbose,
                         header='Arrays are not almost equal')
    assert_mask_equivalent(x.mask, y.mask, err_msg='Masks are not equivalent')


def assert_masked_array_equal(x, y, err_msg='', verbose=True):
    '''
    Checks the elementwise equality of two masked arrays. Also checks that the
    masks are equivalent.
    '''
    compare = operator.__eq__
    assert_array_compare(compare, x, y, err_msg=err_msg, verbose=verbose,
                         header='Arrays are not equal')
    assert_mask_equivalent(x.mask, y.mask, err_msg='Masks are not equivalent')


def assert_mask_equivalent(m1, m2, err_msg=''):
    '''
    Asserts the equality of two masks.

    This is an amended version of ``np.ma.testutils.assert_mask_equal`` to
    allow for one test array to have no mask and the other to have a mask array
    where each element is ``False``. We want to handle this situation as the
    two arrays are functionally equivalent.
    '''
    if m1 is nomask or not np.any(m1):
        assert_(m2 is nomask or not np.any(m2), msg=err_msg)
    if m2 is nomask or not np.any(m2):
        assert_(m1 is nomask or not np.any(m1), msg=err_msg)
    assert_array_equal(m1, m2, err_msg=err_msg)
