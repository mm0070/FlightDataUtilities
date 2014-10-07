# -*- coding: utf-8 -*-
##############################################################################

'''
Multi-state Parameter State Value Mappings
'''

##############################################################################
# Import


import re

from flightdatautilities.patterns import wildcard_match


##############################################################################
# Constants


PARAMETER_CORRECTIONS = {
    'AP (*) Engaged': {1: 'Engaged'},
    'APU (*) On': {1: 'On'},
    'APU Bleed Valve Open': {1: 'Open'},
    'APU Fire': {1: 'Fire'},
    'AT Active': {1: 'Activated'},
    'Alpha Floor': {1: 'Engaged'},
    'Alternate Law': {1: 'Engaged'},
    'Altitude Capture Mode': {1: 'Activated'},
    'Altitude Mode': {1: 'Activated'},
    'Autobrake Selected RTO': {1: 'Selected'},
    'Cabin Altitude Warning': {1: 'Warning'},
    'Climb Mode Active': {1: 'Activated'},
    'Direct Law': {1: 'Engaged'},
    'ECS Pack (*) High Flow': {0: 'Low', 1: 'High'},
    'ECS Pack (*) On': {1: 'On'},
    'Eng (*) Anti Ice': {1: 'On'},
    'Eng (*) Bleed': {0: 'Closed', 1: 'Open'},
    'Eng (*) Fire (1L)': {1: 'Fire'},
    'Eng (*) Fire (1R)': {1: 'Fire'},
    'Eng (*) Fire (2L)': {1: 'Fire'},
    'Eng (*) Fire (2R)': {1: 'Fire'},
    'Eng (*) Fire': {1: 'Fire'},
    'Eng (*) Oil Press Low': {1: 'Low Press'},
    'Eng (*) Thrust Reverser (*) Deployed': {1: 'Deployed'},
    'Eng (*) Thrust Reverser (*) In Transit': {1: 'In Transit'},
    'Eng (*) Thrust Reverser (*) Unlocked': {1: 'Unlocked'},
    'Event Marker (*)': {1: 'Event'},
    'Event Marker (Capt)': {1: 'Event'},
    'Event Marker (FO)': {1: 'Event'},
    'Event Marker': {1: 'Event'},
    'Expedite Climb Mode': {1: 'Activated'},
    'Expedite Descent Mode': {1: 'Activated'},
    'Fire APU Dual Bottle System': {1: 'Fire'},
    'Fire APU Single Bottle System': {1: 'Fire'},
    'Flap Alternate Armed': {1: 'Armed'},
    'Flap Load Relief': {0: 'Normal', 1: 'Load Relief'},
    'Flare Mode': {1: 'Engaged'},
    'Fuel Jettison Nozzle': {1: 'Disagree'},
    'Fuel Qty (L) Low': {1: 'Warning'},
    'Fuel Qty (R) Low': {1: 'Warning'},
    'Fuel Qty Low': {1: 'Warning'},
    'Gear (*) Down': {0: 'Up', 1: 'Down'},
    'Gear (*) In Air': {0: 'Ground', 1: 'Air'},
    'Gear (*) In Transit': {1: 'In Transit'},
    'Gear (*) On Ground': {0: 'Air', 1: 'Ground'},
    'Gear (*) Red Warning': {1: 'Warning'},
    'Gear (*) Up': {0: 'Down', 1: 'Up'},
    'Gear Down Selected': {0: 'Up', 1: 'Down'},
    'Gear Up Selected': {0: 'Down', 1: 'Up'},
    'Heading Mode Active': {1: 'Activated'},
    'ILS Glideslope Capture Active': {1: 'Activated'},
    'ILS Inner Marker (*)': {1: 'Present'},
    'ILS Localizer Capture Active': {1: 'Activated'},
    'ILS Localizer Track Active': {1: 'Activated'},
    'ILS Middle Marker (*)': {1: 'Present'},
    'ILS Outer Marker (*)': {1: 'Present'},
    'Jettison Nozzle': {1: 'Jettison'},
    'Key HF (*)': {1: 'Keyed'},
    'Key Satcom (*)': {1: 'Keyed'},
    'Key VHF (*) (*)': {1: 'Keyed'},
    'Land Track Activated': {1: 'Activated'},
    'Landing Configuration Gear Warning': {1: 'Warning'},
    'Landing Configuration Speedbrake Caution': {1: 'Caution'},
    'Master Caution (*)': {1: 'Caution'},
    'Master Warning (*)': {1: 'Warning'},
    'NAV Mode Active': {1: 'Activated'},
    'Normal Law': {1: 'Engaged'},
    'Open Climb Mode': {1: 'Activated'},
    'Open Descent Mode': {1: 'Activated'},
    'Overspeed Warning': {1: 'Overspeed'},
    'Pitch Alternate Law (*)': {1: 'Engaged'},
    'Pitch Direct Law': {1: 'Engaged'},
    'Pitch Normal Law': {1: 'Engaged'},
    'Roll Alternate Law': {1: 'Engaged'},
    'Roll Direct Law': {1: 'Engaged'},
    'Roll Go Around Mode Active': {1: 'Activated'},
    'Roll Normal Law': {1: 'Engaged'},
    'Runway Mode Active': {1: 'Activated'},
    'Slat Alternate Armed': {1: 'Armed'},
    'Speed Control (*) Auto': {1: 'Auto'},
    'Speed Control (*) Manual': {0: 'Auto'},
    'Speedbrake Armed': {1: 'Armed'},
    'Speedbrake Deployed': {1: 'Deployed'},
    'Spoiler (*) Deployed': {1: 'Deployed'},
    'Spoiler (*) Outboard Deployed': {1: 'Deployed'},
    'Stick Pusher (*)': {1: 'Push'},
    'Stick Shaker (*)': {1: 'Shake'},
    'TAWS (*) Dont Sink': {1: 'Warning'},
    'TAWS (*) Glideslope Cancel': {1: 'Cancel'},
    'TAWS (*) Too Low Gear': {1: 'Warning'},
    'TAWS Alert': {1: 'Alert'},
    'TAWS Caution Obstacle': {1: 'Caution'},
    'TAWS Caution Terrain': {1: 'Caution'},
    'TAWS Caution': {1: 'Caution'},
    'TAWS Failure': {1: 'Failed'},
    'TAWS Glideslope': {1: 'Warning'},
    'TAWS Minimums': {1: 'Minimums'},
    'TAWS Obstacle Warning': {1: 'Warning'},
    'TAWS Predictive Windshear': {1: 'Warning'},
    'TAWS Pull Up': {1: 'Warning'},
    'TAWS Sink Rate': {1: 'Warning'},
    'TAWS Terrain Ahead Pull Up': {1: 'Warning'},
    'TAWS Terrain Ahead': {1: 'Warning'},
    'TAWS Terrain Caution': {1: 'Caution'},
    'TAWS Terrain Override': {1: 'Override'},
    'TAWS Terrain Pull Up': {1: 'Warning'},
    'TAWS Terrain Warning Amber': {1: 'Warning'},
    'TAWS Terrain Warning Red': {1: 'Warning'},
    'TAWS Terrain': {1: 'Warning'},
    'TAWS Too Low Flap': {1: 'Warning'},
    'TAWS Too Low Terrain': {1: 'Warning'},
    'TAWS Warning': {1: 'Warning'},
    'TAWS Windshear Caution': {1: 'Caution'},
    'TAWS Windshear Siren': {1: 'Siren'},
    'TAWS Windshear Warning': {1: 'Warning'},
    'TCAS (*) Failure': {1: 'Failed'},
    'TCAS RA': {1: 'RA'},
    'TCAS TA': {1: 'TA'},
    'Takeoff And Go Around': {1: 'TOGA'},
    'Takeoff Configuration AP Warning': {1: 'Warning'},
    'Takeoff Configuration Aileron Warning': {1: 'Warning'},
    'Takeoff Configuration Flap Warning': {1: 'Warning'},
    'Takeoff Configuration Gear Warning': {1: 'Warning'},
    'Takeoff Configuration Parking Brake Warning': {1: 'Warning'},
    'Takeoff Configuration Rudder Warning': {1: 'Warning'},
    'Takeoff Configuration Spoiler Warning': {1: 'Warning'},
    'Takeoff Configuration Stabilizer Warning': {1: 'Warning'},
    'Takeoff Configuration Warning': {1: 'Warning'},
    'Thrust Mode Selected (*)': {1: 'Selected'},
    'Wing Anti Ice': {1: 'On'},
}


STATE_CORRECTIONS = {
    'APU Bleed Valve Fully Open': 'Open',
    'APU Bleed Valve not Fully Open': 'Closed',
    'DOWN': 'Down',
    'Down Lock': 'Down',
    'Not Closed': 'Open',
    'Not Open': 'Closed',
    'Not armed': 'Not Armed',
    'Not engaged': 'Not Engaged',
    'Openned': 'Open',
    'UP': 'Up',
    'down': 'Down',
    'false': 'False',
    'no Fault': None,
    'not valid': 'Invalid',
    'off': 'Off',
    'on': 'On',
    'true': 'True',
    'up': 'Up',
    'valid': 'Valid',
}


TRUE_STATES = [
    'APU Bleed Valve not Fully Open',
    'APU Fire',
    'Aft CG',
    'Air',
    'Asymmetrical',
    'CMD Mode',
    'CWS Mode',
    'Deployed',
    'Down',
    'Engaged',
    'Event',
    'FMA Displayed',
    'Fault',
    'Good',
    'Ground',
    'Keyed',
    'Not Armed',
    'On',
    'Open',
    'Selected',
    'Track Phase',
    'Unlocked',
    'Valid',
    'Warning',
]


FALSE_STATES = [
    'APU Bleed Valve Fully Open',
    'Air',
    'Armed',
    'Closed',
    'FMA Not Displayed',
    'Ground',
    'Invalid',
    'No APU Fire',
    'No Aft CG',
    'No Event',
    'No Fault',
    'No Warning',
    'Normal',
    'Not Deployed',
    'Not Engaged',
    'Not Keyed',
    'Not in CMD Mode',
    'Not in CWS Mode',
    'Off',
    'Up',
]


# Examples where states conflict:
# * VMO/MMO Selected


##############################################################################
# Functions


def get_parameter_correction(parameter_name):

    if parameter_name in PARAMETER_CORRECTIONS:
        return PARAMETER_CORRECTIONS[parameter_name]

    for pattern, mapping in PARAMETER_CORRECTIONS.items():
        if wildcard_match(pattern, [parameter_name]):
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
