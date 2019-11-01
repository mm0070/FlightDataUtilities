__all__ = ['dcompact', 'dmerge']


def dcompact(d):
    '''
    Compacts a dictionary (removes all empty values).

    :param d: The dictionary to compact.
    :type d: dict:
    :returns: A dictionary with empty values removed.
    :rtype: dict
    '''
    # New output dictionary:
    o = d.__class__()

    # Filter out any unset/empty values in the dictionary:
    for k, v in d.items():
        if isinstance(v, dict):
            x = dcompact(v)
        elif isinstance(v, (bytes, str)):
            x = v.strip()
        else:
            x = v
        if bool(x) or x == 0:
            o[k] = x

    # Return the new dictionary:
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


# XXX: Deprecated: Badly engineered...
def dict_filter(d, keep=None, remove=None):
    '''
    Filter a dictionary specifying which keys should stay and which should be
    removed.

    :param d: A dictionary to filter keys on.
    :type d: dict
    :param keep: A list of keys to be kept within the output dictionary.
    :type keep: list
    :param remove: A list of keys to be removed from the output dictionary.
    :type remove: list
    '''
    def replace_down(x, wildkey, thiskey):
        new_dict = {}
        try:
            for key,value in x.items():
                new_dict[key] = replace_down(x[key], wildkey, thiskey)
        except:
            try:
                x = re.sub(wildkey, thiskey , x)
            except:
                pass
            return x
        return new_dict

    if keep and remove:
        raise ValueError('Cannot keep and remove at the same time!')
    if keep:
        f = lambda k, v: k in keep
        return_dict = d.__class__((k, v) for k, v in d.items() if f(k, v))
    elif remove:
        f = lambda k, v: k not in remove
        return_dict = d.__class__((k, v) for k, v in d.items() if f(k, v))
    else:
        return_dict = d

    # return return_dict # Was the end

    # Extract the wildcard entries from d
    import re
    new_dict={}
    if keep==None:
        return return_dict
    for key in d:
        if '(*)' in key:
            wildkey = key.replace("(*)","\\(\\w*\\)") # This format for re.compile
            wild_one = re.compile(wildkey)
            for thiskey in keep:
                pos = wild_one.match(thiskey)
                if pos:
                    wildkey = key.replace("(*)","\\(\\*\\)") # This format for re()
                    new_dict[thiskey]=replace_down(d[key], wildkey, thiskey)

    return dict(return_dict.items() + new_dict.items())


################################################################################
