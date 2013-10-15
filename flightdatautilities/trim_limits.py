'''
Trim limits
'''

STABILIZER_LIMITS_FAMILIES = {
    'CRJ 900': [3.6, 11.5],
}

STABILIZER_LIMITS_SERIES = {
    'B737-600': [2.25, 8.6],
    'B737-700': [2.65, 8.5],
    'B737-800': [2.05, 8.5],
}


def get_stabilizer_limits(aircraft_family=None, aircraft_series=None):
    if aircraft_family in STABILIZER_LIMITS_FAMILIES:
        return STABILIZER_LIMITS_FAMILIES[aircraft_family]
    elif aircraft_series in STABILIZER_LIMITS_SERIES:
        return STABILIZER_LIMITS_SERIES[aircraft_series]
