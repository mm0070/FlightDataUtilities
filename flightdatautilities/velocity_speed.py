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
            # raise KeyError(msg % arg)
            return None

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


class A300_600(VelocitySpeed):
    '''
    Velocity speed tables for A300-600
    '''
    interpolate = True
    source = 'FDS Customer 6: A300 FCOM'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (200000,205000,210000,215000,220000,225000,230000,235000,240000,245000,250000,255000,260000,265000,270000,275000,280000,285000,290000,295000,300000,305000,310000,315000,320000,325000,330000,335000,340000,345000,350000,355000,360000,365000,370000,375000,380000,385000),
                   0: (   131,   133,   134,   136,   137,   139,   140,   142,   143,   145,   146,   147,   149,   150,   152,   153,   154,   155,   157,   158,   159,   160,   162,   163,   164,   165,   166,   168,   169,   170,   171,   172,   174,   175,   176,   177,   178,   179),
                  15: (   123,   124,   126,   127,   129,   130,   131,   133,   134,   135,   137,   138,   139,   140,   142,   143,   144,   145,   146,   148,   149,   150,   151,   152,   153,   154,   156,   157,   158,   159,   160,   161,   162,   163,   164,   165,   166,   167),
                  20: (   117,   119,   120,   121,   123,   124,   125,   127,   128,   129,   131,   132,   133,   134,   135,   137,   138,   139,   140,   141,   142,   143,   145,   146,   147,   148,   149,   150,   151,   152,   153,   154,   155,   156,   157,   158,   159,   160),
                  # Flap  0 / Slat 15, Taken from  V2/VS 1.27
                  # Flap 15 / Slat 15, Taken from  V2/VS 1.27
                  # Flap 20 / Slat 15, Taken from  V2/VS 1.27
        },
        'vref': {
            'weight': (177000, 205000, 220000, 235000, 250000, 265000, 280000, 295000, 310000, 325000, 340000, 355000, 370000, 385000),
                  40: (   109,    111,    115,    119,    122,    126,    129,    132,    135,    139,    142,    145,    148,    151), #Slat 30/Flap 40
        },
    }


class A300_B4(VelocitySpeed):
    '''
    Velocity speed tables for A300-B4
    '''
    interpolate = True
    source = 'FDS Customer 6: A300 FCOM'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (240000, 260000, 280000, 300000, 320000, 340000),
                   0: (   145,    150,    154,    162,    167,    171), # Slat 15/ Flap 0,  Taken from a graph table
                   8: (   130,    134,    141,    146,    148,    155), # Slat 16/ Flap 8,  Taken from a graph table
                  15: (   123,    128,    133,    137,    142,    146), # Slat 16/ Flap 15, Taken from a graph table
        },
        'vref': {
            'weight': (230000, 240000, 250000, 260000, 270000, 280000, 290000, 300000, 310000, 320000, 330000, 340000, 350000, 360000, 363600),
                  25: (   121,    124,    127,    129,    132,    135,    137,    139,    141,    143,    145,    147,    150,    152,    152), #Slat 25/Flap 25
        },
    }


class A319_100(VelocitySpeed):
    '''
    Velocity speed tables for A319_100 series
    '''
    interpolate = True
    source = 'Pending Review, Customer 125 FDIMU DAR Analysis'
    weight_unit = 't'
    ### 'Vapp' ###
    tables = {
        'vref': {
            'weight': (  40,   44,  48,  52,  56,  60,  64,  68,  72,  76),
                 '3': ( 110,  115, 120, 125, 130, 134, 139, 143, 147, 151),
              'Full': (None, None, 112, 117, 121, 125, 129, 133, 137, 141),
        },
    }


class A320(VelocitySpeed):
    '''
    Velocity speed tables for A320
    '''
    interpolate = True
    source = 'Pending Review from Customer 125'
    weight_unit = 't'
    tables = {
    ### 'Vapp' ###
        'vref': {
            'weight': ( 40,  44,  48,  52,  56,  60,  64,  68,  72,  76,  78),
                 '3': (115, 120, 125, 130, 135, 140, 144, 148, 152, 156, 158),
              'Full': (111, 116, 121, 126, 131, 135, 139, 143, 147, 151, 153),
        },
    }


class A321_200(VelocitySpeed):
    '''
    Velocity speed tables for A321_200 series
    '''
    interpolate = True
    source = 'Pending Review, Customer 125 FDIMU DAR Analysis'
    weight_unit = 't'
    ### 'Vapp' ###
    tables = {
        'vref': {
            'weight': ( 52,  54,  56,  58,  60,  62,  64,  66,  68,  70,  72,  74,  76,  78,  80,  82,  84,  86),
                 '3': (121, 123, 125, 128, 130, 132, 134, 136, 138, 140, 142, 144, 146, 148, 150, 152, 154, 156),
              'Full': (116, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 144, 146, 148, 150),
        },
    }


class A330_300(VelocitySpeed):
    '''
    Velocity speed tables for Airbus A340-300 series
    '''
    interpolate = True
    source = 'FDS Customer 125 DAR Analysis Program'
    weight_unit = 't'
    ### 'Vapp' ###
    tables = {
        'vref': {
            'weight': (120, 130, 140, 150, 160, 170, 180, 190),
                 '3': (131, 131, 131, 133, 135, 139, 143, 147),
              'Full': (131, 131, 131, 131, 132, 136, 140, 144),
        },
    }


class A340_300(VelocitySpeed):
    '''
    Velocity speed tables for Airbus A340-300 series
    '''
    interpolate = True
    source = 'FDS Customer 125 DAR Analysis Program'
    weight_unit = 't'
    ### 'Vapp' ###
    tables = {
        'vref': {
            'weight': (140, 150, 160, 170, 180, 190, 200),
                 '3': (131, 132, 135, 139, 143, 147, 150),
              'Full': (131, 131, 132, 136, 140, 144, 147),
        },
    }


class ATR42_300(VelocitySpeed):
    '''
    Velocity speed tables for ATR42-300 w/ PWC PW120 engines.
    '''
    interpolate = True
    source = 'FDS Customer 6: ATR42 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (14, 14.5, 15, 15.5,  16, 16.5, 16.7, 16.9),
                  15: (92,   94, 96,   98, 100,  102,  102,  103),
        },
        'vref': {
            'weight': (11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5),
                  30: (84,   86, 88,   90, 92,   93, 95,   97, 99,  101,102,  104),
        },
    }

    
class ATR72_200(VelocitySpeed):
    '''
    Velocity speed tables for ATR72-202 w/ PWC PW124B engines.
    '''
    interpolate = True
    source = 'FDS Customer 6: ATR72 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 13,  17,  18,  19,  20,  21, 21.5,  22),
                  15: (105, 105, 108, 111, 114, 117,  118, 120),
        },
        'vref': {
            'weight': (13, 14, 15, 16,  17,  18,  19,  20,  21, 21.5),
                  30: (87, 90, 94, 97, 100, 103, 106, 110, 113,  114),
        },
    }


class ATR72_600(VelocitySpeed):
    '''
    Velocity speed tables for ATR72-600 With PW127F & PW127M engines.
    '''
    interpolate = True
    source = 'FDS Customer 25: ATR72 QRH OPS Data'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 13,  14,  15,  16,  17,  18,  19,  20,  21, 21.5, 22, 22.5,  23),
                  15: (110, 110, 110, 110, 110, 110, 110, 110, 111,  113, 114, 115, 117),
        },
        'vref': {
            'weight': ( 13,  14,  15,  16,  17,  18,  19,  20,  21, 21.5,  22, 22.5,  23),
                   0: (115, 119, 123, 127, 131, 135, 139, 142, 146,  147, 149,  151, 152),
                  15: ( 97,  97, 100, 103, 107, 110, 113, 116, 120,  121, 123,  124, 126),
                  30: ( 95,  95,  95,  95,  96,  99, 102, 105, 108,  109, 111,  113, 115),
        },
    }


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
                   1: (122, 130, 137, 145, 152, 160, 166),
                   5: (118, 125, 132, 139, 146, 153, 159),
                  15: (113, 119, 126, 132, 139, 145, 152),
        },
        'vref': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65),
                  15: (119, 128, 136, 144, 151, 158, 165),
                  30: (111, 119, 127, 134, 141, 147, 154),
                  40: (107, 115, 123, 131, 138, 146, 153),
        },
    }


class B737_400(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-400 w/ CFMI CFM56-3_23.5K engines.
    '''
    interpolate = True
    source = 'FDS Customer 25, 28 & 52: 737 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 40,  45,  50,  55,  60,  65,  70),
                   5: (130, 136, 143, 149, 155, 162, 168),
                  15: (122, 129, 135, 141, 146, 152, 157),
        },
        'vref': {
            'weight': ( 35,  40,  45,  50,  55,  60,  65,  70),
                  15: (123, 132, 141, 149, 156, 164, 171, 177),
                  30: (111, 119, 127, 134, 141, 147, 154, 159),
                  40: (109, 116, 124, 130, 137, 143, 149, 155),
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


class B737_600(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-600.
    '''
    interpolate = True
    minimum_speed = 109
    source = 'FDS Customer 125 Analysis Program'
    weight_unit = 't'
    tables = {
        'vref': {
            'weight': ( 38,  40,  42,  44,  46,  48,  50,  52,  54,  56,  58,  60,  62,  64,  66,  68,  70),
                  15: (111, 114, 116, 119, 122, 125, 127, 130, 132, 135, 137, 140, 142, 144, 146, 148, 150),
                  30: (106, 109, 112, 115, 117, 120, 122, 125, 127, 129, 131, 134, 136, 138, 140, 142, 144),
                  40: (104, 107, 109, 112, 114, 117, 119, 122, 124, 127, 129, 131, 133, 135, 137, 139, 141),
        },
    }


class B737_700_CFM56_7B(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-700.

    Note: V2 and VREF are recorded on Boeing B737 NG aircraft.
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


class B737_700_CFM56_7B27B3(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-700BBJ w/ CFMI CFM56-7B27B3 engines.

    Note: V2 and VREF are recorded on Boeing B737 NG aircraft.
    '''
    interpolate = True
    source = 'FDS Customer 69 & 109 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 40,  44,  48,  52,  56,  60,  64,  68,  72,  76,  80,  84,  88),
                   1: (113, 118, 124, 129, 134, 138, 143, 147, 151, 155, 159, 163, 167),
                   5: (110, 115, 121, 126, 131, 135, 140, 144, 148, 151, 155, 159, 163),
                  10: (109, 114, 119, 123, 127, 131, 135, 138, 141, 144, 148, 152, 155),
                  15: (108, 112, 117, 121, 125, 129, 132, 136, 139, 142, 145, 148, 152),
                  25: (107, 111, 115, 119, 123, 127, 131, 134, 137, 140, 143, 146, None),
        },
        'vref': {
            'weight': ( 45,  50,  55,  60,  65,  70,  75,  80,  85),
                  15: (121, 127, 134, 140, 147, 152, 157, 162, 167),
                  30: (117, 123, 129, 135, 141, 146, 151, 156, 161),
                  40: (114, 120, 127, 133, 139, 144, 149, 154, 159),
        }
    }


class B737_800(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B737-800 w/ CFMI CFM56-7B engines.

    Note: V2 and VREF are recorded on Boeing B737 NG aircraft.
    '''
    interpolate = True
    source = 'FDS Customer 69 & 109: 737 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 40,  45,  50,  55,  60,  65,  70,  75,  80,  85, 90),
                   1: (125, 131, 137, 143, 148, 153, 158, 162, 167, 171, 176),
                   5: (121, 126, 132, 137, 143, 148, 152, 156, 160, 164, 167),
                  10: (119, 125, 131, 136, 141, 146, 150, 154, 158, 162, 166),
                  15: (117, 123, 128, 133, 138, 143, 147, 151, 155, 159, None),
                  25: (115, 121, 126, 131, 136, 141, 145, 149, 153, 157, None),
        },
        'vref': {
            'weight': ( 40,  45,  50,  55,  60,  65,  70,  75,  80,  85),
                  15: (121, 128, 136, 143, 149, 156, 161, 167, 172, 177),
                  30: (115, 122, 129, 136, 142, 148, 153, 158, 163, 168),
                  40: (108, 115, 122, 128, 135, 141, 146, 151, 155, 160),
        }
    }


class B747_400_CF6_80C2B1F(VelocitySpeed):
    '''
    Velocity speed tables for FCOM Boeing B747 400 CF6_80C2B1F
    '''
    interpolate = True
    source = 'FDS Customer 71 QRH'
    weight_unit = 'lb'
    tables = {
        'vref': {
            'weight': (400000, 450000, 500000, 550000, 600000, 650000, 700000, 750000, 800000,  850000, 900000),
                  25: (   126,    134,    141,    149,    156,    163,    169,    176,    182,     188,    194),
                  30: (   121,    128,    136,    143,    150,    156,    162,    169,    175,     181,    186),
        },
    }


class B747_400_PW4056(VelocitySpeed):
    '''
    Velocity speed tables for FCOM Boeing B747-400 PW4056
    '''
    interpolate = True
    source = 'FDS Customer 71 QRH'
    weight_unit = 'lb'
    tables = {
        'vref': {
            'weight': (400000, 490000, 530000, 570000, 620000, 660000, 700000, 750000, 790000,  840000, 880000),
                  25: (   132,    139,    146,    152,    158,    164,    170,    176,    181,     187,    192),
                  30: (   127,    133,    140,    146,    152,    157,    163,    168,    174,     179,    184),
        },
    }


class B757_200_RB211_535C_37(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B757-200 w/ Rolls Royce RB211-535C-37
    engines.
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
    Velocity speed tables for Boeing B757-200 w/ Rolls Royce RB211-535E4
    engines.
    '''
    interpolate = True
    source = 'FDS Customer 27, 104, 109 & 122: 757 FCOM/FPPM'
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
    source = 'FDS Customer 78 & 94 FCOM'
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
    
    Values for Vref at 90 tonnes added by extrapolation of customers' data.
    TODO: Seek verification from Boeing for these speeds.
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
            'weight': ( 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                  20: (122, 128, 135, 141, 146, 151, 157, 162, 168, 173, 179),
                  25: (117, 123, 129, 135, 141, 146, 151, 156, 161, 166, 170),
                  30: (113, 119, 125, 131, 137, 142, 148, 156, 164, 171, 179),
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


class B777_200ER(VelocitySpeed):
    '''
    Velocity speed tables for FCOM Boeing B777-200ER.
    '''
    interpolate = True
    source = 'FDS Customer 27'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300),
                   5: (123, 127, 131, 135, 138, 142, 145, 148, 151, 155, 158, 161, 164, 166, 169, 172, 175),
                  15: (119, 122, 126, 129, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 162, 165, 168),
                  20: (115, 119, 122, 126, 129, 132, 135, 138, 141, 144, 147, 150, 152, 155, 158, 160, None),
        },
        'vref': {
            'weight': (140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300),
                  20: (123, 127, 131, 135, 139, 143, 147, 150, 154, 158, 161, 164, 168, 171, 174, 177, 180),
                  25: (118, 123, 127, 131, 134, 138, 142, 145, 149, 152, 156, 159, 162, 165, 168, 171, 174),
                  30: (113, 117, 121, 124, 128, 132, 135, 139, 142, 145, 148, 151, 154, 157, 161, 164, 166),
        },
    }


class B777_F_GE90_110B1L(VelocitySpeed):
    '''
    Velocity speed tables for FCOM Boeing B777F GE90-110B1L
    '''
    interpolate = True
    source = 'FDS Customer 71'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (320000, 360000, 400000, 440000, 480000, 520000, 560000, 600000, 640000, 680000, 720000, 760000, 800000),
                   5: (   126,    133,    139,    145,    151,    156,    161,    166,    171,    176,    180,    184,    189),
                  15: (   121,    127,    133,    139,    144,    150,    155,    159,    164,    169,    173,    176,    181),
                  20: (   117,    123,    129,    135,    140,    145,    150,    155,    159,    164,    168,    172,    175),
        },
        'vref': {
            'weight': (340000, 380000, 420000, 460000, 500000, 540000, 580000, 620000, 660000, 700000, 740000, 780000),
                  20: (   137,    137,    143,    150,    156,    162,    168,    173,    179,    184,    189,    193),
                  25: (   137,    137,    137,    142,    148,    153,    159,    164,    169,    174,    179,    183),
                  30: (   137,    137,    137,    137,    140,    145,    151,    158,    164,    172,    178,    184),
        },
    }


class B787_8_Trent_1000_A(VelocitySpeed):
    '''
    Velocity speed tables for Boeing B787-8 w/ Trent 1000-A.
    '''
    interpolate = True
    source = 'FDS Customer 124'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210,  220,  230,  240),
                   5: (114, 119, 124, 129, 134, 138, 142, 146, 150, 154, 157, 161,  164,  166,  169),
                  15: (112, 115, 120, 124, 129, 133, 137, 140, 144, 148, 151, 155,  158,  160, None),
                  20: (106, 110, 115, 119, 123, 127, 131, 135, 139, 142, 146, 149, None, None, None),
        },
        'vref': {
            'weight': (120, 130, 140, 150, 160, 170),
                  25: (123, 128, 133, 137, 142, 146),
                  30: (121, 125, 130, 134, 139, 142),
        },
    }


class BAE146_100(VelocitySpeed):
    '''
    Velocity speed tables for BAe 146_100 series
    '''
    interpolate = True
    source = 'FDS Customer 5 Speed Cards table'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 26,  27,  28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38),
                  18: (112, 113, 114, 116, 118, 120, 122, 124, 126, 128, 129, 131, 133),
                  24: (104, 105, 106, 108, 110, 112, 114, 116, 117, 119, 121, 123, 124),
                  30: (102, 102, 102, 103, 104, 106, 107, 109, 111, 113, 114, 116, 117),
        },
        'vref': {
            'weight': (  26,  27,  28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38),
                   0: ( 150, 153, 156, 159, 162, 165, 167, 170, 173, 176, 178, 181, 183),
                  18: ( 120, 122, 124, 126, 128, 130, 132, 133, 135, 137, 138, 140, 142),
                  24: ( 110, 112, 114, 116, 118, 120, 122, 123, 125, 127, 128, 130, 132),
                  30: ( 104, 106, 108, 110, 112, 114, 116, 117, 119, 121, 122, 124, 126),
                  33: (  99, 101, 103, 105, 107, 109, 111, 112, 114, 116, 117, 119, 121),
        },
    }


class BAE146_200(VelocitySpeed):
    '''
    Velocity speed tables for BAe 146_200 series
    '''
    interpolate = True
    source = 'FDS Customer 5 Speed Cards table'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': ( 25,  26,  27,  28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43),
                  18: (110, 111, 113, 115, 117, 119, 121, 122, 124, 126, 128, 129, 131, 133, 134, 136, 138, 139, 141),
                  24: (102, 102, 103, 105, 107, 109, 111, 112, 114, 116, 118, 119, 121, 122, 124, 125, 127, 128, 130),
                  30: ( 97,  99,  99,  99, 101, 102, 104, 106, 107, 109, 111, 113, 114, 116, 117, 119, 121, 123, 124),
        },
        'vref': {
            'weight': ( 25,  26,  27,  28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43),
                   0: (148, 151, 153, 156, 159, 162, 165, 168, 170, 173, 175, 178, 180, 183, 185, 188, 190, 192, 195),
                  18: (118, 120, 122, 124, 126, 127, 129, 131, 133, 135, 136, 138, 140, 141, 143, 144, 146, 148, 149),
                  24: (108, 110, 112, 114, 116, 117, 119, 121, 123, 125, 126, 128, 130, 131, 133, 134, 136, 138, 139),
                  30: (102, 104, 106, 108, 110, 111, 113, 115, 117, 119, 120, 122, 124, 125, 127, 128, 130, 132, 123),
                  33: ( 97,  99, 101, 103, 105, 106, 108, 110, 112, 114, 115, 117, 119, 120, 122, 123, 125, 126, 128),
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


class Challenger_850(VelocitySpeed):
    '''
    Velocity speed tables for Challenger 850 w/ CF-34-3B1 engines
    engines.
    '''
    interpolate = True
    source = 'FDS Customer 106: FCOM'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': ( 38,  40,  42,  44,  46,  48,  50,  52, 52.9),
                  8 : (134, 138, 141, 144, 148, 151, 154, 157,  158),
                 20 : (124, 127, 130, 133, 136, 139, 142, 145,  146),
        },
        'vref': {
            'weight': ( 38,  40,  42,  44,  46, 46.75,  48,  50,  52, 52.9),
                   0: (157, 160, 163, 166, 169,   170, 179, 175, 178,  180),
                   8: (145, 148, 151, 154, 157,   158, 160, 163, 166,  168),
                  20: (139, 142, 145, 148, 151,   152, 154, 157, 160,  162),
                  30: (135, 138, 141, 144, 147,   148, 150, 153, 156,  158),
                  45: (127, 130, 133, 136, 139,   140, 142, 145, 148,  150),
        },
    }


class CRJ_200ER(VelocitySpeed):
    '''
    Velocity speed tables for CRJ-200 Regional Jet.
    '''
    interpolate = True
    source = 'FDS Customer 34 Speed Cards table'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (35000, 36000, 37000, 38000, 39000, 40000, 41000, 42000, 43000, 44000, 45000, 46000, 47000, 48000, 49000, 50000, 51000, 52000, 53000),
                  8 : (  129,   131,   133,   134,   136,   138,   140,   141,   143,   144,   146,   148,   150,   151,   153,   154,   156,   157,   158),
                 20 : (  119,   120,   122,   124,   126,   127,   129,   130,   132,   137,   135,   136,   138,   139,   141,   143,   145,   146,   147),
        },
        'vref': {
            'weight': (35000, 36000, 37000, 38000, 39000, 40000, 41000, 42000, 43000, 44000, 45000, 46000, 47000, 48000, 49000, 50000, 51000, 52000, 53000),
                   0: (  150,   153,   155,   157,   159,   160,   162,   163,   165,   166,   168,   170,   172,   173,   175,   176,   178,   179,   181),
				   8: (  140,   141,   143,   145,   147,   148,   150,   151,   153,   154,   156,   158,   160,   161,   163,   164,   166,   167,   169),
				  20: (  134,   135,   137,   139,   141,   142,   144,   145,   147,   148,   150,   152,   154,   155,   157,   158,   160,   161,   163),
				  30: (  130,   131,   133,   135,   137,   138,   140,   141,   143,   144,   146,   148,   150,   151,   153,   154,   156,   157,   159),
				  48: (  122,   123,   125,   127,   129,   130,   132,   133,   135,   136,   138,   140,   142,   143,   145,   146,   148,   149,   151),
        },
    }


class CRJ_700ER(VelocitySpeed):
    '''
    Velocity speed tables for Bombardier CRJ 700.
    '''
    interpolate = True
    source = 'FDS Customer 34 Speed Cards table'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000, 71000, 72000, 73000, 74000, 75000),
                   8: (  138,   138,   138,  138,    138,   138,   138,   138,   138,   138,   138,   138,   138,   139,   140,   141,   142,   143,   143,   144,   145),
                  20: (  133,   133,   133,  133,    133,   133,   133,   133,   133,   133,   133,   133,   133,   133,   133,   134,   134,   135,   136,   137,   148),
        },
        'vref': {
            'weight': (55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000, 71000, 72000, 73000, 74000, 75000),
                   0: (  165,  165,    165,   166,   167,   168,   169,   170,   171,   172,   173,   174,   175,   176,   177,   178,   179,   180,   181,   182,   183),
                   8: (  143,  143,    143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153,   154,   155,   156,   157,   158,   159,   160,   161),
                  20: (  137,  137,    137,   138,   139,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153,   154,   155),
                  30: (  133,  133,    133,   134,   135,   136,   137,   138,   139,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149,   150,   151),
                  45: (  125,  125,    125,   126,   127,   128,   129,   130,   131,   132,   133,   134,   135,   136,   137,   138,   139,   140,   141,   142,   143),
        },
    }


class CRJ_900(VelocitySpeed):
    '''
    Velocity speed tables for Bombardier CRJ 900.
    '''
    interpolate = True
    source = 'FDS Customer 125 CRJ QAR Analysis'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5, 32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5, 37.0, 37.5, 38.0),
                   8: ( 134,  134,  133,  133,  134,  135,  137,  138,  139,  140,  141,  142,  143,  144,  146,  147,  148,  149,  150,  151,  153,  154,  155,  156,  156,  158,  159,  160),
                  20: ( 135,  135,  134,  134,  133,  132,  132,  132,  132,  133,  134,  134,  135,  136,  137,  138,  139,  140,  142,  142,  143,  144,  145,  146,  147,  148,  149,  149),
        },
        'vref': {
            'weight': (24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5, 32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5, 37.0, 37.5, 38.0),
                   0: ( 160,  161,  162,  163,  164,  165,  167,  168,  169,  170,  172,  173,  174,  175,  176,  177,  178,  179,  181,  182,  183,  184,  185,  186,  187,  188,  189,  190),
                   1: ( 144,  145,  146,  147,  148,  149,  151,  152,  153,  154,  156,  157,  158,  159,  160,  161,  162,  163,  165,  166,  167,  168,  169,  170,  171,  172,  173,  174),
                   8: ( 138,  139,  140,  141,  142,  143,  145,  146,  147,  148,  150,  151,  152,  153,  154,  155,  156,  157,  159,  160,  161,  162,  163,  164,  165,  166,  167,  168),
                  20: ( 132,  133,  134,  135,  136,  137,  139,  140,  141,  142,  144,  145,  146,  147,  148,  149,  150,  151,  153,  154,  155,  156,  157,  158,  159,  160,  161,  162),
                  30: ( 128,  129,  130,  131,  132,  133,  135,  136,  137,  138,  140,  141,  142,  143,  144,  145,  146,  147,  149,  150,  151,  152,  153,  154,  155,  156,  157,  158),
                  45: ( 120,  121,  122,  123,  124,  125,  127,  128,  129,  130,  132,  133,  134,  135,  136,  137,  138,  139,  141,  142,  143,  144,  145,  146,  147,  148,  149,  150),
        },
    }


# Commented out due to being an aircraft series.
#class CRJ_900ER(VelocitySpeed):
    #'''
    #Velocity speed tables for Bombardier CRJ 900ER.
    #'''
    #interpolate = True
    #source = 'FDS Customer 34 Speed Cards table'
    #weight_unit = 'lb'
    #tables = {
    #    'v2': {
    #        'weight': (55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000, 71000, 72000, 73000, 74000, 75000, 76000, 77000, 78000, 79000, 80000, 81000, 82000, 82500),
    #               8: (  134,   134,   134,  134,    135,   136,   137,   138,   139,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153,   154,   155,   156,   157,   158,   159),
    #              20: (  128,   128,   128,  128,    129,   130,   131,   131,   132,   133,   134,   134,   135,   136,   137,   138,   139,   140,   140,   141,   142,   143,   144,   145,   145,   146,   147,   148,   148),
    #   },
    #    'vref': {
    #        'weight': (55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000, 71000, 72000, 73000, 74000, 75000, 76000, 77000, 78000, 79000, 80000, 81000, 82000, 82500),
    #               0: (  160,   161,   162,   163,   165,   166,   167,   168,   169,   170,   171,   172,   173,   174,   175,   176,   177,   178,   179,   180,   181,   182,   183,   184,   185,   186,   187,   188,   188),
    #               8: (  138,   139,   140,   141,   143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153,   154,   155,   156,   157,   158,   159    160,   161,   162,   163,   164,   165,   166,   166),
    #              20: (  132,   133,   134,   135,   137,   138,   139,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153    154,   155,   156,   157,   158,   159,   160,   160),
    #              30: (  128,   129,   130,   131,   133,   134,   135,   136,   137,   138,   139,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149    150,   151,   152,   153,   154,   155,   156,   156),
    #              45: (  120,   121,   122,   123,   125,   126,   127,   128,   129,   130,   131,   132,   133,   134,   135,   136,   137,   138,   139,   140,   141    142,   143,   144,   145,   146,   147,   148,   148),
    #    },
    #}


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


class Global(VelocitySpeed):
    '''
    Velocity speed tables for Global Express XRS Global and the Vision 6000. Dry Conditions at Sea Level, 0 Deg C OAT.
    '''
    interpolate = True
    source = 'FDS Customer 106'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (54000, 58000, 62000, 66000, 70000, 74000, 78000, 82000, 86000, 90000, 94000,  98000, 99500),
                  0 : ( None,   127,   129,   132,   134,   136,   139,   142,   145,   149,   152,    155,   156),
                  6 : (  112,   112,   115,   119,   122,   125,   128,   131,   134,   137,   139,    142,   142),
                 16 : (  111,   109,   112,   115,   118,   120,   123,   126,   129,   132,   135,   None,  None),
                 },
        'vref': {
            'weight': (54000, 58000, 62000, 66000, 70000, 74000, 78000, 82000, 86000, 90000, 94000, 98000, 99500),
                  30: (  107,   110,   114,   118,   121,   125,   128,   132,   135,   139,   142,   144,   145),
        },
    }


class Learjet_45(VelocitySpeed):
    '''
    Velocity speed tables for Learjet 45.
    '''
    interpolate = True
    source = 'FDS Customers 123 FCOM'
    weight_unit = 't'
    tables = {
        'v2': {
            'weight': (6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 9.752),
                   8: (116, 116, 117, 120, 123, 126, 129,   130),
        },
        'vref': {
            'weight': (6.5, 7.0, 7.5, 8.0, 8.5, 8.709),
                  40: (108, 111, 115, 118, 121,   123),
        },
    }


class Learjet_60XR(VelocitySpeed):
    '''
    Velocity speed tables for Learjet 60XR Dry Conditions at Sea Level, 0 Deg C OAT
    engines.
    '''
    interpolate = True
    source = 'FDS Customer 106: FCOM'
    weight_unit = 'lb'
    tables = {
        'v2': {
            'weight': (17400, 17800, 18100, 18200, 18400, 18700, 18800, 19100, 19400, 19800, 20100, 20400, 20800, 21100, 21400, 21800, 22100, 22500, 22800, 23200, 23500),
                  8 : (  138,   138,   138,   138,   139,   139,   140,   140,   141,   142,   143,   144,   145,   146,   147,   148,   149,   150,   151,   152,   153),
                 20 : (  132,   133,   133,   133,   134,   134,   135,   135,   136,   137,   138,   139,   140,   141,   142,   143,   143,   144,   145,   146,   147),
        },
        'vref': {
            'weight':(15300, 15600, 15800, 16100, 16400, 16800, 17100, 17300, 17600, 17800, 18100, 18400, 18700, 19200, 19500),
                  40:(  125,   126,   127,   128,   129,   130,   131,   132,   133,   134,   135,   136,   137,   138,   139),
        },
    }


##############################################################################
# Constants


# TODO: Determine a better way of looking up which table should be used!
VELOCITY_SPEED_MAP = {
    #Airbus
    ('A300-600', None): A300_600,
    ('A300-B4', None): A300_B4,

    ('A319-100', None): A319_100,
    ('A320', None): A320,
    ('A321-200', None): A321_200,

    ('A330-300', None): A330_300,
    ('A340-300', None): A340_300,

    # BAE
    ('BAE146-100', None): BAE146_100,
    ('BAE146-200', None): BAE146_200,

    # ATR
    ('ATR42-300', None): ATR42_300,
    ('ATR42-300(F)', None): ATR42_300,
    ('ATR72-200', None): ATR72_200,
    ('ATR72-200(F)', None): ATR72_200,
    ('ATR72-600', None): ATR72_600,

    # Boeing
    ('B737-300', None): B737_300,
    ('B737-300(QC)', None): B737_300,
    ('B737-400', None): B737_400,
    ('B737-500', None): B737_500,
    ('B737-600', None): B737_600,
    ('B737-700', 'CFM56-7B'): B737_700_CFM56_7B,
    ('B737-700', 'CFM56-7B27B3'): B737_700_CFM56_7B27B3,
    ('B737-800', None): B737_800,

    ('B747-400', 'CF6-80C2B1F'): B747_400_CF6_80C2B1F,
    ('B747-400', 'PW4056'): B747_400_PW4056,
    
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
    ('B767-300F(ER)', 'CF6-80C2B7F'): B767_300_CF6_80C2,
    ('B767-300(ER/F)', 'CF6-80C2'): B767_300_CF6_80C2,
    ('B767-300', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300(ER)', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300F(ER)', 'PW4000-94'): B767_300_PW4000_94,
    ('B767-300(ER/F)', 'PW4000-94'): B767_300_PW4000_94,

    ('B777-200(ER)', None): B777_200ER,
    ('B777-F', 'GE90-110B1L'): B777_F_GE90_110B1L, 

    ('B787-8', 'Trent 1000-A'): B787_8_Trent_1000_A,

    # Beechcraft
    ('1900D', None): Beechcraft_1900D,

    # Fokker
    ('F28-0070', None): F28_0070,

    # Bombardier
    ('Challenger850', None): Challenger_850,
    ('CRJ200', None): CRJ_200ER,
    ('CRJ700', None): CRJ_700ER,
    ('CRJ900', None): CRJ_900,
   #('CRJ900', None): CRJ_900ER,

    ('GlobalXRS',  None): Global,
    ('Global6000', None): Global,

    ('Learjet_45',   None): Learjet_45,
    ('Learjet_60XR', None): Learjet_60XR,

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
