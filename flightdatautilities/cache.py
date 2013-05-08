# -*- coding: utf-8 -*-
###############################################################################

'''
Flight Data Utilities: Cache
'''

###############################################################################
# Imports


try:
    import django.db.models
except ImportError:
    pass

from datetime import datetime, timedelta
from decorator import decorator


###############################################################################
# Exports


__all__ = ['memoize']


###############################################################################
# Functions


def memoize(*args, **kwargs):
    '''
    '''
    # Check whether the decorator has been invoked:
    invoked = bool(not args or kwargs)
    if not invoked:
        obj = args[0]

    # Lookup options provided to the decorator:
    timeout = kwargs.get('timeout', 300)

    def memoizer(obj):
        '''
        '''
        # Make the cache accessible to the outside world:
        obj.__cache = {}

        def wrapper(obj, *args, **kwargs):
            '''
            '''
            now = datetime.now()
            key = args

            # Improve caching support for Django models:
            try:
                if isinstance(key[0], django.db.models.Model):
                    key = (key[0].pk,) + key[1:]
            except NameError:
                pass  # Skip if we didn't have Django :)

            # Clear any stale items from the cache:
            obj.__cache = {k: v \
                    for k, v in obj.__cache.iteritems() \
                    if v['timeout'] >= now}

            item = obj.__cache.get(key)

            # Fetch the value for the cache if it is missing from the cache or
            # the entry in the cache has expired:
            if not item:
                obj.__cache[key] = {
                    'timeout': now + timedelta(seconds=timeout),
                    'value': obj(*args, **kwargs),
                }

            # Return the value from the cache:
            return obj.__cache[key]['value']

        return decorator(wrapper)(obj)

    # Return the decorated function (invoking if required):
    return memoizer if invoked else memoizer(obj)


###############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
