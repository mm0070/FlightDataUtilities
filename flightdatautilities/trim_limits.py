'''
Trim limits
'''

STABILIZER_LIMITS_FAMILIES = {
    'B737-600': [2.25, 8.6],
    'B737-700': [2.65, 8.5],
    'B737-800': [2.05, 8.5],
    'CRJ 900': [3.6, 11.5],
}


def get_stabilizer_limits(aircraft_family):
    if aircraft_family in STABILIZER_LIMITS_FAMILIES:
        return STABILIZER_LIMITS_FAMILIES[aircraft_family]
