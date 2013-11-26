# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
'''

#############################################################################
# Imports


from itertools import chain, cycle, imap, izip, product

from flightdatautilities import sortext

from flightdatautilities.aircrafttables import constants

# Note: These are overridden as part of the aircraft table configuration!
from flightdatautilities.aircrafttables import model_information as mi
from flightdatautilities.aircrafttables import maximum_speed as ms
from flightdatautilities.aircrafttables import velocity_speed as vs


#############################################################################
# Exports


__all__ = (
    'get_aileron_detents', 'get_aileron_map',
    'get_conf_detents', 'get_conf_map', 'get_conf_angles',
    'get_flap_detents', 'get_flap_map',
    'get_lever_detents', 'get_lever_map', 'get_lever_angles',
    'get_slat_detents', 'get_slat_map',
    'get_stabilizer_limits',
    'get_vspeed_map',
    'get_max_speed_table',
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
        detents.update(chain.from_iterable(x.itervalues()))
    return sortext.nsorted(detents)


def get_slat_detents():
    '''
    Get all slat detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in mi.SLAT_MODEL_MAP, mi.SLAT_SERIES_MAP, mi.SLAT_FAMILY_MAP:
        detents.update(chain.from_iterable(x.itervalues()))
    return sortext.nsorted(detents)


def get_aileron_detents():
    '''
    Get all aileron detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    detents = set()
    for x in mi.AILERON_MODEL_MAP, mi.AILERON_SERIES_MAP, mi.AILERON_FAMILY_MAP:
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
    for x in mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP:
        detents.update(chain.from_iterable(imap(extract, x.itervalues())))
    return sortext.nsorted(detents)


def get_lever_detents():
    '''
    Get all lever detents from all supported aircraft types

    :returns: list of detent values
    :rtype: list
    '''
    extract = lambda x: (v[1] for v in x.iterkeys())
    detents = set(map(str, get_flap_detents()))  # initialise with flap detents
    for x in mi.LEVER_MODEL_MAP, mi.LEVER_SERIES_MAP, mi.LEVER_FAMILY_MAP:
        detents.update(chain.from_iterable(imap(extract, x.itervalues())))
    detents.update(constants.LEVER_STATES.values()) # Include Conf Lever states
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

    for k, m in izip(keys, maps):
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

    for k, m in izip(keys, maps):
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

    for k, m in izip(keys, maps):
        if k in m:
            return {v: str(v) for v in m[k]}

    message = "No aileron mapping for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


def get_conf_map(model=None, series=None, family=None):
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
    :raises: KeyError if no mapping found
    :returns: mapping of detent to state values
    :rtype: dict
    '''
    keys = model, series, family
    maps = mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP
    conf = constants.AVAILABLE_CONF_STATES.items()

    for k, m in izip(keys, maps):
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

    for k, m in izip(keys, maps):
        if k in m:
            return dict(m[k].iterkeys())

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
    :type model: string
    :param series: Aircraft series e.g. A340-500
    :type series: string
    :param family: Aircraft family e.g. A340
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
    maps = mi.CONF_MODEL_MAP, mi.CONF_SERIES_MAP, mi.CONF_FAMILY_MAP
    conf = constants.AVAILABLE_CONF_STATES.items()

    for k, m in izip(keys, maps):
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

    for k, m in izip(keys, maps):
        if k not in m:
            continue
        d = m[k]        
        if key == 'both':
            return d
        if key == 'state':
            return {x[1]: v for x, v in d.iteritems()}
        if key == 'value':
            return {x[0]: v for x, v in d.iteritems()}
        
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

    for k, m in izip(keys, maps):
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

    for k, m in izip(keys, maps):
        if k in m:
            return m[k]

    message = "No airbrake coefficients for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


##############################################################################
# Velocity Speed Accessors


def get_vspeed_map(model=None, series=None, family=None, engine_series=None, engine_type=None):
    '''
    Accessor for fetching velocity speed tables for V2/Vref/Vapp.

    Returns a class of VelocitySpeed that can be instantiated.

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
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
    it = izip(imap(lambda x: x[::-1], product(engines, keys)), cycle(maps))

    for k, m in it:
        if k in m:
            return m[k]

    message = "No velocity speed table for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)


##############################################################################
# VMO/MMO Accessors


def get_max_speed_table(model=None, series=None, family=None):
    '''
    Accessor for fetching maximum speed tables for VMO/MMO.

    Returns an instance of a MaximumSpeed object with callable methods.

    :param model: Aircraft series e.g. B737-333
    :type model: string
    :param series: Aircraft series e.g. B737-300
    :type series: string
    :param family: Aircraft family e.g. B737 Classic
    :type family: string
    :raises: KeyError if no table is found
    :returns: lookup object for maximum speeds.
    :rtype: MaximumSpeed
    '''
    keys = model, series, family
    maps = ms.MAX_SPEED_MODEL_MAP, ms.MAX_SPEED_SERIES_MAP, ms.MAX_SPEED_FAMILY_MAP

    for k, m in izip(keys, maps):
        if k in m:
            procedure, args = m[k]
            return procedure(*args)

    message = "No VMO/MMO table for model '%s', series '%s', family '%s'."
    raise KeyError(message % keys)
