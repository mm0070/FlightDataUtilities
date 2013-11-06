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

AVAILABLE_CONF_STATES = {
    0: '0',
    1: '1',
    2: '1+F',
    3: '1*',
    4: '2',
    5: '2*',
    6: '3',
    7: '4',
    8: '5',
    9: 'Full',
}
# The reverse lookup
AVAILABLE_CONF_STATES_REV = dict((v, k) for k, v in AVAILABLE_CONF_STATES.items())

# Mapping of Airbus CONF to Lever positions (can be used by Falcon etc. too)
LEVER_STATES = {
    0: 'Lever 0',
    1: 'Lever 1',
    2: 'Lever 2',
    3: 'Lever 3',
    4: 'Lever Full',
}
CONF_TO_LEVER = {
    # Airbus:
    '0'   : LEVER_STATES[0],
    '1'   : LEVER_STATES[1],
    '1+F' : LEVER_STATES[1],
    '1*'  : LEVER_STATES[2], # Lever is in position 2 when aircraft selects 1*
    '2'   : LEVER_STATES[2],
    '2*'  : LEVER_STATES[3], # Lever is in position 3 when aircraft selects 2*
    '3'   : LEVER_STATES[3],
    'Full': LEVER_STATES[4],
    # Falcon:
    ##'SF0': LEVER_STATES[0],
    ##'SF1': LEVER_STATES[1],
    ##'SF2': LEVER_STATES[2],
    ##'SF3': LEVER_STATES[3],
}