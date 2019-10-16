##############################################################################

'''
'''

#############################################################################
# Imports

import itertools

from natsort import natsorted

from flightdatautilities.aircrafttables import constants

# Note: These are overridden as part of the aircraft table configuration!
from flightdatautilities.aircrafttables import model_information as mi
from flightdatautilities.aircrafttables import velocity_speed as vs
from flightdatautilities.aircrafttables import engine_thresholds as et


#############################################################################
# Exports


__all__ = (
    'get_aileron_detents', 'get_aileron_map',
    'get_conf_detents', 'get_conf_map', 'get_conf_angles',
    'get_flap_detents', 'get_flap_map',
    'get_lever_detents', 'get_lever_map', 'get_lever_angles',
    'get_slat_detents', 'get_slat_map',
    'get_stabilizer_limits',
    'get_kaf_map', 'get_vls1g_map',
    'get_fms_map',
    'get_vspeed_map',
    'get_engine_map',
    'get_aileron_range',
    'get_elevator_range',
    'get_rudder_range',
    'get_control_column_range',
    'get_control_wheel_range',
    'get_cyclic_fore_aft_range',
    'get_cyclic_lateral_range',
    'get_eng_epr_range',
    'get_eng_fuel_flow_range',
    'get_eng_gas_temp_range',
    'get_rudder_pedal_range',
    'get_sidestick_pitch_range',
    'get_sidestick_roll_range',
    'get_tail_rotor_pedal_range',
    'get_throttle_lever_range',
    'get_gear_transition_times',
)


#############################################################################
# Model Information Accessors


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
    for x in mi.FLAP_MODEL_MAP, mi.FLAP_SERIES_MAP, mi.FLAP_FAMILY_MAP:
        detents.update(itertools.chain.from_iterable(x.values()))
    return natsorted(detents)


def get_slat_detents():
    '''
    Get all slat detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in mi.SLAT_MODEL_MAP, mi.SLAT_SERIES_MAP, mi.SLAT_FAMILY_MAP:
        detents.update(itertools.chain.from_iterable(x.values()))
    return natsorted(detents)


def get_aileron_detents():
    '''
    Get all aileron detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in mi.AILERON_MODEL_MAP, mi.AILERON_SERIES_MAP, mi.AILERON_FAMILY_MAP:
        detents.update(itertools.chain.from_iterable(x.values()))
    return natsorted(detents)


def get_conf_detents():
    '''
    Get all conf combinations from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP:
        detents.update(itertools.chain.from_iterable(v.keys() for v in x.values()))
    return natsorted(detents)


def get_lever_detents():
    '''
    Get all lever detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set(map(str, get_flap_detents()))  # initialise with flap detents
    for x in mi.LEVER_MODEL_MAP, mi.LEVER_SERIES_MAP, mi.LEVER_FAMILY_MAP:
        detents.update(itertools.chain.from_iterable(k[1] for v in x.values() for k in v.keys()))
    detents.update(constants.LEVER_STATES.values())  # include conf lever states
    return natsorted(detents)


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
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.FLAP_MODEL_MAP, mi.FLAP_SERIES_MAP, mi.FLAP_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No flap mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_slat_map(model=None, series=None, family=None):
    '''
    Accessor for fetching slat mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.SLAT_MODEL_MAP, mi.SLAT_SERIES_MAP, mi.SLAT_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No slat mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_aileron_map(model=None, series=None, family=None):
    '''
    Accessor for fetching aileron mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.AILERON_MODEL_MAP, mi.AILERON_SERIES_MAP, mi.AILERON_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No aileron mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_conf_map(model=None, series=None, family=None, manufacturer='Airbus'):
    '''
    Accessor for fetching conf mapping parameters.

    Returns a dictionary in the followng form::

        {value: state, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
    :type family: string
    :param manufacturer: Aircraft manufacturer e.g. Airbus
    :type manufacturer: string
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP
    conf = constants.AVAILABLE_CONF_STATES.get(manufacturer, {}).items()

    for k, m in zip(keys, maps):
        if k in m:
            return {x: v for x, v in conf if v in m[k]}

    message = "No conf mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_lever_map(model=None, series=None, family=None):
    '''
    Accessor for fetching lever mapping parameters.

    Returns a dictionary in the following form::

        {value: state, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.LEVER_MODEL_MAP, mi.LEVER_SERIES_MAP, mi.LEVER_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return dict(m[k].keys())

    # Fallback to using the flap mapping if no lever mapping:
    try:
        return get_flap_map(model, series, family)
    except KeyError:
        pass  # fall through to display message defined below...

    message = "No lever mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


########################################
# Angle Mappings

# These functions return a dictionary of some preferred lookup key (multi-state
# raw value or state name) to a tuple of angles of component surfaces which can
# be (slat, flap) or (slat, flap, aileron) depending on what is available. The
# output from these functions can used to help derive multi-states from raw
# surface values.


def get_conf_angles(model=None, series=None, family=None, manufacturer='Airbus', key='state'):
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
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
    :type family: string
    :param manufacturer: Aircraft manufacturer e.g. Airbus
    :type manufacturer: string
    :param key: Key to be provided in the mapping (both, state or value)
    :type key: str
    :raises: KeyError if no mapping found
    :returns: mapping of detent and/or state to surface angle values
    :rtype: dict
    '''
    if key not in ('both', 'state', 'value'):
        raise ValueError("Lookup key must be 'both', 'state' or 'value'.")

    keys = model, series, family
    maps = mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP
    conf = constants.AVAILABLE_CONF_STATES.get(manufacturer, {}).items()

    for k, m in zip(keys, maps):
        if k not in m:
            continue
        if key == 'both':
            return {(x, v): m[k][v] for x, v in conf if v in m[k]}
        if key == 'state':
            return m[k]
        if key == 'value':
            return {x: m[k][v] for x, v in conf if v in m[k]}

    message = "No conf angles for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_lever_angles(model=None, series=None, family=None, key='state'):
    '''
    Accessor for fetching lever mapping parameters.

    Returns a dictionary in one of the followng forms::

        {state: (slat, flap), ...}
        {value: (slat, flap), ...}
        {state: (slat, flap, aileron), ...}
        {(value, state): (slat, flap), ...}

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :param key: Key to be provided in the mapping (both, state or value)
    :type key: str
    :raises: KeyError if no mapping found
    :returns: mapping of detent and/or state to surface angle values
    :rtype: dict
    '''
    if key not in ('both', 'state', 'value'):
        raise ValueError("Lookup key must be 'both', 'state' or 'value'.")

    keys = model, series, family
    maps = mi.LEVER_MODEL_MAP, mi.LEVER_SERIES_MAP, mi.LEVER_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k not in m:
            continue
        d = m[k]
        if key == 'both':
            return d
        if key == 'state':
            return {x[1]: v for x, v in d.items()}
        if key == 'value':
            return {x[0]: v for x, v in d.items()}

    # Fallback to using the flap mapping if no lever mapping:
    try:
        both = get_flap_map(model, series, family).items()
        values, states = zip(*both)
        #             None slat            flap     None flaperon
        angles = zip([None] * len(values), values, [None] * len(values))
    except KeyError:
        pass  # fall through to display message defined below...
    else:
        if key == 'both':
            return dict(zip(both, angles))
        if key == 'state':
            return dict(zip(states, angles))
        if key == 'value':
            return dict(zip(values, angles))

    message = "No lever angles for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


########################################
# Stabilizer Limit Mappings


def get_stabilizer_limits(model=None, series=None, family=None):
    '''
    Accessor for fetching stabilizer limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of stabilizer angle limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.STABILIZER_MODEL_MAP, mi.STABILIZER_SERIES_MAP, mi.STABILIZER_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No stabilizer limits for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


########################################
# Airbrake Coefficient Mappings


def get_kaf_map(model=None, series=None, family=None):
    '''
    Accessor for fetching airbrake coefficients.

    Returns a dictionary in the following form::

        {state: value, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of state to airbrake coefficient values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.KAF_MODEL_MAP, mi.KAF_SERIES_MAP, mi.KAF_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No airbrake coefficients for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


########################################
# VLS1g Mappings


def get_vls1g_map(model=None, series=None, family=None, engine_manufacturer=None):
    '''
    Accessor for fetching VLS1g constants.

    Returns a dictionary in the following form::

        {state: value, ...}

    :param model: Aircraft series e.g. A340-555
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of state to VLS1g constant values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.VLS1G_MODEL_MAP, mi.VLS1G_SERIES_MAP, mi.VLS1G_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m and engine_manufacturer in m[k]:
            return m[k][engine_manufacturer]

    message = "No VLS1g constant for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


########################################
# Flap Manoeuvring Speed Mappings


def get_fms_map(model=None, series=None, family=None):
    '''
    Accessor for fetching flap manoeuvring speed tables.

    Returns a dictionary in the following form::

        {state: value, ...}

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :raises: KeyError if no mapping found
    :returns: mapping of state to flap manoeuvring speed parameters
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.FMS_MODEL_MAP, mi.FMS_SERIES_MAP, mi.FMS_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No flap manoeuvring speed table for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


##############################################################################
# Velocity Speed Accessors


def get_vspeed_map(model=None, series=None, family=None, engine_type=None, engine_series=None):
    '''
    Accessor for fetching velocity speed tables for V2/Vref/Vapp.

    Returns a class of VelocitySpeed that can be instantiated.

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :param engine_type: Engine type e.g. CFM56-3B1
    :type engine_type: string
    :param engine_series: Engine series e.g. CFM56-3
    :type engine_series: string
    :raises: KeyError if no table is found
    :returns: lookup class for velocity speeds.
    :rtype: VelocitySpeed
    '''
    keys = model, series, family
    maps = vs.VSPEED_MODEL_MAP, vs.VSPEED_SERIES_MAP, vs.VSPEED_FAMILY_MAP

    # Create an iterator that so that we can look up in the correct order:
    #
    # - aircraft model, engine type.
    # - aircraft series, engine type.
    # - aircraft family, engine type.
    # - aircraft model, engine series.
    # - aircraft series, engine series.
    # - aircraft family, engine series.
    # - aircraft model.
    # - aircraft series.
    # - aircraft family.
    engines = engine_type, engine_series, None
    it = zip(map(lambda x: x[::-1], itertools.product(engines, keys)), itertools.cycle(maps))

    for k, m in it:
        if k in m:
            return m[k]

    message = "No velocity speed table for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_engine_map(engine_type=None, engine_series=None, mods=None, restriction=None):
    '''
    Accessor for fetching engine threshold tables for Torque/N1/NP/Gas Temp.

    Returns a class of VelocitySpeed that can be instantiated.

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :param engine_type: Engine type e.g. CFM56-3B1
    :type engine_type: string
    :param engine_series: Engine series e.g. CFM56-3
    :type engine_series: string
    :raises: KeyError if no table is found
    :returns: lookup class for velocity speeds.
    :rtype: VelocitySpeed
    '''
    series_map = et.SINGLE_ENGINE_SERIES_MAP if restriction == 'single' else et.ENGINE_SERIES_MAP
    keys = engine_series, engine_type

    # Create an iterator that so that we can look up in the correct order:
    #
    # - aircraft model, engine type.
    # - aircraft series, engine type.
    # - aircraft family, engine type.
    # - aircraft model, engine series.
    # - aircraft series, engine series.
    # - aircraft family, engine series.
    # - aircraft model.
    # - aircraft series.
    # - aircraft family.
    mod_keys = mods if mods else []
    it = zip(map(lambda x: x[::-1], itertools.product(mod_keys + [None], keys)), itertools.cycle([series_map]))

    for k, m in it:
        if k in m:
            return m[k]

    message = "No engine threshods for  '%s', series '%s', family '%s' mods."
    raise KeyError(message % (engine_series, engine_type, mods))


########################################
# Flight Control Mappings

def get_aileron_range(model=None, series=None, family=None):
    '''
    Accessor for fetching stabilizer limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of stabilizer angle limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.AILERON_RANGE_MODEL_MAP, mi.AILERON_RANGE_SERIES_MAP, mi.AILERON_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Aileron range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_elevator_range(model=None, series=None, family=None):
    '''
    Accessor for fetching stabilizer limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of stabilizer angle limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.ELEVATOR_RANGE_MODEL_MAP, mi.ELEVATOR_RANGE_SERIES_MAP, mi.ELEVATOR_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Elevator range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_rudder_range(model=None, series=None, family=None):
    '''
    Accessor for fetching stabilizer limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of stabilizer angle limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.RUDDER_RANGE_MODEL_MAP, mi.RUDDER_RANGE_SERIES_MAP, mi.RUDDER_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Rudder range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_control_column_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Control Column limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.CONTROL_COLUMN_RANGE_MODEL_MAP, mi.CONTROL_COLUMN_RANGE_SERIES_MAP, mi.CONTROL_COLUMN_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Control Column range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_control_wheel_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Control Wheel limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.CONTROL_WHEEL_RANGE_MODEL_MAP, mi.CONTROL_WHEEL_RANGE_SERIES_MAP, mi.CONTROL_WHEEL_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Control Wheel range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_cyclic_fore_aft_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Cyclic Fore-Aft limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.CYCLIC_FORE_AFT_RANGE_MODEL_MAP, mi.CYCLIC_FORE_AFT_RANGE_SERIES_MAP, mi.CYCLIC_FORE_AFT_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Cyclic Fore-Aft range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_cyclic_lateral_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Cyclic Lateral limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.CYCLIC_LATERAL_RANGE_MODEL_MAP, mi.CYCLIC_LATERAL_RANGE_SERIES_MAP, mi.CYCLIC_LATERAL_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Cyclic Lateral range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_eng_epr_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Eng EPR limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.ENG_EPR_RANGE_MODEL_MAP, mi.ENG_EPR_RANGE_SERIES_MAP, mi.ENG_EPR_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Eng EPR range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_eng_fuel_flow_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Eng Fuel Flow limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.ENG_FUEL_FLOW_RANGE_MODEL_MAP, mi.ENG_FUEL_FLOW_RANGE_SERIES_MAP, mi.ENG_FUEL_FLOW_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Eng Fuel Flow range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_eng_gas_temp_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Eng Gas Temp limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.ENG_GAS_TEMP_RANGE_MODEL_MAP, mi.ENG_GAS_TEMP_RANGE_SERIES_MAP, mi.ENG_GAS_TEMP_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Eng Gas Temp range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_rudder_pedal_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Rudder Pedal limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.RUDDER_PEDAL_RANGE_MODEL_MAP, mi.RUDDER_PEDAL_RANGE_SERIES_MAP, mi.RUDDER_PEDAL_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Rudder Pedal range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_sidestick_pitch_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Sidestick Pitch limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.SIDESTICK_PITCH_RANGE_MODEL_MAP, mi.SIDESTICK_PITCH_RANGE_SERIES_MAP, mi.SIDESTICK_PITCH_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Sidestick Pitch range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_sidestick_roll_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Sidestick Roll limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.SIDESTICK_ROLL_RANGE_MODEL_MAP, mi.SIDESTICK_ROLL_RANGE_SERIES_MAP, mi.SIDESTICK_ROLL_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Sidestick Roll range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_tail_rotor_pedal_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Tail Rotor Pedal limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.TAIL_ROTOR_PEDAL_RANGE_MODEL_MAP, mi.TAIL_ROTOR_PEDAL_RANGE_SERIES_MAP, mi.TAIL_ROTOR_PEDAL_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Tail Rotor pedal range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_throttle_lever_range(model=None, series=None, family=None):
    '''
    Accessor for fetching Throttle Lever limits.

    Returns a tuple in the following form::

        (angle, angle)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of limits
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.THROTTLE_LEVER_RANGE_MODEL_MAP, mi.THROTTLE_LEVER_RANGE_SERIES_MAP, mi.THROTTLE_LEVER_RANGE_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Throttle Lever range for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_gear_transition_times(model=None, series=None, family=None):
    '''
    Accessor for fetching duration gears take of fully retract/extend.

    Returns a tuple in the following form::

        (retraction time, extention time)

    :param model: Aircraft series e.g. B737-888
    :type model: string
    :param series: Aircraft series e.g. B737-800
    :type series: string
    :param family: Aircraft family e.g. B737 NG
    :type family: string
    :raises: KeyError if no limits found
    :returns: tuple of durations
    :rtype: tuple
    '''
    keys = model, series, family
    maps = mi.GEAR_TRANSITION_TIME_MODEL_MAP, mi.GEAR_TRANSITION_TIME_SERIES_MAP, mi.GEAR_TRANSITION_TIME_FAMILY_MAP

    for k, m in zip(keys, maps):
        if k in m:
            return m[k]

    message = "No Gear transition times for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)
