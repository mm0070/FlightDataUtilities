# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Flight Data Utilities: Iter Extensions
'''

##############################################################################
# Imports


import numpy as np

from builtins import map, zip
from itertools import chain, count, groupby, islice, takewhile, tee
from operator import itemgetter

from flightdatautilities.array.buffer import chunk
from flightdatautilities.type import as_dtype, byte_size, is_array, is_data


##############################################################################
# Exports


__all__ = ['batch', 'droplast', 'iter_islast', 'nested_groupby']


##############################################################################
# Functions


def batch(start, stop, step):
    '''
    A generator that yields batches between the start and stop values provided.

    :param start: a start index
    :type start: int
    :param stop: a stop index
    :type stop: int
    :param step: an integer step
    :type step: int
    '''
    if stop - start <= step:
        yield (start, stop)
        return
    a, b = tee(count(start, step))
    next(b, None)
    last = None
    for x in takewhile(lambda z: z[1] < stop, zip(a, b)):
        last = x[1]
        yield x
    if last is not None:
        yield (last, stop)


def droplast(n, iterable):
    '''
    Drops the last n items from the provided iterable.

    Based on rejected examples in http://bugs.python.org/issue16774
    '''
    t1, t2 = tee(iterable)
    return map(itemgetter(0), zip(t1, islice(t2, n, None)))


def join(chunks, dtype=None):
    '''
    Join chunks of the same type of data together.

    :param chunks: Chunks of data to join together.
    :type chunks: iterable of str or array
    :param dtype: dtype of data within chunks when
    :type dtype: np.dtype or None
    :returns: Chunks of data joined into a single object.
    :rtype: str or np.ndarray
    '''
    memviews = tuple(memoryview(c) for c in iter_data(chunks))
    if memviews:
        joined = np.concatenate(memviews)
        if dtype:
            return joined.astype(dtype, copy=False)
        elif is_array(chunks[0]):
            return joined
        else:
            return joined.tostring()
        #return as_dtype(joined, dtype, cast=True) if dtype else joined
    else:
        return np.empty(0, dtype=dtype) if dtype else b''


def nested_groupby(iterable, function_list, manipulate=None, output=list):
    '''
    Performs multi-level grouping on a list of data items.

    :param iterable: An iterable object to group items within.
    :type iterable: iterable
    :param function_list: A list of functions for grouping.
    :type function_list: list of functions
    :param manipulate: An optional manipulation function to modify groups.
    :type manipulate: function
    :param output: A type to convert the nested structure to, e.g. OrderedDict.
    :type output: type
    :returns: A list of multi-level grouped data items.
    :rtype: list
    '''
    if not len(function_list):
        return manipulate(iterable) if manipulate else list(iterable)
    return output((k, nested_groupby(v, function_list[1:], manipulate, output))
                  for k, v in groupby(iterable, function_list[0]))


def iter_data(data_gen):
    '''
    Iterate over an iterable and yield only data.

    :type data_gen: iterable
    :rtype: iterable
    '''
    return (d for d in data_gen if is_data(d))


def iter_data_start_idx(data_gen, start, count=None, byte=False, dtype=None):
    '''
    Start a generator at a index into the data it is yielding.

    :type data_gen: generator
    :type start: int
    :rtype: generator
    '''
    if start == 0:
        return chunk(data_gen, count, flush=True, dtype=dtype) if count else data_gen

    size = byte_size if byte else len
    pos = 0
    for data in data_gen:
        if not is_data(data):
            continue
        next_pos = pos + size(data)
        if next_pos == start:
            break
        elif next_pos > start:
            dtype = getattr(data, 'dtype', None)
            itemsize = 1 if dtype is None else dtype.itemsize
            convert = byte and itemsize != 1
            if convert:
                # since data may be split at an arbitrary byte location within a chunk, we can't
                # automatically cast data back to the original dtype as it may not be at an
                # itemsize boundary
                data = data.view(np.uint8)

            data = data[start - pos:]

            if convert:
                if len(data) % itemsize:
                    if not count:
                        raise ValueError('invalid chunk remainder size %d for dtype %s conversion in generator_data_start' %
                                         (len(data), itemsize))
                    data_gen = iter_dtype(data_gen, np.uint8)
                else:
                    data = data.view(dtype)
                    convert = False

            start_gen = chain([data], data_gen)

            if count:
                start_gen = chunk(start_gen, (count * itemsize) if convert else count, flush=True, dtype=dtype)

            if convert:  # convert back into original dtype
                start_gen = iter_dtype(start_gen, dtype, skip_incompatible=True)

            return start_gen
        pos = next_pos
    return data_gen


def iter_data_stop_idx(data_gen, stop, byte=False):
    '''
    Stop a generator at an index into the data it is yielding.

    :type data_gen: generator
    :type stop: int
    :yields: data from data_gen until stop
    '''
    if stop == 0:
        return
    size = byte_size if byte else len
    pos = 0
    for data in data_gen:
        if not is_data(data):
            yield data
        next_pos = pos + size(data)
        if next_pos > stop:
            if byte:
                dtype = getattr(data, 'dtype', None)
                itemsize = 1 if dtype is None else dtype.itemsize
                convert = itemsize != 1
            else:
                convert = False

            if convert:
                data = data.view(np.uint8)

            data = data[:stop - pos]

            if convert:
                data = data[:len(data) // itemsize * itemsize].view(dtype)
            yield data
            return
        yield data
        if next_pos == stop:
            return
        pos = next_pos


def iter_dtype(data_gen, dtype=None, copy=False, cast=False, skip_incompatible=False):
    '''
    Iterate over an iterable while converting to dtype.

    :type data_gen: iterable
    :type skip_incompatible: bool
    :rtype: iterable
    '''
    for data in data_gen:
        try:
            yield as_dtype(data, dtype, copy=copy, cast=cast)
        except ValueError:
            if skip_incompatible:
                continue
            else:
                raise


def iter_islast(iterable):
    '''
    Based on http://code.activestate.com/recipes/392015-finding-the-last-item-in-a-loop/
    '''
    it = iter(iterable)
    prev = next(it)
    for item in it:
        yield prev, False
        prev = item
    yield prev, True


def tolist(array):
    '''
    '''
    return [a.tolist() if hasattr(a, 'tolist') else tolist(a) for a in array]


def is_empty(iterable):
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return iterable, True
    else:
        return chain([first], it), False

