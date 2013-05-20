# -*- coding: utf-8 -*-
#############################################################################

'''
Flight Data Utilities: Aircraft Configuration Information
'''

#############################################################################
# Flap Selections

# Notes:
#
# Todo:
# - B757 ACMS dataframe uses FLAP_LEVER - create a test case with this data
# - B777 Records using many discrete positions, use that! (create a multi-part
# parameter which scales FLAP_15 discrete by 15!


FLAP_SERIES_MAP = {
    '1900': (0, 10, 20, 35),                    # FAA TCDS A24CE Rev 106
    '1900C': (0, 10, 20, 35),                   # FAA TCDS A24CE Rev 106
    '1900D': (0, 17.5, 35),                     # FAA TCDS A24CE Rev 106
    'A300B2': (0, 8, 15, 25),                   # FAA TCDS A35EU Rev 26
    'A300B2K': (0, 8, 15, 25),                  # FAA TCDS A35EU Rev 26
    'A300B4(F)': (0, 8, 15, 25),                # FAA TCDS A35EU Rev 26
    'A300F4': (0, 15, 20, 40),                  # FAA TCDS A35EU Rev 26
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
    'DHC-8-100': (0, 5, 15, 35),                # FAA TCDS A13NM Rev 20
    'DHC-8-200': (0, 5, 15, 35),                # FAA TCDS A13NM Rev 20
    'DHC-8-300': (0, 5, 10, 15, 35),            # FAA TCDS A13NM Rev 20
    'DHC-8-400': (0, 5, 10, 15, 35),            # FAA TCDS A13NM Rev 20
    'ERJ-135BJ': (0, 9, 22, 45),                # FAA TCDS T00011AT Rev 29
}


FLAP_FAMILY_MAP = {
    'A310': (0, 15, 20, 40),                            # FAA TCDS A35EU Rev 26
    'A318': (0, 10, 15, 20, 40),                        # FAA TCDS A28NM Rev 11
    'A319': (0, 10, 15, 20, 40),                        # FAA TCDS A28NM Rev 11
    'A320': (0, 10, 15, 20, 35),                        # FAA TCDS A28NM Rev 11
    'A321': (0, 10, 14, 21, 25),                        # FAA TCDS A28NM Rev 11
    'A330': (0, 8, 14, 22, 32),                         # Smart Cockpit A330 General Limitions Rev 19
    'BAE 146': (0, 18, 24, 30, 33),                     # FAA TCDS A49EU Rev 17
    'B737 Classic': (0, 1, 2, 5, 10, 15, 25, 30, 40),   # Smart Cockpit B737E Flight Controls 9.10.13
    'B737 NG': (0, 1, 2, 5, 10, 15, 25, 30, 40),        # Smart Cockpit B_NG Flight Controls (1)
    'B747': (0, 1, 5, 10, 20, 25, 30),                  # Smart Cockpit B747-400 Flight Controls 9.10.8
    'B757': (0, 1, 5, 15, 20, 25, 30),                  # Smart Cockpit B757-200RR Flight Controls 9.10.8
    'B767': (0, 1, 5, 15, 20, 25, 30),                  # Smart Cockpit B767-300GE Flight Controls 9.10.10
    'B777': (0, 1, 5, 15, 20, 25, 30),                  # Smart Cockpit B777 Flight Controls 9.10.7
    'CL604': (0, 20, 30, 45),                           # FAA TCDS A21EA Rev 31
    'CL850': (0, 8, 20, 30, 45),                        # FAA TCDS A21EA Rev ??  FIXME
    'CRJ 100/200': (0, 8, 20, 30, 45),                  # FAA TCDS A21EA Rev ??; No flap 8 on some aircraft? FIXME
    'CRJ 700': (0, 1, 8, 20, 30, 45),                   # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ 900': (0, 1, 8, 20, 30, 45),                   # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'DC-9': (0, 11, 15, 28, 40),                        # FAA TCDS A6WE Rev 28 FIXME
    'ERJ-135/145': (0, 9, 18, 22, 45),                  # FAA TCDS T00011AT Rev 29
    ####'ERJ-170/175': (0, 5, 10, 20, 35),                  # FAA TCDS A56NM Rev 8 FIXME
    ####'ERJ-190/195': (0, 7, 10, 20, 37),                  # FAA TCDS A57NM Rev ?? FIXME
    'F7X': (0, 9, 20, 40),                              # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    'F28': (0, 8, 15, 25, 42),                          # FAA TCDS A20EU Rev 14
    'G-IV': (0, 10, 20, 39),                            # FAA TCDS A12EA Rev 40 FIXME
    'G-V': (0, 10, 20, 39),                             # FAA TCDS A12EA Rev 40 FIXME
    'G550': (0, 10, 20, 39),                            # FAA TCDS A12EA Rev ?? FIXME
    'GLOBAL': (0, 1, 8, 20, 30, 45),                    # FAA TCDS T00003NY Rev ?? FIXME
    'L382': (0, 50, 100),                               # FAA TCDS A1SO Rev 16 (100% = 36)
    'MD-11': (0, 15, 22, 25, 28, 35, 50),               # FAA TCDS A22WE Rev 12
    'DC-9': (0, 11, 15, 28, 40),                        # FAA TCDS ????? Rev ??
    'RJ85': (0, 18, 24, 30, 33),                        # FAA TCDS A49EU Rev 17

    'test': (5.5, 10.1, 20.9),                          # test_derive_fractional_settings

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
}


SLAT_FAMILY_MAP = {
    'A318': (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A319': (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A320': (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A321': (0, 18, 22, 27),    # FAA TCDS A28NM Rev 11
    'A330': (0, 16, 20, 23),    # Smart Cockpit A330 General Limitions Rev 19
    'CRJ 700': (0, 20, 25),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ 900': (0, 20, 25),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    ####'F7X': (Not Extended, Extended),     # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
}


#############################################################################
# Aileron Selections


AILERON_SERIES_MAP = {
    'A340-500': (0, 10),       # FAA TCDS A43NM Rev 7 & AHY A330/A340 Flight Controls
}


AILERON_FAMILY_MAP = {
    'A330': (0, 5, 10),        # Smart Cockpit A330 General Limitions Rev 19
}


#############################################################################
# Conf Selections

# Notes:
# - The series conf map will take precedence over the family conf map.
# - If using flap and slat to determine conf, only create a tuple of length 2
# - Each entry is of the form -- indication: (slat, flap, aileron)


CONF_SERIES_MAP = {
    'A340-200': {
        '0': (0, 0),           # FAA TCDS A43NM Rev 7
        '1': (20, 0),          # FAA TCDS A43NM Rev 7
        '1+F': (20, 17),       # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2': (24, 22),         # FAA TCDS A43NM Rev 7
        '3': (24, 26),         # FAA TCDS A43NM Rev 7
        'Full': (24, 32),      # FAA TCDS A43NM Rev 7
    },
    'A340-300': {
        '0': (0, 0),           # FAA TCDS A43NM Rev 7
        '1': (20, 0),          # FAA TCDS A43NM Rev 7
        '1+F': (20, 17),       # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2': (24, 22),         # FAA TCDS A43NM Rev 7
        '3': (24, 26),         # FAA TCDS A43NM Rev 7
        'Full': (24, 32),      # FAA TCDS A43NM Rev 7
    },
    'A340-500': {
        '0': (0, 0, 0),        # FAA TCDS A43NM Rev 7
        '1': (21, 0, 0),       # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        '1+F': (21, 17, 10),   # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '1*': (24, 17, 10),    # FAA TCDS A43NM Rev 7 (ECAM Indication = 2)
        '2': (24, 22, 10),     # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        '3': (24, 29, 10),     # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
        'Full': (24, 34, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    },
    'A340-600': {
        '0': (0, 0),           # FAA TCDS A43NM Rev 7
        '1': (20, 0),          # FAA TCDS A43NM Rev 7
        '1+F': (20, 17),       # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2': (23, 22),         # FAA TCDS A43NM Rev 7
        '3': (23, 29),         # FAA TCDS A43NM Rev 7
        'Full': (23, 34),      # FAA TCDS A43NM Rev 7
    },
}


CONF_FAMILY_MAP = {
    'A318': {
        '0': (0, 0),           # FAA TCDS A28NM Rev 11
        '1': (18, 0),          # FAA TCDS A28NM Rev 11
        '1+F': (18, 10),       # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2': (22, 15),         # FAA TCDS A28NM Rev 11
        '3': (22, 20),         # FAA TCDS A28NM Rev 11
        'Full': (27, 40),      # FAA TCDS A28NM Rev 11
    },
    'A319': {
        '0': (0, 0),           # FAA TCDS A28NM Rev 11
        '1': (18, 0),          # FAA TCDS A28NM Rev 11
        '1+F': (18, 10),       # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2': (22, 15),         # FAA TCDS A28NM Rev 11
        '3': (22, 20),         # FAA TCDS A28NM Rev 11
        'Full': (27, 40),      # FAA TCDS A28NM Rev 11
    },
    'A320': {
        '0': (0, 0),           # FAA TCDS A28NM Rev 11
        '1': (18, 0),          # FAA TCDS A28NM Rev 11
        '1+F': (18, 10),       # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2': (22, 15),         # FAA TCDS A28NM Rev 11
        '3': (22, 20),         # FAA TCDS A28NM Rev 11
        'Full': (27, 35),      # FAA TCDS A28NM Rev 11
    },
    'A321': {
        '0': (0, 0),           # FAA TCDS A28NM Rev 11
        '1': (18, 0),          # FAA TCDS A28NM Rev 11
        '1+F': (18, 10),       # FAA TCDS A28NM Rev 11 (ECAM Indication = 1+F)
        '2': (22, 14),         # FAA TCDS A28NM Rev 11
        '3': (22, 21),         # FAA TCDS A28NM Rev 11
        'Full': (27, 25),      # FAA TCDS A28NM Rev 11
    },
    'A330': {
        '0': (0, 0, 0),        # Smart Cockpit A330 General Limitions Rev 4 
        '1': (16, 0, 0),       # Smart Cockpit A330 General Limitions Rev 4 
        '1+F': (16, 8, 5),     # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 1+F)
        '1*': (20, 8, 10),     # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 2)
        '2': (20, 14, 10),     # Smart Cockpit A330 General Limitions Rev 4
        '2*': (23, 14, 10),    # Smart Cockpit A330 General Limitions Rev 4 (ECAM Indication = 3)
        '3': (23, 22, 10),     # Smart Cockpit A330 General Limitions Rev 4
        'Full': (23, 32, 10),  # Smart Cockpit A330 General Limitions Rev 4
    },    
    ####'F7X': {
    ####    '0'  : (0, 0),         # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    ####    'SF1': (Extended, 9),  # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    ####    'SF2': (Extended, 20), # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    ####    'SF3': (Extended, 40), # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    ####},
}


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
    raise KeyError("No flap mapping for series '%s', family '%s'." % \
        (series, family))


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
    raise KeyError("No slat mapping for series '%s', family '%s'." % \
        (series, family))


def get_aileron_map(series=None, family=None):
    '''
    Accessor for fetching aileron mapping parameters.

    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: list of detent values
    :rtype: list
    '''
    if series in AILERON_SERIES_MAP:
        return AILERON_SERIES_MAP[series]
    if family in AILERON_FAMILY_MAP:
        return AILERON_FAMILY_MAP[family]
    raise KeyError("No aileron mapping for series '%s', family '%s'" % \
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
    raise KeyError("No conf mapping for series '%s', family '%s'." % \
        (series, family))


#############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
