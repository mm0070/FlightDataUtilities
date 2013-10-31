# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Utilities for looking up velocity speeds for various aircraft.

Note that we do not take every factor into account when selecting a value from
the lookup tables as we cannot always determine suitable values for some of the
parameters (temperature, altitude, runway slope, tailwind, etc.) nor presume to
guess what value was chosen for a particular flight.

It is necessary to ensure that flap/conf values reflect those held for the
aircraft family or series in the model information module.

When deciding on the table to select, we use the following order of precedence:

- aircraft model, engine type.
- aircraft series, engine type.
- aircraft family, engine type.
- aircraft model, engine series.
- aircraft series, engine series.
- aircraft family, engine series.
- aircraft model.
- aircraft series.
- aircraft family.

'''

##############################################################################
# Imports


from flightdatautilities.aircrafttables.interfaces import VelocitySpeed


##############################################################################
# Velocity Speed Table Classes


class B737_300(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-300 w/ CFM56-3 20K engines.
    '''
    interpolate = True
    source = 'FDS Customer 109: 737 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65),
                 '1': (122, 130, 137, 145, 152, 160, 166),
                 '5': (118, 125, 132, 139, 146, 153, 159),
                '15': (113, 119, 126, 132, 139, 145, 152),
        },
        'vref': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65),
                '15': (119, 128, 136, 144, 151, 158, 165),
                '30': (111, 119, 127, 134, 141, 147, 154),
                '40': (107, 115, 123, 131, 138, 146, 153),
        },
    }


##############################################################################
# Constants

# The format for the following mappings should match the following:
#
#   {
#       ('name', 'engine'): class,
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:    model, series or family name of the aircraft. (string)
#   - engine:  series or type of the engine if available. (string or None)
#   - class:   a class implementing VelocitySpeed.


VSPEED_MODEL_MAP = {}


VSPEED_SERIES_MAP = {
    # Boeing
    ('B737-300', None): B737_300,
    ('B737-300', 'CFM56-3'): B737_300,
}


VSPEED_FAMILY_MAP = {}
