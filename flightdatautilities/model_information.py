# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
#############################################################################

'''
Flight Data Utilities: Aircraft Configuration Information
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


FLAP_MODEL_MAP = {
####'CRJ100LR':           (0, 20, 30, 45),             # FAA TCDS A21EA Rev 31
}


FLAP_SERIES_MAP = {
    '1900':               (0, 10, 20, 35),             # FAA TCDS A24CE Rev 106
    '1900C':              (0, 10, 20, 35),             # FAA TCDS A24CE Rev 106
    '1900D':              (0, 17.5, 35),               # FAA TCDS A24CE Rev 106
    'A300B2':             (0, 8, 15, 25),              # FAA TCDS A35EU Rev 26
    'A300B2K':            (0, 8, 15, 25),              # FAA TCDS A35EU Rev 26
    'A300B4(F)':          (0, 8, 15, 25),              # FAA TCDS A35EU Rev 26
    'A300F4':             (0, 15, 20, 40),             # FAA TCDS A35EU Rev 26
    'A340-200':           (0, 17, 22, 26, 32),         # FAA TCDS A43NM Rev 7
    'A340-300':           (0, 17, 22, 26, 32),         # FAA TCDS A43NM Rev 7
    'A340-500':           (0, 17, 22, 29, 34),         # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    'A340-600':           (0, 17, 22, 29, 34),         # FAA TCDS A43NM Rev 7
    'ATR42-200':          (0, 15, 30, 45),             # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-300':          (0, 15, 30, 45),             # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-320':          (0, 15, 30, 45),             # FAA TCDS A53EU Rev 21 (45 = Emergency)
    'ATR42-500':          (0, 15, 25, 35),             # FAA TCDS A53EU Rev 21 (35 = Effective 33)
    'ATR72-100':          (0, 15, 28),                 # FAA TCDS A53EU Rev 21
    'ATR72-200':          (0, 15, 28),                 # FAA TCDS A53EU Rev 21
    'ATR72-210':          (0, 15, 33),                 # FAA TCDS A53EU Rev 21 (-500 is -212A!)
    'Challenger300':      (0, 10, 20, 30),             # FAA TCDS T00005NY Rev 6 & Smart Cockpit Challenger300 Flight Controls
    'Challenger604':      (0, 20, 30, 45),             # FAA TCDS A21EA Rev 31
    'Challenger605':      (0, 20, 30, 45),             # FAA TCDS A21EA Rev 31
    'Challenger850':      (0, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31
    'CRJ100':             (0, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31
    'CRJ200':             (0, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31
    'CRJ700':             (0, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ900':             (0, 8, 20, 30, 45),          # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'DHC-8-100':          (0, 5, 15, 35),              # FAA TCDS A13NM Rev 20
    'DHC-8-200':          (0, 5, 15, 35),              # FAA TCDS A13NM Rev 20
    'DHC-8-300':          (0, 5, 10, 15, 35),          # FAA TCDS A13NM Rev 20
    'DHC-8-400':          (0, 5, 10, 15, 35),          # FAA TCDS A13NM Rev 20
    'ERJ-135BJ':          (0, 9, 22, 45),              # FAA TCDS T00011AT Rev 29
####'Citation Sovereign': (0, 7, 15, 35),              # Smart Cockpit Citation Sovereign Flight Controls Mode; 680; FIXME
####'Citation Bravo':     (0, 15, 40),                 # FAA TCDS A22CE Rev 65 Smart Cockpit Citation Bravo Limitations Model 550; FIXME
####'Citation CJ1':       (0, 15, 35, 60),             # FAA TCDS A1WI Rev 21 & Smart Cockpit Citation CJ1 Limitations (60 = prohibited in flight) Model 525A; FIXME
####'Citation CJ3':       (0, 15, 35, 55),             # FAA TCDS A1WI Rev 21 & Smart Cockpit Citation CJ3 Limitations (55 = Prohibited in flight) Model 525B; FIXME
####'Citation X':         (0, 5, 15, 35),              # Smart Cockpit Citation X Limitations Model 750; FIXME
####'Citation XLS':       (0, 7, 15, 35),              # FAA TCDS A22CE Rev 65; FIXME
}


FLAP_FAMILY_MAP = {
    'A310':         (0, 15, 20, 40),                   # FAA TCDS A35EU Rev 26
    'A318':         (0, 10, 15, 20, 40),               # FAA TCDS A28NM Rev 11
    'A319':         (0, 10, 15, 20, 40),               # FAA TCDS A28NM Rev 11
    'A320':         (0, 10, 15, 20, 35),               # FAA TCDS A28NM Rev 11
    'A321':         (0, 10, 14, 21, 25),               # FAA TCDS A28NM Rev 11
    'A330':         (0, 8, 14, 22, 32),                # Smart Cockpit A330 General Limitions Rev 19
    'A380':         (0, 8, 17, 26, 33),                # Smart Cockpit A380 Briefing For Pilots
    'BAE 146':      (0, 18, 24, 30, 33),               # FAA TCDS A49EU Rev 17 (Includes RJ85 & RJ100)
    'B727':         (0, 2, 5, 15, 25, 30, 40),         # Smart Cockpit B727 Flight Controls
    'B737 Classic': (0, 1, 2, 5, 10, 15, 25, 30, 40),  # Smart Cockpit B737E Flight Controls 9.10.13
    'B737 NG':      (0, 1, 2, 5, 10, 15, 25, 30, 40),  # Smart Cockpit B_NG Flight Controls (1)
    'B747':         (0, 1, 5, 10, 20, 25, 30),         # Smart Cockpit B747-400 Flight Controls 9.10.8
    'B757':         (0, 1, 5, 15, 20, 25, 30),         # Smart Cockpit B757-200RR Flight Controls 9.10.8
    'B767':         (0, 1, 5, 15, 20, 25, 30),         # Smart Cockpit B767-300GE Flight Controls 9.10.10
    'B777':         (0, 1, 5, 15, 20, 25, 30),         # Smart Cockpit B777 Flight Controls 9.10.7
    'B787':         (0, 5, 15, 20, 30),                # FAA TCDS T00021SE Rev 6
    'CL-600':       (0, 20, 30, 45),                   # FAA TCDS A21EA Rev 31
    'DC-9':         (0, 13, 20, 25, 30, 40),           # FAA TCDS A6WE Rev 28 (DC-9-81 & DC-9-82)
    'ERJ-135/145':  (0, 9, 18, 22, 45),                # FAA TCDS T00011AT Rev 29
####'ERJ-170/175':  (0, 5, 10, 20, 35),                # FAA TCDS A56NM Rev 8; FIXME
    'ERJ190':       (0, 7, 10, 20, 37),                # FAA TCDS A57NM Rev 9 & Smart Cockpit Embraer_190 Flight Controls & FAA TCDS A57NM Rev 9
    'F27':          (0, 5, 10, 15, 20, 25, 35),        # FAA TCDS A-817 Rev 21
    'F28':          (0, 8, 15, 25, 42),                # FAA TCDS A20EU Rev 14
    'Falcon':       (0, 9, 20, 40),                    # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2
    'G550':         (0, 10, 20, 39),                   # FAA TCDS A12EA Rev 40
    'G-IV':         (0, 10, 20, 39),                   # FAA TCDS A12EA Rev 40
    'G-V':          (0, 10, 20, 39),                   # FAA TCDS A12EA Rev 40
    'Global':       (0, 6, 16, 30),                    # FAA TCDS T00003NY Rev 16 & Smart Cockpit G5000 Limitations Vol 1
    'L100':         (0, 50, 100),                      # FAA TCDS A1SO Rev 16 (100% = 36)
    'L1011':        (0, 4, 10, 14, 18, 22, 33),        # FAA TCDS A23WE Rev 19
    'Learjet':      (0, 8, 20, 40),                    # FAA TCDS T00008WI Rev 17
####'MD-11':        (0, 15, 22, 25, 28, 35, 50),       # FAA TCDS A22WE Rev 12; FIXME
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


SLAT_SERIES_MAP = {
    'A300B2':     (0, 20, 25),       # FAA TCDS A35EU Rev 26; FIXME: B2-203!
    'A300B2K':    (0, 16, 25),       # FAA TCDS A35EU Rev 26
    'A300B4(F)':  (0, 16, 25),       # FAA TCDS A35EU Rev 26
    'A300F4':     (0, 15, 30),       # FAA TCDS A35EU Rev 26
    'A340-200':   (0, 20, 24),       # FAA TCDS A43NM Rev 7
    'A340-300':   (0, 20, 24),       # FAA TCDS A43NM Rev 7
    'A340-500':   (0, 21, 24),       # FAA TCDS A43NM Rev 7 & FDS Customer #47 A330/A340 Flight Controls
    'A340-600':   (0, 20, 23),       # FAA TCDS A43NM Rev 7
    'CRJ700':     (0, 20, 25),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    'CRJ900':     (0, 20, 25),       # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
####'Citation X': (0, Extd),         # Smart Cockpit Citation X Limitations Model 750; FIXME
}


SLAT_FAMILY_MAP = {
    'A310':       (0, 15, 20, 30),  # FAA TCDS A35EU Rev 26
    'A318':       (0, 18, 22, 27),  # FAA TCDS A28NM Rev 11
    'A319':       (0, 18, 22, 27),  # FAA TCDS A28NM Rev 11
    'A320':       (0, 18, 22, 27),  # FAA TCDS A28NM Rev 11
    'A321':       (0, 18, 22, 27),  # FAA TCDS A28NM Rev 11
    'A330':       (0, 16, 20, 23),  # Smart Cockpit A330 General Limitions Rev 19
    'A380':       (0, 20, 23),      # Smart Cockpit A380 Briefing For Pilots
    'B787':       (0, 50, 100),     # Boeing 787 Operations Manual
    'DC-9':       (0, 17.8, 21),    # FAA TCDS A6WE Rev 28 (DC-9-81 & DC-9-82)
    'ERJ190':     (0, 15, 25),      # FAA TCDS A57NM Rev 9 & Smart Cockpit Embraer_190 Flight Controls
####'Falcon':     (0, Extd),        # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME; Note: Extd: Inboard = 20, Median & Outboard = 35
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


AILERON_SERIES_MAP = {
    'A340-300': (0, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #125 A330/A340 Flight Controls
    'A340-500': (0, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #47  A330/A340 Flight Controls
    'A340-600': (0, 10),  # FIXME: Verify this is correct...
}


AILERON_FAMILY_MAP = {
    'A330': (0, 5, 10),   # Smart Cockpit A330 General Limitions Rev 19
    'A380': (0, 5, 10),   # Smart Cockpit A380 Briefing For Pilots
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
        '0':    (0, 0, 0),     # FAA TCDS A43NM Rev 7
        '1':    (20, 0, 0),    # FAA TCDS A43NM Rev 7 & FDS Customer #125 A330/A340 Flight Controls
        '1+F':  (20, 17, 10),  # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '1*':   (24, 17, 10),  # FAA TCDS A43NM Rev 7 (ECAM Indication = 2)
        '2':    (24, 22, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #125 A330/A340 Flight Controls
        '3':    (24, 26, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #125 A330/A340 Flight Controls
        'Full': (24, 32, 10),  # FAA TCDS A43NM Rev 7 & FDS Customer #125 A330/A340 Flight Controls
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
        '0':    (0, 0, 0),     # FAA TCDS A43NM Rev 7
        '1':    (20, 0, 0),    # FAA TCDS A43NM Rev 7
        '1+F':  (20, 17, 10),  # FAA TCDS A43NM Rev 7 (ECAM Indication = 1+F)
        '2':    (23, 22, 10),  # FAA TCDS A43NM Rev 7
        '3':    (23, 29, 10),  # FAA TCDS A43NM Rev 7
        'Full': (23, 34, 10),  # FAA TCDS A43NM Rev 7
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


LEVER_SERIES_MAP = {
    'CRJ700': {
        (0,  '0'):    (0, 0),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (1,  '1'):    (20, 0),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (8,  '8'):    (20, 8),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (20, '20'):   (20, 20),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (30, '30'):   (25, 30),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (45, '45'):   (25, 45),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    },
    'CRJ900': {
        (0,  '0'):    (0, 0),      # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (1,  '1'):    (20, 0),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (8,  '8'):    (20, 8),     # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (20, '20'):   (20, 20),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (30, '30'):   (25, 30),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
        (45, '45'):   (25, 45),    # FAA TCDS A21EA Rev 31 & Smart Cockpit CRJ-700/900 Flight Controls Rev 3
    },
}


LEVER_FAMILY_MAP = {
    'A310': {
        (0,  '0'):    (0, 0),      # FAA TCDS A35EU Rev 26
        (1,  '0+S'):  (15, 0),     # FAA TCDS A35EU Rev 26
        (15, '15'):   (15, 15),    # FAA TCDS A35EU Rev 26
        (20, '20'):   (20, 20),    # FAA TCDS A35EU Rev 26
        (40, '40'):   (30, 40),    # FAA TCDS A35EU Rev 26
    },
    'B787': {
        (0,  '0'):    (0, 0),      # FAA TCDS T00021SE Rev 6
        (1,  '1'):    (50, 0),     # FAA TCDS T00021SE Rev 6
        (5,  '5'):    (50, 5),     # FAA TCDS T00021SE Rev 6
        (15, '15'):   (50, 15),    # FAA TCDS T00021SE Rev 6
        (20, '20'):   (50, 20),    # FAA TCDS T00021SE Rev 6
        (25, '25'):   (100, 20),   # FAA TCDS T00021SE Rev 6
        (30, '30'):   (100, 30),   # FAA TCDS T00021SE Rev 6
    },
    'ERJ190': {
        (64, '0'):    (0, 0),      # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (32, '1'):    (15, 7),     # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (16, '2'):    (15, 10),    # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (8,  '3'):    (15, 20),    # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (4,  '4'):    (25, 20),    # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (2,  '5'):    (25, 20),    # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
        (1,  'Full'): (25, 37),    # Smart Cockpit Embraer 190 Flight Controls & FAA TCDS A57NM Rev 9
    },
####'Falcon': {
####    (0, '0'):     (0, 0),      # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME
####    (1, 'SF1'):   (Extd, 9),   # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME; Note: Extd: Inboard = 20, Median & Outboard = 35
####    (2, 'SF2'):   (Extd, 20),  # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME; Note: Extd: Inboard = 20, Median & Outboard = 35
####    (3, 'SF3'):   (Extd, 40),  # FAA TCDS A59NM Rev 1 & Smart Cockpit 7X Flight Controls Issue 2; FIXME; Note: Extd: Inboard = 20, Median & Outboard = 35
####},
    'Global': {
        (0,  '0'):    (0, 0),      # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (1,  '0+S'):  (20, 0),     # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (6,  '6'):    (20, 6),     # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (16, '16'):   (20, 16),    # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
        (30, '30'):   (20, 30),    # FAA TCDS T00003NY Rev 16 & Smart Cockpit Global 5000 Flight Controls
    },
}


#############################################################################
# Imports


import logging
import numpy as np

from itertools import chain, imap, izip

from flightdatautilities import sortext


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


#############################################################################
# Globals


logger = logging.getLogger(name=__name__)


#############################################################################
# Accessors


########################################
# Detents

# These functions return a sorted list of unique available detents for all
# aircraft models as defined in the mappings above.


def get_flap_detents():
    '''
    Get all flap combinations from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in FLAP_MODEL_MAP, FLAP_SERIES_MAP, FLAP_FAMILY_MAP:
        detents.update(chain.from_iterable(x.itervalues()))
    return sortext.nsorted(detents)


def get_slat_detents():
    '''
    Get all slat detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in SLAT_MODEL_MAP, SLAT_SERIES_MAP, SLAT_FAMILY_MAP:
        detents.update(chain.from_iterable(x.itervalues()))
    return sortext.nsorted(detents)


def get_aileron_detents():
    '''
    Get all aileron detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in AILERON_MODEL_MAP, AILERON_SERIES_MAP, AILERON_FAMILY_MAP:
        detents.update(chain.from_iterable(x.itervalues()))
    return sortext.nsorted(detents)


def get_conf_detents():
    '''
    Get all conf combinations from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    extract = dict.iterkeys
    detents = set()
    for x in CONF_MODEL_MAP, CONF_SERIES_MAP, CONF_FAMILY_MAP:
        detents.update(chain.from_iterable(imap(extract, x.itervalues())))
    return sortext.nsorted(detents)


def get_lever_detents():
    '''
    Get all lever detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    extract = lambda x: (v[1] for v in x.iterkeys())
    detents = set()
    for x in LEVER_MODEL_MAP, LEVER_SERIES_MAP, LEVER_FAMILY_MAP:
        detents.update(chain.from_iterable(imap(extract, x.itervalues())))
    return sortext.nsorted(detents)


########################################
# Values Mappings

# These functions return a dictionary with a mapping from values to states. The
# dictionaries returned are in a form that can be used as the values mappings
# for multi-state parameters.


def get_flap_map(model=None, series=None, family=None):
    '''
    Accessor for fetching flap mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: String
    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = FLAP_MODEL_MAP, FLAP_SERIES_MAP, FLAP_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No flap mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


def get_slat_map(model=None, series=None, family=None):
    '''
    Accessor for fetching slat mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: String
    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = SLAT_MODEL_MAP, SLAT_SERIES_MAP, SLAT_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No slat mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


def get_aileron_map(model=None, series=None, family=None):
    '''
    Accessor for fetching aileron mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: String
    :param series: Aircraft series e.g. A340-500
    :type series: String
    :param family: Aircraft family e.g. A340
    :type family: String
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = AILERON_MODEL_MAP, AILERON_SERIES_MAP, AILERON_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No aileron mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


def get_conf_map(model=None, series=None, family=None):
    '''
    Accessor for fetching conf mapping parameters.

    Returns a dictionary in the followng form::

        {value: state, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: String
    :param series: Aircraft series e.g. A340-500
    :type series: String
    :param family: Aircraft family e.g. A340
    :type family: String
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = CONF_MODEL_MAP, CONF_SERIES_MAP, CONF_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            return {x: v for x, v in AVAILABLE_CONF_STATES.items() if v in m[k]}

    message = "No conf mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


def get_lever_map(model=None, series=None, family=None):
    '''
    Accessor for fetching lever mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: String
    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = LEVER_MODEL_MAP, LEVER_SERIES_MAP, LEVER_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            return dict(m[k].iterkeys())

    # Fallback to using the flap mapping if no lever mapping:
    try:
        return get_flap_map(model, series, family)
    except KeyError:
        pass  # fall through to display message defined below...

    message = "No lever mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


########################################
# Angle Mappings

# These functions return a dictionary of some preferred lookup key (multi-state
# raw value or state name) to a tuple of angles of component surfaces which can
# be (slat, flap) or (slat, flap, aileron) depending on what is available. The
# output from these functions can used to help derive multi-states from raw
# surface values.


def get_conf_angles(model=None, series=None, family=None, key='state'):
    '''
    Accessor for fetching conf mapping parameters.

    Returns a dictionary in one of the followng forms::

        {state: (slat, flap), ...}
        {state: (slat, flap, aileron), ...}
        {value: (slat, flap), ...}
        {value: (slat, flap, aileron), ...}
        {(value, state): (slat, flap), ...}
        {(value, state): (slat, flap, aileron), ...}

    :param model: Aircraft series e.g. A340-555
    :type model: String
    :param series: Aircraft series e.g. A340-500
    :type series: String
    :param family: Aircraft family e.g. A340
    :type family: String
    :param key: Key to be provided in the mapping (both, state or value)
    :type key: str
    :raises: KeyError if no mapping found
    :returns: mapping of detent and/or state to surface angle values
    :rtype: dict
    '''
    if key not in ('both', 'state', 'value'):
        raise ValueError("Lookup key must be 'both', 'state' or 'value'.")

    keys = model, series, family
    maps = CONF_MODEL_MAP, CONF_SERIES_MAP, CONF_FAMILY_MAP
    available = AVAILABLE_CONF_STATES.items()

    for k, m in izip(keys, maps):
        if k not in m:
            continue
        if key == 'both':
            return {(x, v): m[k][v] for x, v in available if v in m[k]}
        if key == 'state':
            return m[k]
        if key == 'value':
            return {x: m[k][v] for x, v in available if v in m[k]}

    message = "No conf angles for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))


def get_lever_angles(model=None, series=None, family=None, key='state'):
    '''
    Accessor for fetching conf mapping parameters.

    Returns a dictionary in one of the followng forms::

        {state: (slat, flap), ...}
        {value: (slat, flap), ...}
        {(value, state): (slat, flap), ...}

    :param model: Aircraft series e.g. B737-333
    :type model: String
    :param series: Aircraft series e.g. B737-300
    :type series: String
    :param family: Aircraft family e.g. B737
    :type family: String
    :param key: Key to be provided in the mapping (both, state or value)
    :type key: str
    :raises: KeyError if no mapping found
    :returns: mapping of detent and/or state to surface angle values
    :rtype: dict
    '''
    if key not in ('both', 'state', 'value'):
        raise ValueError("Lookup key must be 'both', 'state' or 'value'.")

    keys = model, series, family
    maps = LEVER_MODEL_MAP, LEVER_SERIES_MAP, LEVER_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k not in m:
            continue
        if key == 'both':
            return m[k]
        if key == 'state':
            return {x[1]: v for x, v in m[k].iteritems()}
        if key == 'value':
            return {x[0]: v for x, v in m[k].iteritems()}

    message = "No lever angles for model '%s', series '%s', family '%s'."
    raise KeyError(message % (model, series, family))
