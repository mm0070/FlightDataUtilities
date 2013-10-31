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
    'A330':       (0, 16, 20, 23),  # Smart Cockpit A330 General Limitions Rev 19
    'Global':     (0, 20),          # FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1 & LFL
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
#           'state': (slat, flap, aileron),
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
#   - aileron:  aileron angle in degrees for the state. (float or integer)
#
# Additional import notes to follow:
#
#   - The aileron value is optional if the aircraft doesn't use it.
#   - If not using aileron, to determine conf, only create a tuple of length 2.


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
        (0,  '0'):    (0, 0),      # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (1,  '0+S'):  (20, 0),     # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (6,  '6'):    (20, 6),     # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (16, '16'):   (20, 16),    # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (30, '30'):   (20, 30),    # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
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
