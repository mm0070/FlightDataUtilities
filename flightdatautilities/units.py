# -*- coding: utf-8 -*-
##############################################################################

'''
Provides utilities for handling conversions between units of flight data.
'''

# FIXME: Default unit change - 'dots' should be 'dot'?
# FIXME: Default unit change - 'mB' should be 'mbar' or 'mb'?

##############################################################################
# Constants


CONVERSION_MULTIPLIERS = {
    # Flow (Volume):
    'lb/h': {
        'kg/h': 0.45359237,
        't/h': 0.00045359237,
    },
    'kg/h': {
        'lb/h': 2.204622622,
        't/h': 0.001,
    },
    't/h': {
        'lb/h': 2204.622621849,
        'kg/h': 1000.0,
    },
    # Frequency:
    'KHz': {
        'MHz': 0.001,
        'GHz': 0.000001,
    },
    'MHz': {
        'KHz': 1000.0,
        'GHz': 0.001,
    },
    'GHz': {
        'KHz': 1000000.0,
        'MHz': 1000.0,
    },
    # Length:
    'ft': {
        'm': 0.3048,
        'km': 0.0003048,
        'mi': 0.00018939,
        'nm': 0.000164579,
    },
    'm': {
        'ft': 3.280839895,
        'km': 0.001,
        'mi': 0.000621371,
        'nm': 0.000539957,
    },
    'km': {
        'ft': 3280.839895013,
        'm': 1000.0,
        'mi': 0.621371192,
        'nm': 0.539956803,
    },
    'mi': {
        'ft': 5280.0,
        'm': 1609.344,
        'km': 1.609344,
        'nm': 0.868976242,
    },
    'nm': {
        'ft': 6076.11548554,
        'm': 1852.0,
        'km': 1.852,
        'mi': 1.150779448,
    },
    # Mass:
    'lb': {
        'kg': 0.45359237,
        't': 0.00045359237,
    },
    'kg': {
        'lb': 2.204622622,
        't': 0.001,
    },
    't': {
        'lb': 2204.622621849,
        'kg': 1000.0,
    },
    # Pressure:
    'inHg': {
        'mB': 33.86389,
        'psi': 0.491154221,
    },
    'mB': {
        'inHg': 0.02952998,
        'psi': 0.014503774,
    },
    'psi': {
        'inHg': 2.036020375,
        'mB': 68.94757,
    },
    # Speed:
    'kt': {
        'mph': 0.514444 / 0.44704,
        'fpm': 0.514444 / 0.00508,
    },
    'mph': {
        'kt': 0.44704 / 0.514444,
        'fpm': 0.44704 / 0.00508,
    },
    'fpm': {
        'kt': 0.00508 / 0.514444,
        'mph': 0.00508 / 0.44704,
    },
    # Time:
    'h': {
        'min': 60.0,
        's': 3600.0,
    },
    'min': {
        'h': 0.016666667,
        's': 60.0,
    },
    's': {
        'h': 0.000277778,
        'min': 0.016666667,
    },
    # Other:
    'gs-ddm': {
        'dots': 11.428571428571429,
    },
    'loc-ddm': {
        'dots': 12.903225806451614,
    },
    'mV': {
        'dots': 0.01333333333333333,
    },
    'dots': {
        'gs-ddm': 0.0875,
        'loc-ddm': 0.0775,
        'mV': 75,
    }
}


CONVERSION_FUNCTIONS = {
    # Temperature:
    u'°C': {
        u'°F': lambda v: v * 9.0 / 5.0 + 32.0,
        u'°K': lambda v: v + 273.15,
    },
    u'°F': {
        u'°C': lambda v: (v - 32.0) * 5.0 / 9.0,
        u'°K': lambda v: (v + 459.67) * 5.0 / 9.0,
    },
    u'°K': {
        u'°C': lambda v: v - 273.15,
        u'°F': lambda v: v * 9.0 / 5.0 - 459.67,
    },
}


STANDARD_CONVERSIONS = {
    # Flow (Volume):
    'lb/h': 'kg/h',
    't/h': 'kg/h',
    # Length:
    'mi': 'nm',
    # Mass:
    'lb': 'kg',
    't': 'kg',
    # Pressure:
    'inHg': 'mB',
    # Temperature:
    u'°F': u'°C',
    u'°K': u'°C',
    # Other:
    'gs-ddm': 'dots',
    'loc-ddm': 'dots',
    'mV': 'dots',
}


UNIT_CORRECTIONS = {
    # Flow (Volume):
    'lb/hr': 'lb/h',
    'lbs/h': 'lb/h',
    'lbs/hr': 'lb/h',
    'kg/hr': 'kg/h',
    'kgs/h': 'kg/h',
    'kgs/hr': 'kg/h',
    't/hr': 't/h',
    'ts/h': 't/h',
    'ts/hr': 't/h',
    'tonne/h': 't/h',
    'tonne/hr': 't/h',
    'tonnes/h': 't/h',
    'tonnes/hr': 't/h',
    # Length:
    'fts': 'ft',
    'feet': 'ft',
    'foot': 'ft',
    'metre': 'm',
    'metres': 'm',
    'kilometre': 'km',
    'kilometres': 'km',
    'mile': 'mi',
    'miles': 'mi',
    # Mass:
    'kgs': 'kg',
    'lbs': 'lb',
    'tonne': 't',
    'tonnes': 't',
    # Speed:
    'kts': 'kt',
    'knot': 'kt',
    'knots': 'kt',
    'mi/h': 'mph',
    'mi/hr': 'mph',
    'ft/m': 'fpm',
    'ft/min': 'fpm',
    'feet/min': 'fpm',
    # Temperature:
    'C': u'°C',
    'F': u'°F',
    'K': u'°K',
    # Time:
    'hr': 'h',
    'hrs': 'h',
    'mins': 'min',
    'sec': 's',
    'secs': 's',
    # Other:
    'dot': 'dots',
}


##############################################################################
# Functions


def normalise(unit):
    '''
    Normalises the provided unit to a well known form.

    :param unit: the unit to normalise.
    :type unit: string
    :returns: the normalised unit.
    :rtype: string
    '''
    return UNIT_CORRECTIONS.get(unit, unit)


def function(unit, output):
    '''
    Looks up the conversion function for the units provided.

    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the conversion function
    :rtype: function
    '''
    return CONVERSION_FUNCTIONS[normalise(unit)][normalise(output)]


def multiplier(unit, output):
    '''
    Looks up the conversion multiplier for the units provided.

    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the conversion multiplier
    :rtype: float
    '''
    return CONVERSION_MULTIPLIERS[normalise(unit)][normalise(output)]


def convert(value, unit, output):
    '''
    Converts a value from one unit to another.

    :param value: the value to convert.
    :type value: numeric
    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the value altered to new units
    :rtype: numeric
    :raises: ValueError -- if any of the units are not known.
    '''
    try:
        if unit in CONVERSION_FUNCTIONS:
            return function(unit, output)(value)
        if unit in CONVERSION_MULTIPLIERS:
            return value * multiplier(unit, output)
        raise ValueError('Unknown unit: %s' % unit)
    except KeyError:
        raise ValueError('Unknown output unit: %s' % output)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
