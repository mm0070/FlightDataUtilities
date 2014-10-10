# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
'''

#############################################################################
# Constants


# Do not change these values without updating the following:
# - Configuration parameter in Flight Data Analyser
# - Updating the multi-states in LFLs.


# Mapping of value to configuration states (for use by Airbus and similar aircraft):
AVAILABLE_CONF_STATES = {
    0: '0',
    10: '1',
    12: '1(T/O)', # Detailed in A330 Flight Crew Operating Manual REV 004
    13: '1+F',
    16: '1*',
    20: '2',
    26: '2*',
    30: '3',
    40: '4',
    50: '5',
    90: 'Full',
}


# Reverse mapping of value to configuration states (for use by Airbus and similar aircraft):
AVAILABLE_CONF_STATES_REV = {v: k for k, v in AVAILABLE_CONF_STATES.items()}


# Mapping of value to lever positions (for use by Airbus and similar aircraft):
LEVER_STATES = {
    0: 'Lever 0',
    10: 'Lever 1',
    20: 'Lever 2',
    30: 'Lever 3',
    40: 'Lever 4',
    50: 'Lever 5',
    90: 'Lever Full',
}


# Mapping of configuration state to lever positions:
CONF_TO_LEVER = {
    # Airbus:
    '0':      'Lever 0',
    '1':      'Lever 1',
    '1(T/O)': 'Lever 1',
    '1+F':    'Lever 1',
    '1*':     'Lever 1',  # Lever position is 2 when aircraft selects 1*
    '2':      'Lever 2',
    '2*':     'Lever 3',  # Lever position is 3 when aircraft selects 2*
    '3':      'Lever 3',
    'Full':   'Lever Full',
}


# Mapping to next configuration state for looking up the next VFE:
CONF_VFE_NEXT_STATE = {
    '0':    '1',     # Based on values in A320/A321 AFPS
    '1':    '1+F',   # Based on values in A320/A321 AFPS
    '1+F':  '2',     # Based on values in A320/A321 AFPS
    '1*':   '2',     # Based on values in A320/A321 AFPS
    '2':    '3',     # Based on values in A320/A321 AFPS
    '2*':   '3',     # Based on values in A320/A321 AFPS
    '3':    'Full',  # Based on values in A320/A321 AFPS
    'Full': None,    # Based on values in A320/A321 AFPS; -30kt
}
