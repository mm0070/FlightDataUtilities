# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
#############################################################################

'''
Utilities for looking up model information for various aircraft.
'''

#############################################################################
# Flap Selections

# The format for the following mappings should match the following:
#
#   {
#       'name': (0, angle, ...),
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - angle:  flap angle in degrees. (float or integer)
#
# Additional import notes to follow:
#
#   - There must always be a retracted angle value which is (usually) 0.


FLAP_MODEL_MAP = {}


FLAP_SERIES_MAP = {}


FLAP_FAMILY_MAP = {
    'A330':         (0, 8, 14, 22, 32),                # Smart Cockpit A330 General Limitions Rev 19
    'B737 Classic': (0, 1, 2, 5, 10, 15, 25, 30, 40),  # Smart Cockpit B737E Flight Controls 9.10.13
    'Global':       (0, 6, 16, 30),                    # FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1
}


#############################################################################
# Slat Selections

# The format for the following mappings should match the following:
#
#   {
#       'name': (0, angle, ...),
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - angle:  slat angle in degrees. (float or integer)
#
# Additional import notes to follow:
#
#   - There must always be a retracted angle value which is (usually) 0.


SLAT_MODEL_MAP = {}


SLAT_SERIES_MAP = {}


SLAT_FAMILY_MAP = {
    'A330':   (0, 16, 20, 23),  # Smart Cockpit A330 General Limitions Rev 19
    'Global': (0, 20),          # FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1 & LFL
}


#############################################################################
# Aileron Selections

# The format for the following mappings should match the following:
#
#   {
#       'name': (0, angle, ...),
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - angle:  aileron angle in degrees. (float or integer)
#
# Additional import notes to follow:
#
#   - There must always be a retracted angle value which is (usually) 0.


AILERON_MODEL_MAP = {}


AILERON_SERIES_MAP = {}


AILERON_FAMILY_MAP = {
    'A330': (0, 5, 10),   # Smart Cockpit A330 General Limitions Rev 19
}


#############################################################################
# Conf Selections

# The format for the following mappings should match the following:
#
#   {
#       'name': {
#           'state': (slat, flap, flaperon),
#           ...
#       },
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:     model, series or family name of the aircraft. (string)
#   - state:    name of the state for the configuration parameter. (string)
#   - slat:     slat angle in degrees for the state. (float or integer)
#   - flap:     flap angle in degrees for the state. (float or integer)
#   - flaperon: aileron angle in degrees for the state. (float or integer)
#
# Additional import notes to follow:
#
#   - The flaperon value is optional if the aircraft doesn't use it.
#   - If not using flaperon, to determine conf, fill with None


CONF_MODEL_MAP = {}


CONF_SERIES_MAP = {}


CONF_FAMILY_MAP = {
    'A330': {
        '0':    (0, 0, 0),     # Smart Cockpit A330 General Limitions Rev 4
        '1':    (16, 0, 0),    # Smart Cockpit A330 General Limitions Rev 4
        '1+F':  (16, 8, 5),    # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 1+F)
        '1*':   (20, 8, 10),   # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 2)
        '2':    (20, 14, 10),  # Smart Cockpit A330 General Limitions Rev 4
        '2*':   (23, 14, 10),  # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 3)
        '3':    (23, 22, 10),  # Smart Cockpit A330 General Limitions Rev 4
        'Full': (23, 32, 10),  # Smart Cockpit A330 General Limitions Rev 4
    },
}


#############################################################################
# Lever Selections

# The format for the following mappings should match the following:
#
#   {
#       'name': {
#           (value, 'state'): (slat, flap),
#           ...
#       },
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - value:  raw value for a multi-state parameter. (float or integer)
#   - state:  name of the state for a multi-state parameter. (string)
#   - slat:   slat angle in degrees for the lever position. (float or integer)
#   - flap:   flap angle in degrees for the lever position. (float or integer)


LEVER_MODEL_MAP = {}


LEVER_SERIES_MAP = {}


LEVER_FAMILY_MAP = {
    'Global': {
        (0,  '0'):   (0, 0, None),    # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (1,  '0+S'): (20, 0, None),   # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (6,  '6'):   (20, 6, None),   # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (16, '16'):  (20, 16, None),  # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (30, '30'):  (20, 30, None),  # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
    },
}


#############################################################################
# Stabilizer Limits

# The format for the following mappings should match the following:
#
#   {
#       'name': (angle, angle),
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - angle:  stabilizer angle in degrees. (float or integer)


STABILIZER_MODEL_MAP = {}


STABILIZER_SERIES_MAP = {
    'B737-600': (2.25, 8.6),
}


STABILIZER_FAMILY_MAP = {}


#############################################################################
# Airbrake Coefficient

# The format for the following mappings should match the following:
#
#   {
#       'name': {
#           'state': value,
#           ...
#       },
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - state:  a configuration state name. (string)
#   - value:  airbrake coefficient for the configuration state. (float)


KAF_MODEL_MAP = {}


KAF_SERIES_MAP = {}


KAF_FAMILY_MAP = {
    'A330': {
        '1':    0.0000,  # FIXME: Lookup correct value as example...
        '1+F':  0.0000,  # FIXME: Lookup correct value as example...
        '2':    0.0000,  # FIXME: Lookup correct value as example...
        '3':    0.0000,  # FIXME: Lookup correct value as example...
        'Full': 0.0000,  # FIXME: Lookup correct value as example...
    },
}


#############################################################################
# VLS1g Constant

# The format for the following mappings should match the following:
#
#   {
#       'name': {
#           'engine': {
#               'state': value,
#               ...
#            },
#            ...
#       },
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:    model, series or family name of the aircraft. (string)
#   - engine:  manufacturer name of the engine. (string)
#   - state:   a configuration state name. (string)
#   - value:   VLS1g constant for the configuration state. (float)


VLS1G_MODEL_MAP = {}


VLS1G_SERIES_MAP = {}


VLS1G_FAMILY_MAP = {
    'A330': {
        'Rolls Royce': {
            '0':    10.950,  # A320/A321 AFPS
            '1':     9.820,  # A320/A321 AFPS
            '1+F':   9.180,  # A320/A321 AFPS
            '1*':    8.920,  # A320/A321 AFPS
            '2':     8.650,  # A320/A321 AFPS
            '2*':    8.540,  # A320/A321 AFPS
            '3':     8.420,  # A320/A321 AFPS
            'Full':  8.160,  # A320/A321 AFPS
        },
    },
}


##############################################################################
# (Recommended) Flap Manoeuvring Speed Tables

# The format for the following mappings should match the following:
#
#   {
#       'name': {
#           'state': value,
#           ...
#       },
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - state:  a flap state name. (string)
#   - value:  arguments for determining flap manoeuvring speed. (mixed)
#
# The format of value is one of the following:
#
#   - (detent, offset)
#   - ((max_wt, speed), ...)
#
# Where the parameters are:
#
#   - detent: flap detent for vref lookup table, e.g. '30' --> Vref30 (string)
#   - offset: a speed offset to apply in knots (integer)
#   - max_wt: the upper end of a weight range (integer)
#   - speed:  a fixed speed value to be used for the weight range (integer)
#
# None can be specified for the value where a flap setting is unavailable.


FMS_MODEL_MAP = {}


FMS_SERIES_MAP = {}


FMS_FAMILY_MAP = {
    'B737 Classic': {
        # Weight Ranges:
        # - kg: (w <=  53070,  53070 < w <=  62823,  62823 < w)
        # - lb: (w <= 117000, 117000 < w <= 138500, 138500 < w)
        # Applicable to aircraft with the following installed:
        # - Rudder Pressure Reducer (RDR)
        # - Rudder System Enhancement Program (RSEP)
        # Adjustments for aircraft without modifications:
        # - Add 10 kt for flap 0, 1 & 5 if RDR deactivated or not installed.
        # - Add 10 kt for flap 5 & 10 if RSEP deactivated or not installed.
        '0':  ((53070, 210), (62823, 220), (99999, 230)),  # B737 FCTM
        '1':  ((53070, 190), (62823, 200), (99999, 210)),  # B737 FCTM
        '2':  None,                                        # Not defined...
        '5':  ((53070, 170), (62823, 180), (99999, 190)),  # B737 FCTM
        '10': ((53070, 160), (62823, 170), (99999, 180)),  # B737 FCTM
        '15': ((53070, 150), (62823, 160), (99999, 170)),  # B737 FCTM
        '25': ((53070, 140), (62823, 150), (99999, 160)),  # B737 FCTM
        '30': ('30', 0),                                   # B737 FCTM
        '40': ('40', 0),                                   # B737 FCTM
    },
}

##############################################################################
# Control surface ranges

# This is the list of tables required for full and free checks
# Entries below should be made in the format
#    'name': (min, max),   # Source of values
#
# Names used in each section must match those used in the Polaris database.
# Lower level types (e.g. model) only need adding if they vary from the level
# above (e.g. series, family)

AILERON_RANGE_MODEL_MAP = {}

AILERON_RANGE_SERIES_MAP = {}

AILERON_RANGE_FAMILY_MAP = {}

ELEVATOR_RANGE_MODEL_MAP = {}

ELEVATOR_RANGE_SERIES_MAP = {}

ELEVATOR_RANGE_FAMILY_MAP = {}

RUDDER_RANGE_MODEL_MAP = {}

RUDDER_RANGE_SERIES_MAP = {}

RUDDER_RANGE_FAMILY_MAP = {}

# This is the list of tables required for populating the new graph features

CONTROL_COLUMN_RANGE_FAMILY_MAP = {}

CONTROL_COLUMN_RANGE_SERIES_MAP = {}

CONTROL_COLUMN_RANGE_MODEL_MAP = {}

CONTROL_WHEEL_RANGE_FAMILY_MAP = {}

CONTROL_WHEEL_RANGE_SERIES_MAP = {}

CONTROL_WHEEL_RANGE_MODEL_MAP = {}

SIDESTICK_PITCH_RANGE_FAMILY_MAP = {}

SIDESTICK_PITCH_RANGE_SERIES_MAP = {}

SIDESTICK_PITCH_RANGE_MODEL_MAP = {}

SIDESTICK_ROLL_RANGE_FAMILY_MAP = {}

SIDESTICK_ROLL_RANGE_SERIES_MAP = {}

SIDESTICK_ROLL_RANGE_MODEL_MAP = {}

RUDDER_PEDAL_RANGE_FAMILY_MAP = {}

RUDDER_PEDAL_RANGE_SERIES_MAP = {}

RUDDER_PEDAL_RANGE_MODEL_MAP = {}

THROTTLE_LEVER_RANGE_FAMILY_MAP = {}

THROTTLE_LEVER_RANGE_SERIES_MAP = {}

THROTTLE_LEVER_RANGE_MODEL_MAP = {}
