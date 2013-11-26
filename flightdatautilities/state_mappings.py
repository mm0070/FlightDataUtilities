# -*- coding: utf-8 -*-
##############################################################################

'''
Multi-state Parameter State Value Mappings
'''

##############################################################################
# Import


import re

from fnmatch import translate


##############################################################################
# Constants


PARAMETER_CORRECTIONS = {
    'AP Engaged': {1: 'Engaged'},
    'AT Engaged': {1: 'Engaged'},
    'Alpha Floor': {1: 'Engaged'},
    'Alternate Law': {1: 'Engaged'},
    'Autobrake Selected RTO': {1: 'Selected'},
    'Cabin Altitude': {1: 'Warning'},
    'Direct Law': {1: 'Engaged'},
    'ECS Pack (*) High Flow': {1: 'High', 0: 'Low'},
    'ECS Pack (*) On': {1: 'On'},
    'Eng (*) Anti Ice': {1: 'On'},
    'Eng (*) Bleed': {1: 'Open', 0: 'Closed'},
    'Eng (*) Fire': {1: 'Fire'},
    'Eng (*) Thrust Reverser Deployed': {1: 'Deployed'},
    'Eng (*) Thrust Reverser In Transit': {1: 'In Transit'},
    'Eng (*) Thrust Reverser Unlocked': {1: 'Unlocked'},
    'Event Marker': {1: 'Event'},
    'Flap Load Relief': {0: 'Normal', 1: 'Load Relief'},
    'Flap Alternate Armed': {1: 'Armed'},  # FIXME: Add {0: 'Not Armed'}?
    'Slat Alternate Armed': {1: 'Armed'},  # FIXME: Add {0: 'Not Armed'}?
    'Gear (*) Down': {1: 'Down', 0: 'Up'},
    'Gear (*) In Air': {1: 'Air', 0: 'Ground'},
    'Gear (*) On Ground': {1: 'Ground', 0: 'Air'},
    'Gear (*) Red Warning': {1: 'Warning'},
    'Gear Down Selected': {1: 'Down', 0: 'Up'},
    'Gear Down': {1: 'Down', 0: 'Up'},
    'Gear In Air': {1: 'Air', 0: 'Ground'},
    'Gear On Ground': {1: 'Ground', 0: 'Air'},
    'Gear Up Selected': {1: 'Up', 0: 'Down'},
    'Jettison Nozzle': {1: 'Jettison'},
    'Key HF (*)': {1: 'Keyed'},
    'Key Satcom (*)': {1: 'Keyed'},
    'Key VHF (*)': {1: 'Keyed'},
    'Landing Configuration Gear Warning': {1: 'Warning'},
    'Landing Configuration Speedbrake Caution': {1: 'Caution'},
    'Master Caution': {1: 'Caution'},
    'Master Warning': {1: 'Warning'},
    'Normal Law': {1: 'Engaged'},
    'Overspeed Warning': {1: 'Overspeed'},
    'Pitch Alternate Law (*)': {1: 'Engaged'},
    'Pitch Alternate Law': {1: 'Engaged'},
    'Pitch Direct Law': {1: 'Engaged'},
    'Pitch Normal Law': {1: 'Engaged'},
    'Roll Alternate Law': {1: 'Engaged'},
    'Roll Direct Law': {1: 'Engaged'},
    'Roll Normal Law': {1: 'Engaged'},
    'Speedbrake Armed': {1: 'Armed'},
    'Speedbrake Deployed': {1: 'Deployed'},
    'Stick Shaker (*)': {1: 'Shake'},
    'TAWS Alert': {1: 'Alert'},
    'TAWS Caution Obstacle': {1: 'Caution'},
    'TAWS Caution Terrain': {1: 'Caution'},
    'TAWS Caution': {1: 'Caution'},
    'TAWS Dont Sink': {1: 'Warning'},
    'TAWS Failure': {1: 'Failed'},
    'TAWS Glideslope': {1: 'Warning'},
    'TAWS Obstacle Warning': {1: 'Warning'},
    'TAWS Pull Up': {1: 'Warning'},
    'TAWS Sink Rate': {1: 'Warning'},
    'TAWS Terrain Caution': {1: 'Caution'},
    'TAWS Terrain Pull Up Ahead': {1: 'Warning'},
    'TAWS Terrain Pull Up': {1: 'Warning'},
####'TAWS Terrain Warning Amber': {},
####'TAWS Terrain Warning Red': {},
    'TAWS Terrain': {1: 'Warning'},
    'TAWS Too Low Flap': {1: 'Warning'},
    'TAWS Too Low Gear': {1: 'Warning'},
    'TAWS Too Low Terrain': {1: 'Warning'},
    'TAWS Warning': {1: 'Warning'},
    'TAWS Windshear Caution': {1: 'Caution'},
    'TAWS Windshear Siren': {1: 'Siren'},
    'TAWS Windshear Warning': {1: 'Warning'},
    'TCAS Failure': {1: 'Failed'},
    'Takeoff And Go Around': {1: 'TOGA'},
    'Takeoff Configuration Flap Warning': {1: 'Warning'},
    'Takeoff Configuration Parking Brake Warning': {1: 'Warning'},
    'Takeoff Configuration Spoiler Warning': {1: 'Warning'},
    'Takeoff Configuration Stabilizer Warning': {1: 'Warning'},
    'Takeoff Configuration Warning': {1: 'Warning'},
    'Wing Anti Ice': {1: 'On'},
}

STATE_CORRECTIONS = {
    'Not Closed': 'Open',
    'Down Lock': 'Down',
    'Openned': 'Open',
    'Not engaged': 'Not Engaged',
    'on': 'On',
    'off': 'Off',
    'Not armed': 'Not Armed',
    'APU Bleed Valve Fully Open': 'Open',
    'APU Bleed Valve not Fully Open': 'Closed',
    'no Fault': None,
    'false': 'False',
    'true': 'True',
    'valid': 'Valid',
    'not valid': 'Invalid',
}

# Examples where states conflict:
# * VMO/MMO Selected

TRUE_STATES = [
    'Engaged',
    'on',
    'CMD Mode',
    'CWS Mode',
    '1',
    'Open',  # ?
    'FMA Displayed',
    'Event',  # ?
    'Asymmetrical',
    'Ground',  # ? Landing Squat Switch (L/N/R), Gear (L) On Ground
    'Down',  # ? Gear (L/R/N) Down
    'GOOD',
    'Warning',
    'Keyed',
    'Track Phase',
    'Selected',
    'Deployed',
    'Unlocked',
    'AC BUS 2 OFF',
    'APU Bleed Valve not Fully Open',  # APU Bleed Valve Not Open
    'Not armed',  # ? ATS Arming Lever Off
    'APU Fire',
    'Aft CG',
    'Fault',
    'Valid',
]


FALSE_STATES = [
    'Not Engaged',
    'off',
    'Not in CMD Mode',
    'Not in CWS Mode',
    '0',
    'Closed',  # ?
    'FMA Not Displayed',
    'Air',  # ? Landing Squat Switch (L/N/R)
    'Up',  # ? Gear (L/R/N) Down
    'FAIL/OFF',  # Slat Assymetrical
    'AC BUS 2 not OFF',
    'APU Bleed Valve Fully Open',  # APU Bleed Valve Not Open
    'Armed',  # ? ATS Arming Lever Off
    'No APU Fire',
    'No Aft CG',
    'Normal',
    'No Warning',
    'no Fault',
    'Invalid',
]


##############################################################################
# Functions


def get_parameter_correction(parameter_name):

    if parameter_name in PARAMETER_CORRECTIONS:
        return PARAMETER_CORRECTIONS[parameter_name]

    for pattern, mapping in PARAMETER_CORRECTIONS.items():
        if '(*)' in pattern or '(?)' in pattern:
            regex = translate(pattern)
            re_obj = re.compile('^' + regex + '$')
            matched = re_obj.match(parameter_name)
            if matched:
                return mapping


def normalise_discrete_mapping(original_mapping, parameter_name=None):

    true_state = original_mapping[1]
    false_state = original_mapping[0]

    true_state = STATE_CORRECTIONS.get(true_state, true_state)
    false_state = STATE_CORRECTIONS.get(false_state, false_state)

    inverted = true_state in FALSE_STATES or false_state in TRUE_STATES

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {0: false_state, 1: true_state}

    return normalised_mapping, inverted


def normalise_multistate_mapping(original_mapping, parameter_name=None):

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {}

        for value, state in original_mapping.items():
            normalised_mapping[value] = STATE_CORRECTIONS.get(state, state)

    return normalised_mapping
