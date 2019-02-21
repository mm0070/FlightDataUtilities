# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Flight Data Utilities: Iter Extensions
'''

##############################################################################
# Imports


from builtins import map, zip
from itertools import count, groupby, islice, takewhile, tee
from operator import itemgetter


##############################################################################
# Exports


__all__ = ['batch', 'droplast', 'nested_groupby']


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
