# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Utilities for looking up velocity speeds for various aircraft.

Note that we do not take every factor into account when selecting a value from
the lookup tables as we cannot always determine suitable values for some of the
parameters (temperature, altitude, runway slope, tailwind, etc.) nor presume to
guess what value was chosen for a particular flight.

It is necessary to ensure that flap lever values reflect those held for the
aircraft family, series or model in the model information module.

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


from flightdatautilities import units as ut
from flightdatautilities.aircrafttables.interfaces import VelocitySpeed


##############################################################################
# Velocity Speed Table Classes

# Velocity speed class definitions must define the following:
#
#   - source:   documentation sources for the values in the tables. (string)
#   - tables:   a dictionary containing the lookup tables.
#
# A number of other attributes may need to be defined:
#
#   - weight_scale: a number to scale the weights by, e.g. 1000. (integer)
#   - weight_unit:  unit of the weight values, i.e. None, LB, KG, TONNE.
#   - fallback:     a dictionary containing fallback values.
#
# The standard tables may contain a number of entries:
#
#   - v2:   a dictionary of tuples of weights and speeds by flap lever detent.
#   - vref: a dictionary of tuples of weights and speeds by flap lever detent.
#   - vapp: a dictionary of tuples of weights and speeds by flap lever detent.
#   - vmo:  a table for maximum operating speed.
#   - mmo:  a table for maximum operating mach.
#
# The fallback tables may contain a number of entries:
#
#   - v2:   a dictionary of fixed speeds by flap lever detent.
#   - vref: a dictionary of fixed speeds by flap lever detent.
#   - vapp: a dictionary of fixed speeds by flap lever detent.
#
# The entry for v2/vref/vapp standard tables should match the format:
#
#   {
#       'weight': (100, 200, 300, 400, 500),
#           '25': (110, 115, 120, 125, 130),
#           '30': (105, 110, 115, 120, 125),
#   }
#
# The entry for v2/vref/vapp fallback tables should match the format:
#
#   {
#       '25': 120,
#       '30': 115,
#   }
#
# The entry for vmo/mmo may be one of the folloing:
#
#   - none:     will result in a masked, zeroed array.
#
#       {..., 'vmo': None, ...}
#
#   - fixed:    a fixed value regardless of altitude (integer/float)
#
#       {..., 'vmo': 350, ...}
#
#   - dict:     a dictionary of altitudes and speed values.
#               interpolates between values - repeat altitude value to step.
#               should propagate minimum value to sea level.
#               should propagate maximum value to maximum operating altitude.
#
#       {..., 'vmo': {
#           'altitude': (  0, 10000, 10000, 20000, 40000),
#              'speed': (350,   330,   300,   300,   300)
#       }, ...}
#


class B737_300(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-300 w/ CFM56-3 20K engines.
    '''
    source = 'FDS Customer 109; B737 FCOM'
    weight_unit = ut.TONNE
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
        'vmo': 340,
        'mmo': 0.82,
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
