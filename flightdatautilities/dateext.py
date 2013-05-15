# -*- coding: utf-8 -*-
##############################################################################

'''
Flight Data Utilities: Date Extensions
'''

##############################################################################
# Imports


import operator

from datetime import date, datetime, time, timedelta


##############################################################################
# Exports


__all__ = ['range']


##############################################################################
# Functions


def range(start, stop, step=1, field='days'):
    '''
    Generates a list of date and times between the two provided dates.

    :param start: the date (and time) at the start of the range.
    :type start: datetime.date or datetime.datetime
    :param stop: the date (and time) at the end of the range.
    :type stop: datetime.date or datetime.datetime
    :param step: the step size
    :type step: integer
    :param field: the field to use when adding time with each step
    :type field: string
    :returns: a range of dates
    :rtype: list
    '''

    if not isinstance(step, int):
        raise TypeError('range() integer step argument expected, got %s.' % type(step).__name__)

    if step == 0:
        raise ValueError('range() step argument must not be zero')

    if field not in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
        raise ValueError('range() field argument must be acceptable by timedelta().')

    if start > stop and step > 0 or start < stop and step < 0:
        return []

    if isinstance(start, datetime):
        current = start
        convert = False
    elif isinstance(start, date):
        current = datetime.combine(start, time())
        convert = True  # Convert back to datetime.date() at the end.
    else:
        raise ValueError('range() start argument must be date or datetime')

    if isinstance(stop, datetime):
        limit = stop
    elif isinstance(stop, date):
        limit = datetime.combine(stop, time())
    else:
        raise ValueError('range() stop argument must be date or datetime')

    increment = timedelta(**{field: step})
    compare = operator.lt if step > 0 else operator.gt

    dates = []

    while compare(current, limit):
        if not convert:
            dates.append(current)
        elif len(dates) == 0 or dates[-1] != current.date():
            dates.append(current.date())
        current += increment

    return dates


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
