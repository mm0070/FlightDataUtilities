##############################################################################

'''
Flight Data Utilities: Iter Extensions
'''

##############################################################################
# Imports


import itertools
import operator


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
    a, b = itertools.tee(itertools.count(start, step))
    next(b, None)
    last = None
    for x in itertools.takewhile(lambda z: z[1] < stop, zip(a, b)):
        last = x[1]
        yield x
    if last is not None:
        yield (last, stop)


def droplast(n, iterable):
    '''
    Drops the last n items from the provided iterable.

    Based on rejected examples in http://bugs.python.org/issue16774
    '''
    t1, t2 = itertools.tee(iterable)
    return map(operator.itemgetter(0), zip(t1, itertools.islice(t2, n, None)))


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
    return output(
        (k, nested_groupby(v, function_list[1:], manipulate, output))
        for k, v in itertools.groupby(iterable, function_list[0])
    )
