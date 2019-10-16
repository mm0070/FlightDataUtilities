'''
Upgrading from Python 2.7 to Python 3.7 and using numpy versions past 1.10.x
requires helper methods to help maintain consistent behaviour from an existing
codebase. 
'''

# Python 3 and Numpy 1.15+ upgrade helpers
import math
import numpy as np

def py2round(x, d=0):
    '''
    Provide the same rounding behaviour as the round() method in Python 2
    '''
    p = 10 ** d
    return float(math.floor((x * p) + math.copysign(0.5, x))) / p


def slices_int(*args):
    '''
    Create or modify a slice, ensuring that a data in a slice,
    or a list of slices, are integers or NoneType.

    cast a single slice to an integar slice:
       slices_int(slice) -> slice

    cast multiple slices returns a list of integar slices:
       slices_int([slice, slice, ...]) -> [slice, slice, ...]
       slices_int((slice, slice, ...)) -> [slice, slice, ...]

    create an integar slice:

       slices_int(value) -> slice(int(value))
    value can be an int, float or numpy.number based value.

       slices_int(value, value) -> slice(int(value), int(value))
       slices_int(value, value, value) -> slice(int(value), int(value), int(value))
    value can be an NoneType, int, float or numpy.number based value.
    '''
    def make_slice_int(s):
        return slice(int_idx(s.start), int_idx(s.stop), int_idx(s.step))
    arg_len = len(args)
    if arg_len == 1 and isinstance(args[0], slice):
        return make_slice_int(args[0])
    elif arg_len == 1 and isinstance(args[0], (int, float, np.number)):
        return slice(int(args[0]))
    elif arg_len == 1 and all(isinstance(_s, slice) for _s in args[0]):
        return [make_slice_int(_s) for _s in args[0]]
    elif arg_len in (2, 3) and \
         all(isinstance(_s, (int, float, np.number)) or _s is None for _s in args):
        return slice(int_idx(args[0]), int_idx(args[1]),
                     None if arg_len==2 or args[2] is None else int(args[2]))
    else:
        if arg_len == 1:
            raise TypeError("slices_int needs to be a slice, "
                            "multiple slices or a value type of int, "
                            "float, np.number")
        if arg_len in (2, 3):
            raise TypeError("slices_int needs 2 or 3 values with the type of"
                            " int, float, np.number")
        else:
            raise TypeError("slices_int expects 1 to 3 arguments. Got %s",
                            arg_len)


def np_ma_zeros(fill_value):
    return np.ma.zeros(
        int_idx(fill_value)
    )


def int_idx(value):
    return None if value is None else int(value)
