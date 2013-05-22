# -*- coding: utf-8 -*-
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

- aircraft series, engine type.
- aircraft family, engine type.
- aircraft series, engine series.
- aircraft family, engine series.
- aircraft series.
- aircraft family.

'''

##############################################################################
# Imports


import logging
import numpy as np

from abc import ABCMeta
from bisect import bisect_left

import scipy.interpolate as interp

from flightdatautilities import units


##############################################################################
# Globals


logger = logging.getLogger(__name__)


##############################################################################
# Abstract Classes


class VelocitySpeed(object):
    '''
    Provides a base implementation of a velocity speed lookup table.

    There are a number of flags that can be set to configure the table:

    - interpolate -- whether to interpolate between table values.
    - minimum_speed -- the absolute minimum speed.
    - source -- reference to the documentation or source of lookup table.
    - weight_unit -- the unit for all of the weights in the table.
    '''

    __meta__ = ABCMeta

    interpolate = False
    minimum_speed = None
    source = None
    weight_unit = 'kg'  # Can be one of 'lb', 'kg', 't' or None.

    tables = {
        'v2': {'weight': ()},
        'vref': {'weight': ()},
    }

    @property
    def v2_settings(self):
        '''
        Provides a list of available flap/conf settings for V2.

        :returns: a list of flap/conf settings.
        :rtype: list
        '''
        settings = self.tables['v2'].keys()
        if 'weight' in settings:
            settings.remove('weight')
        return sorted(settings)

    @property
    def vref_settings(self):
        '''
        Provides a list of available flap/conf settings for Vref.

        :returns: a list of flap/conf settings.
        :rtype: list
        '''
        settings = self.tables['vref'].keys()
        if 'weight' in settings:
            settings.remove('weight')
        return sorted(settings)

    def v2(self, setting, weight=None):
        '''
        Look up a value for V2.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: V2 value or None.
        :rtype: float
        :raises: KeyError -- when table or flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._get_velocity_speed(self.tables['v2'], setting, weight)

    def vref(self, setting, weight=None):
        '''
        Look up a value for Vref.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: Vref value or None.
        :rtype: float
        :raises: KeyError -- when table or flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._get_velocity_speed(self.tables['vref'], setting, weight)

    def _get_velocity_speed(self, lookup, setting, weight=None):
        '''
        Looks up the velocity speed in the provided lookup table.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param lookup: The velocity speed lookup table.
        :type lookup: dict
        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: A velocity speed value or None.
        :rtype: float
        :raises: KeyError -- when flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        if setting not in lookup:
            msg = "Velocity speed table '%s' has no entry for flap/conf '%s'."
            arg = (self.__class__.__name__, setting)
            logger.error(msg, *arg)
            raise KeyError(msg % arg)

        # If table which doesn't have weights return fixed value:
        if self.weight_unit is None:
            return lookup[setting]

        # Convert the aircraft weight to match the lookup table:
        weight = units.convert(weight, 'kg', self.weight_unit)

        wt = lookup['weight']
        if not min(wt) <= weight <= max(wt) or weight is np.ma.masked:
            msg = "Weight '%s' outside of range for velocity speed table '%s'."
            arg = (weight, self.__class__.__name__)
            logger.warning(msg, *arg)
            return None

        # Determine the value for the velocity speed:
        if self.interpolate:
            f = interp.interp1d(lookup['weight'], lookup[setting])
            value = f(weight)
        else:
            index = bisect_left(lookup['weight'], weight)
            value = lookup[setting][index]

        # Return a minimum speed if we have one and the value is below it:
        if self.minimum_speed is not None and value < self.minimum_speed:
            return self.minimum_speed

        return value


##############################################################################
# Velocity Speed Table Classes


# TODO: Review and update source name.
class B737_300(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-300.
    '''
    interpolate = True
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65),
                   1: (124, 131, 138, 145, 153, 160, 168),
                   5: (119, 126, 132, 139, 146, 153, 160),
                  15: (113, 120, 126, 132, 139, 145, 152),
        },
        'vref': {
            'weight': ( 32,  36,  40,  44,  48,  52,  56,  60,  64),
                  15: (111, 118, 125, 132, 138, 143, 149, 154, 159),
                  30: (105, 111, 117, 123, 129, 135, 140, 144, 149),
                  40: (101, 108, 114, 120, 125, 130, 135, 140, 145),
        },
    }


# TODO: Review and update source name.
class B737_400(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-400.
    '''
    interpolate = True
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 40,  45,  50,  55,  60,  65,  70),
                   5: (130, 136, 143, 149, 155, 162, 168),
        },
        'vref': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65,  70,  70),
                  15: (123, 132, 141, 149, 156, 164, 171, 177, 177),
                  30: (111, 119, 127, 134, 141, 147, 154, 159, 159),
                  40: (109, 116, 124, 130, 137, 143, 149, 155, 155),
        },
    }


# TODO: Review and update source name.
class B737_500(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-500.
    '''
    interpolate = True
    minimum_speed = 109
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 30,  35,  40,  45,  50,  55,  60,  65),
                   5: (112, 119, 126, 133, 139, 146, 152, 157),
                  15: (107, 113, 120, 126, 132, 138, 143, 146),
        },
        'vref': {
            'weight': ( 36,  40,  44,  48,  52,  56,  60),
                  15: (118, 125, 132, 137, 143, 149, 153),
                  30: (111, 117, 125, 130, 134, 140, 144),
                  40: (108, 114, 121, 126, 130, 135, 140),
        },
    }


# TODO: Review and update source name.
class B737_700(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-700.

    Note: This table is available but should never be needed as the Boeing B737
    NG family of aircraft record the V2 and VREF parameters in the data frame.
    '''
    interpolate = True
    minimum_speed = 110
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 40,  45,  49,  54,  58,  63,  68,  72),
                   1: (114, 120, 126, 132, 137, 142, 147, 152),
                   5: (111, 117, 123, 129, 134, 139, 144, 148),
                  15: (107, 113, 117, 122, 127, 131, 135, 138),
        },
        'vref': {
            'weight': ( 40,  45,  49,  54,  58,  63,  68,  72,  77),
                  15: (115, 121, 127, 133, 139, 145, 150, 155, 159),
                  30: (111, 117, 123, 129, 134, 140, 144, 149, 153),
                  40: (108, 114, 120, 126, 132, 137, 142, 147, 151),
        },
    }


class B737_700_CFM56_7B(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-700.

    Note: This table is available but should never be needed as the Boeing B737
    NG family of aircraft record the V2 and VREF parameters in the data frame.
    '''
    interpolate = True
    minimum_speed = 110
    source = 'FDS Customer 105: 737 FCOM'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000),
                   1: (  114,    120,    126,    131,    137,    142,    147,    151),
                   5: (  111,    117,    123,    129,    134,    139,    144,    148),
                  10: (  109,    114,    119,    124,    128,    133,    137,    140),
                  15: (  107,    112,    117,    122,    126,    130,    134,   None),
                  25: (  106,    111,    116,    120,    125,    129,    133,   None),
        },
        'vref': {
            'weight': (90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000),
                  15: (  115,    121,    127,    133,    139,    145,    150,    155,    159,    164),
                  30: (  111,    117,    123,    129,    134,    140,    144,    149,    153,    158),
                  40: (  108,    114,    120,    126,    132,    137,    142,    147,    151,    156),
        },
    }


# TODO: Review and update source name.
class B737_800(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-800.

    Note: This table is available but should never be needed as the Boeing B737
    NG family of aircraft record the V2 and VREF parameters in the data frame.
    '''
    interpolate = True
    minimum_speed = 110
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 41,  45,  50,  54,  59,  63,  68,  73,  77,  82),
                   1: (167, 164, 160, 156, 151, 147, 142, 137, 131, 126),
                   5: (161, 158, 154, 150, 146, 141, 137, 132, 127, 121),
                  15: (156, 153, 149, 145, 141, 137, 133, 128, 123, 118),
        },
        'vref': {
            'weight': ( 41,  45,  50,  54,  59,  63,  68,  73,  77,  82),
                  15: (174, 169, 164, 159, 154, 148, 142, 135, 129, 122),
                  30: (165, 160, 156, 151, 146, 141, 135, 129, 123, 116),
                  40: (157, 153, 148, 144, 139, 133, 128, 122, 116, 109),
        }
    }


class B757_200_RB211_535C_37(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B757-200 with Rolls Royce
    RB211-535C-37 engines.
    '''
    interpolate = True
    source = 'FDS Customer 20: Support Ticket 243; 757 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 70,  80,  90, 100, 110),
                  1 : (141, 151, 160, 169, 179),
                  5 : (129, 139, 147, 156, 165),
                 15 : (124, 132, 139, 147, 155),
                 20 : (114, 124, 133, 141, 148),
        },
        'vref': {
            'weight': ( 60,  70,  80,  90, 100, 110, 120),
                  20: (116, 125, 135, 143, 151, 159, 167),
                  25: (108, 117, 126, 134, 142, 151, 158),
                  30: (106, 115, 124, 132, 140, 149, 157),
        },
    }


class B757_200_RB211_535E4_37(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B757-200 with Rolls Royce
    RB211-535E4 engines.
    '''
    interpolate = True
    source = 'FDS Customer 109: 757 FCOM/FPPM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 70,  80,  90, 100, 110, 120),
                   1: (138, 150, 160, 169, 177, 186),
                   5: (130, 139, 147, 155, 163, 171),
                  15: (123, 131, 139, 147, 154, 161),
                  20: (117, 125, 132, 140, 147, 154),
        },
        'vref': {
            'weight': ( 60,  70,  80,  90, 100, 110, 120),
                  20: (116, 125, 135, 143, 151, 159, 167),
                  25: (108, 117, 126, 134, 142, 151, 158),
                  30: (106, 115, 124, 132, 140, 149, 157),
        },
    }
B757_200_RB211_535E4_B_37 = B757_200_RB211_535E4_37
B757_200_RB211_535E4_C_37 = B757_200_RB211_535E4_37


class B767(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B767.
    '''
    interpolate = True
    source = 'FDS Customer 20: 767 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                   5: (127, 134, 139, 145, 151, 156, 161, 166, 171, 176),
                  15: (122, 128, 134, 139, 144, 149, 154, 159, 164, 168),
                  20: (118, 124, 129, 134, 140, 144, 149, 154, 159, 164),
        },
        'vref': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                  20: (128, 135, 141, 146, 151, 157, 162, 168, 173, 179),
                  25: (123, 129, 135, 141, 146, 151, 156, 161, 166, 170),
                  30: (119, 125, 131, 137, 142, 148, 156, 164, 171, 179),
        },
    }


class B767_200_CF6_80A(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B767-200 w/ GE CF6-80A.
    '''
    interpolate = True
    source = 'FDS Customer 78'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000),
                   1: (   135,    140,    145,    150,    155,    160,    164,    169),
                   5: (   130,    135,    140,    144,    149,    154,    158,    162),
                  15: (   123,    128,    133,    138,    142,    146,    151,   None),
                  20: (   120,    125,    129,    134,    138,    143,    148,   None),
        },
        'vref': {
            'weight': (220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000),
                  20: (   129,    135,    141,    146,    151,    156,    161,    165),
                  25: (   126,    132,    137,    142,    147,    152,    157,    161),
                  30: (   122,    127,    133,    138,    143,    147,    152,    156),
        },
    }


class B767_300_CF6_80C2(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B767-300 w/ GE CF6-80C2.
    '''
    interpolate = True
    source = 'FDS Customers 20, 78 & 109: 767 FCOM/FPPM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                   5: (128, 134, 140, 145, 151, 156, 161, 166, 171, 175),
                  15: (122, 128, 134, 139, 144, 150, 154, 159, 164, 168),
                  20: (118, 124, 129, 134, 139, 145, 149, 154, 159, 165),
        },
        'vref': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                  20: (128, 135, 141, 146, 151, 157, 162, 168, 173, 179),
                  25: (123, 129, 135, 141, 146, 151, 156, 161, 166, 170),
                  30: (119, 125, 131, 137, 142, 148, 156, 164, 171, 179),
        },
    }


class B767_300_PW4000_94(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B767-300 w/ P&W 4000-94.
    '''
    interpolate = True
    source = 'FDS Customer 78'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                   5: (121, 127, 134, 140, 145, 151, 156, 161, 166, 171, 175),
                  15: (116, 122, 128, 134, 139, 144, 149, 154, 159, 164, 168),
                  20: (112, 118, 124, 129, 135, 140, 144, 149, 154, 160, 165),
        },
        'vref': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                  20: (128, 134, 140, 146, 152, 157, 162, 168, 174, 179),
                  25: (123, 129, 135, 140, 146, 151, 156, 161, 166, 170),
                  30: (119, 125, 131, 137, 142, 148, 156, 164, 171, 179),
        },
    }


# TODO: Review and update source name.
class F28_0070(VelocitySpeed):
    '''
    Velocity speed tables for Fokker F28-0070 (Fokker 70).
    '''
    interpolate = True
    source = ''
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 26,  28,  30,  32,  34,  36,  38,  40,  42),
                   0: (117, 119, 123, 127, 131, 135, 139, 143, 146),
                   8: (114, 115, 118, 122, 126, 129, 133, 135, 139),
                  15: (112, 113, 115, 117, 120, 124, 127, 131, 134),
        },
        'vref': {
            'weight': ( 26,  28,  30,  32,  34,  36,  38,  40,  42),
                   0: (124, 129, 133, 137, 142, 146, 150, 154, 157),
                  25: (113, 117, 121, 125, 129, 133, 137, 140, 143),
                  42: (104, 108, 112, 115, 119, 122, 126, 129, 132),
        },
    }


class Beechcraft_1900D(VelocitySpeed):
    '''
    Velocity speed tables for Beechcraft 1900D.
    '''
    source = 'FDS Customer 121'
    weight_unit = None  # Table only contains fixed values.
    tables = {
        # Note: Mid-range for temperatures +20°C to +40°C, S>L> to 6000ft PA.
        #       Lowest V2 = 103 kts @ 10000ft PA, 14000 lb, 30°C
        #       Highest V2 = 123 kts @ flap 0, MAUW 17120 lb, n/a °C
        'v2': {0: 125, 17.5: 114},
        # Note: Mid-range for temperatures +20°C to +40°C, S>L> to 6000ft PA.
        #       Lowest VREF = 93 kts
        #       Highest VREF = 115 kts @ MLW 16000 lb
        'vref': {35: 97},
    }


##############################################################################
# Constants


# TODO: Determine a better way of looking up which table should be used!
VELOCITY_SPEED_MAP = {
    # Boeing
    ('B737-300', None): B737_300,
    ('B737-300(QC)', None): B737_300,
    ('B737-400', None): B737_400,
    ('B737-500', None): B737_500,
    ('B737-700', None): B737_700,
    ('B737-700', 'CFM56-7B'): B737_700_CFM56_7B,
    ('B737-800', None): B737_800,

    ('B757-200', 'RB211-535C-37'): B757_200_RB211_535C_37,
    ('B757-200', 'RB211-535E4-37'): B757_200_RB211_535E4_37,
    ('B757-200', 'RB211-535E4-B-37'): B757_200_RB211_535E4_B_37,
    ('B757-200', 'RB211-535E4-C-37'): B757_200_RB211_535E4_C_37,
    ('B757-200(F)', 'RB211-535C-37'): B757_200_RB211_535C_37,
    ('B757-200(PCF)', 'RB211-535E4-37'): B757_200_RB211_535E4_37,
    ('B757-200(PCF)', 'RB211-535E4-B-37'): B757_200_RB211_535E4_B_37,
    ('B757-200(PCF)', 'RB211-535E4-C-37'): B757_200_RB211_535E4_C_37,

    ('B767', None): B767,
    ('B767-200', 'CF6-80A'): B767_200_CF6_80A,
    ('B767-200(F)', 'CF6-80A'): B767_200_CF6_80A,
    ('B767-200(ER)', 'CF6-80A'): B767_200_CF6_80A,
    ('B767-200(ER/F)', 'CF6-80A'): B767_200_CF6_80A,
    ('B767-300', 'CF6-80C2'): B767_300_CF6_80C2,
    ('B767-300(ER)', 'CF6-80C2'): B767_300_CF6_80C2,
    ('B767-300F(ER)', 'CF6-80C2'): B767_300_CF6_80C2,
    ('B767-300(ER/F)', 'CF6-80C2'): B767_300_CF6_80C2,
    ('B767-300', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300(ER)', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300F(ER)', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300(ER/F)', 'PW4000-94'): B767_300_PW4000_94,

    # Fokker
    ('F28-0070', None): F28_0070,

    # Beechcraft
    ('1900D', None): Beechcraft_1900D,
}


##############################################################################
# Functions


def get_vspeed_map(series=None, family=None, engine_series=None, engine_type=None):
    '''
    Accessor for fetching velocity speed table classes.

    :param series: An aircraft series e.g. B737-300
    :type series: string
    :param family: An aircraft family e.g. B737
    :type family: string
    :param engine_series: An engine series e.g. CF6-80C2
    :type engine_series: string
    :returns: associated VelocitySpeed class
    :rtype: VelocitySpeed
    :raises: KeyError -- if no velocity speed mapping found.
    '''
    lookup_combinations = ((series, engine_type),
                           (family, engine_type),
                           (series, engine_series),
                           (family, engine_series),
                           (series, None),
                           (family, None))

    for combination in lookup_combinations:
        if combination in VELOCITY_SPEED_MAP:
            return VELOCITY_SPEED_MAP[combination]

    msg = "No velocity speed table mapping for series '%s' or family '%s'."
    raise KeyError(msg % (series, family))


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
