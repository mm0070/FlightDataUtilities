import numpy as np

from collections import Sequence


# XXX: _memoryviewslice is a cython oddity that is not importable.
ARRAY_TYPES = {'ndarray'}
MEMORYVIEW_TYPES = {'memoryview', '_memoryviewslice'}
ARRAY_LIKE_TYPES = ARRAY_TYPES | MEMORYVIEW_TYPES


def as_dtype(obj, dtype=None, copy=False, cast=False):
    '''
    Returns str or array as str or array with specified dtype.

    :type obj: str or np.array
    :type dtype: np.dtype or str or None
    :type copy: bool
    :type cast: bool
    :rtype: str or np.array
    '''
    if dtype is None and is_array_like(obj):
        obj = obj.tostring()
    elif dtype is not None:
        if is_bytes(obj):
            obj = np.fromstring(obj, dtype=dtype)
        else:
            if is_memoryview(obj):
                obj = np.asarray(obj)
            if obj.dtype != dtype:
                obj = obj.astype(dtype, copy=copy) if cast else obj.view(dtype)
    return obj


def as_int(obj):
    '''
    Returns obj cast as integer, unpacks if wrapped in a sequence.

    :type obj: int, float or list
    :rtype: int
    '''
    try:
        return int(obj)
    except TypeError:
        # list
        if len(obj) == 1:
            return int(obj[0])
        else:
            raise ValueError('single value is required')


def as_sequence(obj):
    '''
    Returns obj wrapped in a list if not already a sequence.

    :type obj: None, int, float or list
    :returns: obj unchanged if obj is sequence or None else obj wrapped in a list
    :rtype: collections.Sequence or None
    '''
    return obj if isinstance(obj, Sequence) or obj is None else [obj]


def byte_size(data):
    '''
    Size in bytes of data.

    :type data: bytes or np.ndarray
    :rtype: int
    '''
    length = len(data)
    if is_array_like(data):
        length *= data.dtype.itemsize
    return length


def is_array(obj):
    '''
    Check if an object is an array type.

    :param obj: Object to be checked.
    :type obj: object
    :rtype: bool
    '''
    return obj.__class__.__name__ in ARRAY_TYPES


def is_array_like(obj):
    '''
    Check if an object is an array type.

    :param obj: Object to be checked.
    :type obj: object
    :rtype: bool
    '''
    return obj.__class__.__name__ in ARRAY_LIKE_TYPES


def is_bytes(data):
    '''
    Check if data is bytes (bytes for Python 3, str for Python 2).
    '''
    return data.__class__ == bytes


def is_data(data):
    '''
    Whether or not object is data (array-like or bytes).
    '''
    return is_array_like(data) or is_bytes(data)


def is_generator(obj):
    '''
    Replacement for inspect.isgenerator which works with Cython generators.

    https://bitbucket.org/simpy/simpy/issues/73/
    '''
    return hasattr(obj, 'throw')


def is_data_iterable(obj):
    '''
    Whether or not object is an iterable of data chunks.
    '''
    return not isinstance(obj, (bytes, str)) and (isinstance(obj, Sequence) or is_generator(obj))


def is_memoryview(obj):
    '''
    Check if an object is a memoryview.

    :param obj: Object to be checked.
    :type obj: object
    :rtype: bool
    '''
    return obj.__class__.__name__ in MEMORYVIEW_TYPES


def is_split(obj):
    return isinstance(obj, dict)

