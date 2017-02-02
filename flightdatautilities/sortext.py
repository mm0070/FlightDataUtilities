# -*- coding: utf-8 -*-
##############################################################################

'''
Flight Data Utilities: Sort Extensions
'''

# TODO: New sort function to strip common leading words, e.g. 'a', 'the', ...
# TODO: Amend sort functions to strip accents/diacritics to for i18n support.
# TODO: Complete sort functions to fully support floating point numbers.
# TODO: Create vsorted() to sort version strings, i.e. 1.5 > 0.7

##############################################################################
# Imports


import re


##############################################################################
# Exports


__all__ = ['nsorted']


##############################################################################
# Functions


def nsorted(iterable, key=None, reverse=False):
    '''
    A natural version of ``sorted`` that takes numeric ordering into account.

    **Note**: Removes space characters from the sort key.

    :param iterable: Returns a new sorted list from the items in iterable.
    :type iterable: iterable
    :param key:
    :type key: function
    :param reverse:
    :type reverse: boolean
    :returns: List of items in iterable sorted naturally.
    :rtype: iterable
    '''
    z = re.compile('(\d+(?:\.\d+)*)')
    c = lambda t: float(t) if t.isdigit() else t
    if not key:
        key = lambda x: x
    wrapper = lambda x: list(map(c, z.split(str(key(x)).replace(' ', ''))))
    return sorted(iterable, key=wrapper, reverse=reverse)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
