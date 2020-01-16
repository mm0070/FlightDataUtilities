import types

from flightdatautilities.dict_helpers import dcompact


class Struct(dict):
    '''
    A recursive class for building and representing objects with.

    Can be accessed as a dictionary or using attributes, and non-existing
    attributes can be assigned to without creating a structure for that
    attribute manually.

    Note: Checking for attribute existence with ``hasattr(x, 'a')`` is broken.
          Use ``'a' in x``.
    '''

    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def __init__(self, d={}, **kwargs):
        '''
        Initialises the structure.

        :param d: A dictionary to convert into a structure.
        :type d: dict
        :param kwargs: Keyword arguments for populating the structure.
        :type kwargs: dict
        :returns: A new structure.
        :rtype: Struct
        '''
        if isinstance(d, types.GeneratorType):
            generator = d
        else:
            d = d.copy()
            d.update(kwargs)
            generator = d.items()
        for k, v in generator:
            if type(v) == Struct:
                # Ensure that we clone structures (uses dict.copy())
                setattr(self, k, Struct(v.copy()))
            elif type(v) == dict:
                setattr(self, k, Struct(v))
            else:
                setattr(self, k, v)

    def __getattr__(self, key):
        '''
        Retrieves an attribute from the structure.

        If the structure does not have the attribute set, a new structure will
        be automatically created for that attribute.

        :param key: The key of attribute to access.
        :type key: str
        :returns: The value stored for the attribute or a new structure.
        :rtype: mixed
        '''
        try:
            # Attempt to get a value for the specified attribute key:
            return self.__getitem__(key)
        except KeyError:
            # Ensure that we do not create new structure for magic attributes:
            if key.startswith('__') and key.endswith('__'):
                raise AttributeError('\'%s\' object has no attribute \'%s\'' % (
                    self.__class__.__name__,
                    key,
                ))
            # Create new structures for unknown attributes:
            s = Struct()
            setattr(self, key, s)
            return s

    def __repr__(self):
        '''
        Returns a representation of the structure from which the structure can
        be recreated.

        :returns: A string representation of the structure.
        :rtype: str
        '''
        kv = ['%s=%s' % (k, repr(v)) for (k, v) in self.items()]
        return 'Struct(%s)' % ', '.join(kv)

    def to_dict(self):
        '''
        Recursively convert the structure to a plain dictionary.

        :returns: The structure converted to a dictionary.
        :rtype: dict
        '''
        convert = lambda v: v.to_dict() if type(v) == Struct else v
        return dcompact(dict((k, convert(v)) for k, v in self.items()))


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
