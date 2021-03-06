__all__ = ['dcompact', 'dmerge']


def dcompact(d):
    '''
    Compacts a dictionary (removes all empty values).

    :param d: The dictionary to compact.
    :type d: dict:
    :returns: A dictionary with empty values removed.
    :rtype: dict
    '''
    # Filter out any unset/empty values in the dictionary:
    o = d.__class__()
    for k, v in d.items():
        if isinstance(v, dict):
            x = dcompact(v)
        elif isinstance(v, str):
            x = v.strip()
        else:
            x = v
        if bool(x) or x == 0:
            o[k] = x
    return o


def dmerge(x, y, overwrite=()):
    '''
    Deep merges dictionary ``y`` into dictionary ``x``.

    If a key from ``y`` exists in ``x``, the value of ``y`` is used unless both
    values are dictionaries that can be merged.

    The ``overwrite`` option allows for a list of keys in the nested dictionary
    that should not be merged at any level, merely overwritten.

    Beware! Although objects are merged, they may not be copied and thus are
    shared references into the original dictionary that was merged in.

    :param x: The dictionary to recursively merge into.
    :type x: dict
    :param y: The dictionary to be merged in.
    :type y: dict
    :param overwrite: A list of keys where the value should be overwritten.
    :type overwrite: list or tuple
    '''
    if not isinstance(x, dict) or not isinstance(y, dict):
        raise TypeError('Arguments must be dictionaries.')
    for k, v in y.items():
        if not isinstance(v, dict):
            x[k] = v
        elif k not in x.keys():
            x[k] = v.copy()
        elif not isinstance(x[k], dict):
            x[k] = v.copy()
        elif k in overwrite:
            x[k] = v.copy()
        else:
            dmerge(x[k], v, overwrite=overwrite)
    return x
