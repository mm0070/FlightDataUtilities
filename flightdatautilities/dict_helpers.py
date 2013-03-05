# -*- coding: utf-8 -*-
################################################################################


__all__ = ['dcompact', 'dflatten', 'dfilter', 'dmap', 'dmerge']


def dcompact(d):
    '''
    Compacts a dictionary (removes all empty values).

    :param d: The dictionary to compact.
    :type d: dict:
    :returns: A dictionary with empty values removed.
    :rtype: dict
    '''
    # New output dictionary:
    o = {}

    # Filter out any unset/empty values in the dictionary:
    for k, v in d.iteritems():
        if isinstance(v, dict):
            x = dcompact(v)
        elif isinstance(v, basestring):
            x = v.strip()
        else:
            x = v
        if bool(x) or x == 0:
            o[k] = x

    # Return the new dictionary:
    return o


def dflatten(d, glue=' ', manipulate=lambda k: k):
    '''
    Flatten a dictionary joining nested keys together with the provided string.

    Additionally a manipulation function may be passed in for modifying keys.

    :param d: The dictionary to flatten.
    :type d: dict
    :param glue: The string to glue keys together with.
    :type glue: str
    :param manipulate: An optional key manipulation function.
    :type manipulate: function
    :returns: A flattened dictionary.
    :rtype: dict
    '''
    # New output dictionary:
    o = {}

    # Loop over dictionary items and recursively flatten:
    for k0, v0 in d.iteritems():
        if isinstance(v0, dict):
            # Flatten nested dictionary and glue manipulated keys:
            for k1, v1 in dflatten(v0).iteritems():
                k = glue.join(map(manipulate, [k0, k1]))
                o[k] = v1
        else:
            # Manipulate key and assign value:
            k = manipulate(k0)
            o[k] = v0

    # Return the new dictionary:
    return o


def dfilter(f, d):
    '''
    An equivalent of the builtin filter function that works for dictionaries.

    :param f: A function that takes a key and value and returns a boolean.
    :type f: function
    :param d: The dictionary to filter.
    :type d: dict
    :return: A dictionary filtered according to the specified filter function.
    :rtype: dict
    '''
    return dict((k, v) for k, v in d.iteritems() if f(k, v))


def dmap(f, d):
    '''
    An equivalent of the builtin map function that works for dictionaries.

    :param f: A function that takes a key and value and returns a key and value.
    :type f: function
    :param d: The dictionary to map.
    :type d: dict
    :return: A dictionary where values have been mapped by the function.
    :rtype: dict
    '''
    return dict(f(k, v) for k, v in d.iteritems())


def dmerge(x, y):
    '''
    Deep merges dictionary ``y`` into dictionary ``x``.

    If a key from ``y`` exists in ``x``, the value of ``y`` is used unless both
    values are dictionaries that can be merged.

    :param x: The dictionary to recursively merge into.
    :type x: dict
    :param y: The dictionary to be merged in.
    :type y: dict
    '''

    if not isinstance(x, dict) or not isinstance(y, dict):
        raise TypeError('Arguments must be dictionaries.')
    for k, v in y.iteritems():
        if isinstance(v, dict) and k in x.keys() and isinstance(x[k], dict):
            dmerge(x[k], v)
        else:
            x[k] = v
    return x
            
            
def flatten_list_of_dicts(ld, merge_key):
    '''
    Useful for django creating a single dictionary from queryset.values() 
    list of dicts.
    
    If merge key is not unique, it will be overidden. Merge key will remain 
    within original dict. Raises KeyError if merge_key not present in all dicts
    
    :param ld: List of dictionaries to merge
    :type ld: list of dict
    :param merge_key: Key which must be present in all dicts
    :type merge_key: object
    '''
    #py2.7+ use: return {d[merge_key] : d for d in ld}
    return dict(((d[merge_key], d) for d in ld))


# XXX: Deprecated: Badly engineered - just use dfilter() above!
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
    if keep and remove:
        raise ValueError('Cannot keep and remove at the same time!')
    if keep:
        f = lambda k, v: k in keep
    elif remove:
        f = lambda k, v: k not in remove
    else:
        return d
    return dfilter(f, d)


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
