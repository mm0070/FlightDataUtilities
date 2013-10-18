# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
#############################################################################

'''
Flight Data Utilities: Aircraft Configuration Information
'''

#############################################################################
# Flap Selections


##### FIXME: Can we avoid doing this model specific level?
####FLAP_MODEL_MAP = {
####    'CRJ 100LR': (0, 20, 30, 45),               # FAA TCDS A21EA Rev 31
####}


FLAP_SERIES_MAP = {
    '1900':      (0, 10, 20, 35),               # FAA TCDS A24CE Rev 106
    '1900C':     (0, 10, 20, 35),               # FAA TCDS A24CE Rev 106
    '1900D':     (0, 17.5, 35),                 # FAA TCDS A24CE Rev 106
    'A300B2':    (0, 8, 15, 25),                # FAA TCDS A35EU Rev 26
    'A300B2K':   (0, 8, 15, 25),                # FAA TCDS A35EU Rev 26
    'A300B4(F)': (0, 8, 15, 25),                # FAA TCDS A35EU Rev 26
    'A300F4':    (0, 15, 20, 40),               # FAA TCDS A35EU Rev 26
    'A340-200':  (0, 17, 22, 26, 32),           # FAA TCDS A43NM Rev 7
    'A340-300':  (0, 17, 22, 26, 32),           # FAA TCDS A43NM Rev 7
    'A340-500':  (0, 17, 22, 29, 34),           # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    'A340-600':  (0, 17, 22, 29, 34),           # FAA TCDS A43NM Rev 7
    'ATR42-200': (0, 15, 30, 45),               # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-300': (0, 15, 30, 45),               # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-320': (0, 15, 30, 45),               # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-500': (0, 15, 25, 35),               # FAA TCDS A53EU Rev 21 (35 = Effective 33)
    'ATR72-100': (0, 15, 28),                   # FAA TCDS A53EU Rev 21
    'ATR72-200': (0, 15, 28),                   # FAA TCDS A53EU Rev 21
    'ATR72-210': (0, 15, 33),                   # FAA TCDS A53EU Rev 21 (-500 is -212A!)
    'Challenger850':   (0, 8, 20, 30, 45),      # FAA TCDS A21EA Rev 31
    'CRJ100': (0, 8, 20, 30, 45),               # FAA TCDS A21EA Rev 31
    'CRJ200': (0, 8, 20, 30, 45),               # FAA TCDS A21EA Rev 31
    'CRJ700':   (0, 1, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ900':   (0, 1, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'DHC-8-100': (0, 5, 15, 35),                # FAA TCDS A13NM Rev 20
    'DHC-8-200': (0, 5, 15, 35),                # FAA TCDS A13NM Rev 20
    'DHC-8-300': (0, 5, 10, 15, 35),            # FAA TCDS A13NM Rev 20
    'DHC-8-400': (0, 5, 10, 15, 35),            # FAA TCDS A13NM Rev 20
    'ERJ-135BJ': (0, 9, 22, 45),                # FAA TCDS T00011AT Rev 29
    ####'Citation Sovereign': (0, 7, 15, 35),   # Smart Cockpit Citation Sovereign Flight Controls Mode; 680; FIXME
    ####'Citation Bravo':     (0, 15, 40),      # FAA TCDS A22CE Rev 65 Smart Cockpit Citation Bravo Limitations Model 550; FIXME
    ####'Citation CJ1':       (0, 15, 35, 60),  # FAA TCDS A1WI Rev 21 & Smart Cockpit Citation CJ1 Limitations (60 = prohibited in flight) Model 525A; FIXME
    ####'Citation CJ3':       (0, 15, 35, 55),  # FAA TCDS A1WI Rev 21 & Smart Cockpit Citation CJ3 Limitations (55 = Prohibited in flight) Model 525B; FIXME
    ####'Citation X':         (0, 5, 15, 35),   # Smart Cockpit Citation X Limitations Model 750; FIXME
    ####'Citation XLS':       (0, 7, 15, 35),   # FAA TCDS A22CE Rev 65; FIXME
}


FLAP_FAMILY_MAP = {
    'A310':    (0, 15, 20, 40),                        # FAA TCDS A35EU Rev 26
    'A318':    (0, 10, 15, 20, 40),                    # FAA TCDS A28NM Rev 11
    'A319':    (0, 10, 15, 20, 40),                    # FAA TCDS A28NM Rev 11
    'A320':    (0, 10, 15, 20, 35),                    # FAA TCDS A28NM Rev 11
    'A321':    (0, 10, 14, 21, 25),                    # FAA TCDS A28NM Rev 11
    'A330':    (0, 8, 14, 22, 32),                     # Smart Cockpit A330 General Limitions Rev 19
    'A380':    (0, 8, 17, 26, 33),                     # Smart Cockpit A380 Briefing For Pilots
    'BAE 146': (0, 18, 24, 30, 33),                    # FAA TCDS A49EU Rev 17 (Includes RJ85 & RJ100)
    'B727':    (0, 2, 5, 15, 25, 30, 40),              # Smart Cockpit B727 Flight Controls
    'B737 Classic': (0, 1, 2, 5, 10, 15, 25, 30, 40),  # Smart Cockpit B737E Flight Controls 9.10.13
    'B737 NG': (0, 1, 2, 5, 10, 15, 25, 30, 40),       # Smart Cockpit B_NG Flight Controls (1)
    'B747':    (0, 1, 5, 10, 20, 25, 30),              # Smart Cockpit B747-400 Flight Controls 9.10.8
    'B757':    (0, 1, 5, 15, 20, 25, 30),              # Smart Cockpit B757-200RR Flight Controls 9.10.8
    'B767':    (0, 1, 5, 15, 20, 25, 30),              # Smart Cockpit B767-300GE Flight Controls 9.10.10
    'B777':    (0, 1, 5, 15, 20, 25, 30),              # Smart Cockpit B777 Flight Controls 9.10.7
    'B787':    (0, 1, 5, 15, 20, 25, 30),              # FAA TCDS T00021SE Rev 6
    'CL-600':   (0, 20, 30, 45),                       # FAA TCDS A21EA Rev 31
    'DC-9':    (0, 13, 20, 25, 30, 40),                # FAA TCDS A6WE Rev 28 (DC-9-81 & DC-9-82)
    'ERJ-135/145': (0, 9, 18, 22, 45),                 # FAA TCDS T00011AT Rev 29
    ####'ERJ-170/175': (0, 5, 10, 20, 35),             # FAA TCDS A56NM Rev 8; FIXME
    'ERJ190':  (0, 7, 10, 20, 37),                     # FAA TCDS A57NM Rev 9 & Smart Cockpit Embraer_190 Flight Controls & FAA TCDS A57NM Rev 9
    'F27':     (0, 5, 10, 15, 20, 25, 35),             # FAA TCDS A-817 Rev 21
    'F28':     (0, 8, 15, 25, 42),                     # FAA TCDS A20EU Rev 14
    'Falcon':  (0, 9, 20, 40),                         # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    'G550':    (0, 10, 20, 39),                        # FAA TCDS A12EA Rev 40
    'G-IV':    (0, 10, 20, 39),                        # FAA TCDS A12EA Rev 40
    'G-V':     (0, 10, 20, 39),                        # FAA TCDS A12EA Rev 40
    'Global':  (0, 6, 16, 30),                         # FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1
    'L100':    (0, 50, 100),                           # FAA TCDS A1SO Rev 16 (100% = 36)
    'Learjet': (0, 8, 20, 40),                         # FAA TCDS T00008WI Rev 17
    'L1011':   (0, 4, 10, 14, 18, 22, 33),             # FAA TCDS A23WE Rev 19
    ####'MD-11':   (0, 15, 22, 25, 28, 35, 50),        # FAA TCDS A22WE Rev 12; FIXME
}


#############################################################################
# Slat Selections


SLAT_SERIES_MAP = {
    'A300B2':    (0, 20, 25),   # FAA TCDS A35EU Rev 26; FIXME: B2-203!
    'A300B2K':   (0, 16, 25),   # FAA TCDS A35EU Rev 26
    'A300B4(F)': (0, 16, 25),   # FAA TCDS A35EU Rev 26
    'A300F4':    (0, 15, 30),   # FAA TCDS A35EU Rev 26
    'A340-200':  (0, 20, 24),   # FAA TCDS A43NM Rev 7
    'A340-300':  (0, 20, 24),   # FAA TCDS A43NM Rev 7
    'A340-500':  (0, 21, 24),   # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    'A340-600':  (0, 20, 23),   # FAA TCDS A43NM Rev 7
    'CRJ700':    (0, 20, 25),   # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ900':    (0, 20, 25),   # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    ####'Citation X': (Not Extended, Extended),    # Smart Cockpit Citation X Limitations Model 750; FIXME
}


SLAT_FAMILY_MAP = {
    'A310':    (0, 15, 20, 30),    # FAA TCDS A35EU Rev 26
    'A318':    (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A319':    (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A320':    (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A321':    (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A330':    (0, 16, 20, 23),    # Smart Cockpit A330 General Limitions Rev 19
    'A380':    (0, 20, 23),        # Smart Cockpit A380 Briefing For Pilots
    'B787':    (0, 50, 100),       # Boeing 787 Operations Manual
    'DC-9':    (0, 17.8, 21),      # FAA TCDS A6WE Rev 28 (DC-9-81 & DC-9-82)
    'ERJ190':  (0, 15, 25),        # FAA TCDS A57NM Rev 9 & Smart Cockpit Embraer_190 Flight Controls
    ####'Falcon': (Not Extended, Extended),   # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
	#### Note: Slats Extended: Inboard Down = 20 deg, Median & Outboard Down = 35 deg
    'Global': (0, 20),             # (Not Extended, Extended) FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1 & LFL doc
}


#############################################################################
# Aileron Selections


AILERON_SERIES_MAP = {
    'A340-500': (0, 10),        # FAA TCDS A43NM Rev 7 & AHY A330/A340 Flight Controls
}


AILERON_FAMILY_MAP = {
    'A330': (0, 5, 10),         # Smart Cockpit A330 General Limitions Rev 19
    'A380': (0, 5, 10),         # Smart Cockpit A380 Briefing For Pilots
}


#############################################################################
# Conf Selections

# Notes:
# - The series conf map will take precedence over the family conf map.
# - If using flap and slat to determine conf, only create a tuple of length 2
# - Each entry is of the form -- indication: (slat, flap, aileron)


CONF_SERIES_MAP = {
    'A340-200': {
        '0':    (0, 0),        # FAA TCDS A43NM Rev 7
        '1':    (20, 0),       # FAA TCDS A43NM Rev 7
        '1+F':  (20, 17),      # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2':    (24, 22),      # FAA TCDS A43NM Rev 7
        '3':    (24, 26),      # FAA TCDS A43NM Rev 7
        'Full': (24, 32),      # FAA TCDS A43NM Rev 7
    },
    'A340-300': {
        '0':    (0, 0),        # FAA TCDS A43NM Rev 7
        '1':    (20, 0),       # FAA TCDS A43NM Rev 7
        '1+F':  (20, 17),      # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2':    (24, 22),      # FAA TCDS A43NM Rev 7
        '3':    (24, 26),      # FAA TCDS A43NM Rev 7
        'Full': (24, 32),      # FAA TCDS A43NM Rev 7
    },
    'A340-500': {
        '0':    (0, 0, 0),     # FAA TCDS A43NM Rev 7
        '1':    (21, 0, 0),    # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        '1+F':  (21, 17, 10),  # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '1*':   (24, 17, 10),  # FAA TCDS A43NM Rev 7 (ECAM Indication = 2)
        '2':    (24, 22, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        '3':    (24, 29, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        'Full': (24, 34, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    },
    'A340-600': {
        '0':    (0, 0),        # FAA TCDS A43NM Rev 7
        '1':    (20, 0),       # FAA TCDS A43NM Rev 7
        '1+F':  (20, 17),      # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2':    (23, 22),      # FAA TCDS A43NM Rev 7
        '3':    (23, 29),      # FAA TCDS A43NM Rev 7
        'Full': (23, 34),      # FAA TCDS A43NM Rev 7
    },
    'CRJ700': {
        '0':    (0, 0),        # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '1':    (20, 0),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '8':    (20, 8),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '20':   (20, 20),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '30':   (25, 30),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '45':   (25, 45),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    },
    'CRJ900': {
        '0':    (0, 0),        # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '1':    (20, 0),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '8':    (20, 8),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '20':   (20, 20),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '30':   (25, 30),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        '45':   (25, 45),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    },
}


CONF_FAMILY_MAP = {
    'A318': {
        '0':    (0, 0),        # FAA TCDS A28NM Rev 11
        '1':    (18, 0),       # FAA TCDS A28NM Rev 11
        '1+F':  (18, 10),      # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2':    (22, 15),      # FAA TCDS A28NM Rev 11
        '3':    (22, 20),      # FAA TCDS A28NM Rev 11
        'Full': (27, 40),      # FAA TCDS A28NM Rev 11
    },
    'A319': {
        '0':    (0, 0),        # FAA TCDS A28NM Rev 11
        '1':    (18, 0),       # FAA TCDS A28NM Rev 11
        '1+F':  (18, 10),      # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2':    (22, 15),      # FAA TCDS A28NM Rev 11
        '3':    (22, 20),      # FAA TCDS A28NM Rev 11
        'Full': (27, 40),      # FAA TCDS A28NM Rev 11
    },
    'A320': {
        '0':    (0, 0),        # FAA TCDS A28NM Rev 11
        '1':    (18, 0),       # FAA TCDS A28NM Rev 11
        '1+F':  (18, 10),      # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2':    (22, 15),      # FAA TCDS A28NM Rev 11
        '3':    (22, 20),      # FAA TCDS A28NM Rev 11
        'Full': (27, 35),      # FAA TCDS A28NM Rev 11
    },
    'A321': {
        '0':    (0, 0),        # FAA TCDS A28NM Rev 11
        '1':    (18, 0),       # FAA TCDS A28NM Rev 11
        '1+F':  (18, 10),      # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2':    (22, 14),      # FAA TCDS A28NM Rev 11
        '3':    (22, 21),      # FAA TCDS A28NM Rev 11
        'Full': (27, 25),      # FAA TCDS A28NM Rev 11
    },
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
    'A380': {
        '0':    (0, 0, 0),     # Smart Cockpit A380 Briefing For Pilots
        '1':    (20, 0, 0),    # Smart Cockpit A380 Briefing For Pilots
        '1+F':  (20, 8, 5),    # Smart Cockpit A380 (ECAM Indication = 1+F)
        '2':    (20, 17, 5),   # Smart Cockpit A380 Briefing For Pilots
        '3':    (23, 26, 5),   # Smart Cockpit A380 Briefing For Pilots
        'Full': (23, 33, 10),  # Smart Cockpit A380 Briefing For Pilots
    },
    'B787': { # Flap settings must be integers.
        0:    (0, 0),
        1:    (50, 0),
        5:    (50, 5),
        15:   (50, 15),
        20:   (50, 20),
        25:   (100, 20),
        30:   (100, 30),
    },
    'ERJ190': {
        '0':    (0, 0),        # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        '1':    (15, 7),       # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        '2':    (15, 10),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        '3':    (15, 20),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        '4':    (25, 20),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        '5':    (25, 20),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        'Full': (25, 37),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
    },
    ####'Falcon': {
    ####    '0'  : (0, 0),         # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
    ####    'SF1': (Extended, 9),  # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
    ####    'SF2': (Extended, 20), # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
    ####    'SF3': (Extended, 40), # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
	#### Note: Slats Extended: Inboard Down = 20 deg, Median & Outboard Down = 35 deg
    ####},
}


#############################################################################
# Imports


import logging
import numpy as np

from itertools import imap


#############################################################################
# Globals


logger = logging.getLogger(name=__name__)


#############################################################################
# Accessors


def get_flap_detents():
    '''
    Get all flap combinations from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    all_detents = set()
    for detents in FLAP_SERIES_MAP.itervalues():
        all_detents.update(detents)
    for detents in FLAP_FAMILY_MAP.itervalues():
        all_detents.update(detents)
    return sorted(all_detents)


def get_conf_detents():
    '''
    Get all conf combinations from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    all_detents = set()
    for detents in imap(dict.keys, CONF_SERIES_MAP.itervalues()):
        all_detents.update(detents)
    for detents in imap(dict.keys, CONF_FAMILY_MAP.itervalues()):
        all_detents.update(detents)
    return sorted(all_detents)


def get_slat_detents():
    '''
    Get all slat detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    all_detents = set()
    for detents in SLAT_SERIES_MAP.itervalues():
        all_detents.update(detents)
    for detents in SLAT_FAMILY_MAP.itervalues():
        all_detents.update(detents)
    return sorted(all_detents)


def get_flap_map(series=None, family=None):
    '''
    Accessor for fetching flap mapping parameters.

    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: list of detent values
    :rtype: list
    '''
    if series in FLAP_SERIES_MAP:
        return FLAP_SERIES_MAP[series]
    if family in FLAP_FAMILY_MAP:
        return FLAP_FAMILY_MAP[family]
    raise KeyError("No flap mapping for series '%s', family '%s'." %
                   (series, family))


def get_flap_values_mapping(series, family, flap_param=None):
    '''
    Get the flap mapping for the aircraft type. Should this not be
    available, rounds the available flap array to the nearest 5 degrees.

    If flap_param is None, raises KeyError as no fallback available.

    Returns the values mapping:
    { int(flap angle) : str(flap angle) }

    :param series: Aircraft Series with .value attribute
    :type series: Attribute
    :param family: Aircraft Family with .value attribute
    :type family: Attribute
    :param flap_param: Recorded flap parameter.
    :type flap_param: Parameter
    :returns: Values Mapping for each flap setting for provided aircraft type
    :rtype: Dict
    '''
    try:
        flap_steps = get_flap_map(series.value, family.value)
    except KeyError:
        # no flaps mapping, round to nearest 5 degrees
        logger.warning("No flap settings for series '%s' family '%s' - "
                       "rounding to nearest 5", series.value, family.value)
        if flap_param is None:
            raise
        # round to nearest 5 degrees (as per round_to_nearest)
        step = 5.0
        array = np.ma.round(flap_param.array / step) * step
        flap_steps = [int(f) for f in np.ma.unique(array)
                      if f is not np.ma.masked]
    return {int(f): str(f) for f in flap_steps}


def get_slat_map(series=None, family=None):
    '''
    Accessor for fetching slat mapping parameters.

    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: list of detent values
    :rtype: list
    '''
    if series in SLAT_SERIES_MAP:
        return SLAT_SERIES_MAP[series]
    if family in SLAT_FAMILY_MAP:
        return SLAT_FAMILY_MAP[family]
    raise KeyError("No slat mapping for series '%s', family '%s'." %
                   (series, family))


def get_aileron_map(series=None, family=None):
    '''
    Accessor for fetching aileron mapping parameters. Note this is used for
    generating the Flaperon parameter.

    :param series: Aircraft series e.g. A340-500
    :type series: String
    :param family: Aircraft family e.g. A330
    :type family: String
    :raises: KeyError if no mapping found
    :returns: list of detent values
    :rtype: list
    '''
    if series in AILERON_SERIES_MAP:
        return AILERON_SERIES_MAP[series]
    if family in AILERON_FAMILY_MAP:
        return AILERON_FAMILY_MAP[family]
    raise KeyError("No aileron mapping for series '%s', family '%s'" %
                   (series, family))


def get_conf_map(series=None, family=None):
    '''
    Accessor for fetching conf mapping parameters.

    Return is a dictionary of state: tuple where tuple can contain either
    (slat, flap) or (slat, flap, aileron) depending on Aircraft requirements.

    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: conf mapping
    :rtype: dict
    '''
    if series in CONF_SERIES_MAP:
        return CONF_SERIES_MAP[series]
    if family in CONF_FAMILY_MAP:
        return CONF_FAMILY_MAP[family]
    raise KeyError("No conf mapping for series '%s', family '%s'." %
                   (series, family))
