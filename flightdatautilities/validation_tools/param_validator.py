#!/usr/bin/env python
'''
Suite of validation functions for a Parameter object as defined in
FlightDataAccessor.datatypes.
These tests allow to validate parameters from a FDF (Flight Data File).

The various validation functions will return a list of `LogRecord`s,
see https://docs.python.org/3/library/logging.html#logging.LogRecord

This should allow the client code to use those findings the way they want.
If they just want to log those entries, they can do:
>>> for record in records:
>>>     logger.handle(record)
'''

import logging
from logging import LogRecord
from logging.handlers import BufferingHandler
from typing import Iterable, List
import numpy as np

from analysis_engine.utils import list_parameters
import flightdataaccessor as fda

from flightdatautilities.validation_tools.parameter_lists import PARAMETERS_FROM_FILES
from flightdatautilities.patterns import wildcard_match
from flightdatautilities.state_mappings import PARAMETER_CORRECTIONS
from flightdatautilities import units as ut


class MemoryBufferHandler(BufferingHandler):
    def get(self):
        '''Provides all accumulated LogRecord and flush the buffer.'''
        buffer = self.buffer
        self.flush()
        return buffer


logger = logging.getLogger(__name__)
buffer = MemoryBufferHandler(capacity=1_000)
logger.addHandler(buffer)
logger.setLevel(logging.DEBUG)


VALID_FREQUENCIES = {
    # base 2 frequencies
    0.03125,
    0.015625,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
    4,
    8,
    16,
    # other non base 2 frequencies
    0.016666667,
    0.05,
    0.1,
    0.2,
    5,
    10,
    20,
}

# -----------------------------------------------------------------------------
# Collection of parameters known to Polaris
# -----------------------------------------------------------------------------

# Main list of parameters that from the Polaris analysis engine
PARAMETERS_ANALYSIS = list_parameters()

# Minimum list of parameters (including alternatives) needed in the HDF file.
# See check_for_core_parameters method
PARAMETERS_CORE = [
    'Airspeed',
    'Heading',
    'Altitude STD',
    # Helicopter only
    'Nr',
    # Alternatives
    'Heading True',
    'Nr (1)',
    'Nr (2)',
]

# Extra parameters not listed from list_parameter
PARAMETERS_EXTRA = [
    'Day',
    'Hour',
    'Minute',
    'Month',
    'Second',
    'Year',
    'Frame Counter',
    'Subframe Counter',
]

PARAMETER_LIST = list(set(PARAMETERS_FROM_FILES + PARAMETERS_ANALYSIS +
                          PARAMETERS_CORE + PARAMETERS_EXTRA))


# -----------------------------------------------------------------------------



def check_for_core_parameters(param_names: Iterable[str], helicopter=False) -> List[LogRecord]:
    """
    Check that the following parameters exist in the iterable:
    - 'Airspeed'
    - 'Altitude STD'
    - either 'Heading' or 'Heading True'
    For Helicopters, an additional parameter, Rotor Speed, is required:
    - either 'Nr' or for dual rotors 'Nr (1)' and 'Nr (2)'
    Minimum parameter required for any analysis to be performed.
    """
    airspeed = 'Airspeed' in param_names
    altitude = 'Altitude STD' in param_names
    heading = 'Heading' in param_names
    heading_true = 'Heading True' in param_names
    rotor = 'Nr' in param_names
    nr1and2 = ('Nr (1)' in param_names) and ('Nr (2)' in param_names)

    core_available = airspeed and altitude and (heading or heading_true)
    if core_available and helicopter:
        core_available = rotor or nr1and2

    if core_available:
        logger.info("All core parameters available for analysis.")
        if heading_true and not heading:
            logger.info("Analysis will use parameter 'Heading True' as "
                        "parameter 'Heading' not available.")
    else:
        if not airspeed:
            logger.error("Parameter 'Airspeed' not found. Required as one "
                         "of the core parameters for analysis.")
        if not altitude:
            logger.error("Parameter 'Altitude STD' not found. Required as "
                         "one of the core parameters for analysis.")
        if not heading and not heading_true:
            logger.error("Parameter 'Heading' and 'Heading True' not found. "
                         "One of these parameters is required for analysis.")
        if helicopter and not rotor and not nr1and2:
            logger.error("Parameter 'Nr' (or 'Nr (1)' and 'Nr (2)') not "
                         "found. Helicopter's rotor speed is required as one "
                         "of the core parameter for analysis.")
    return buffer.get()


def validate_arinc_429(parameter) -> List[LogRecord]:
    """
    Reports if parameter attribute arinc_429 exists.
    If so, check it is a boolean and report its value.
    """
    logger.info("Checking parameter attribute: arinc_429")
    if parameter.arinc_429 is None:
        logger.warn("'arinc_429': No attribute for '%s'. Optional attribute, "
                    "if parmater does not have an ARINC 429 source.",
                    parameter.name)
    else:
        if 'bool' not in type(parameter.arinc_429).__name__:
            logger.error("'arinc_429': Attribute for %s is not a Boolean "
                         "type.", parameter.name)
        if parameter.arinc_429:
            logger.info("'arinc_429': '%s' has an ARINC 429 source.",
                        parameter.name)
        else:
            logger.info("'arinc_429': '%s' does not have an ARINC 429 source.",
                        parameter.name)
    return buffer.get()


def validate_source_name(parameter) -> List[LogRecord]:
    """Reports if the parameter attribute source_name exists."""
    logger.info("Checking parameter attribute: source_name")
    if parameter.source_name is None:
        logger.info("'source_name': No attribute for '%s'. Attribute is "
                    "optional.", parameter.name)
    else:
        pname = parameter.source_name
        logger.info("'source_name': Attribute is present. Original name '%s' "
                    "maps to %s'", pname, parameter.name)
    return buffer.get()


def validate_supf_offset(parameter) -> List[LogRecord]:
    """
    Check if the parameter attribute supf_offset exists (It is required)
    and report.
    """
    logger.info("Checking parameter attribute: supf_offset")
    if parameter.offset is None:
        logger.error("'supf_offset': No attribute for '%s'. Attribute is "
                     "Required. ", parameter.name)
    else:
        if 'float' not in type(parameter.offset).__name__:
            msg = "'supf_offset': Type for '%s' is not a float. "\
                "Got %s instead" % (parameter.name,
                                    type(parameter.offset).__name__)
            if parameter.offset == 0:
                logger.warn(msg)
            else:
                logger.error(msg)
        else:
            logger.info("'supf_offset': Attribute is present and correct "
                        "data type and has a value of %s", parameter.offset)
    return buffer.get()


def validate_values_mapping(parameter, states=False) -> List[LogRecord]:
    """
    Check if the parameter attribute values_mapping exists (It is required for
    discrete or multi-state parameter) and reports the value.
    """
    logger.info("Checking parameter attribute: values_mapping")
    if not parameter.values_mapping:
        if parameter.data_type in ('Discrete', 'Multi-state',
                                   'Enumerated Discrete'):
            logger.error("'values_mapping': No attribute for '%s'. "
                         "Attribute is Required for a %s parameter.",
                         parameter.name, parameter.data_type)
        else:
            logger.info("'values_mapping': No attribute. Not required "
                        "for '%s'.", parameter.name)
    else:
        logger.info("'values_mapping': Attribute value is: %s",
                    parameter.values_mapping)

        if parameter.data_type == 'Discrete':
            try:
                value0 = parameter.values_mapping[0]  # False values
                logger.debug("'values_mapping': Discrete value 0 maps to "
                             "'%s'.", value0)
            except KeyError:
                logger.debug("'values_mapping': Discrete value 0 has no "
                             "mapping.")
            try:
                value1 = parameter.values_mapping[1]  # True values
            except KeyError:
                logger.error("'values_mapping': Discrete value 1 has no "
                             "mapping. Needs to have a mapping for this "
                             "value.")
            else:
                if value1 in ["", "-"]:
                    logger.error("'values_mapping': Discrete value 1 should "
                                 "not map to '-' or an empty string. Value "
                                 "1 maps to '%s'.", value1)
                else:
                    logger.debug("'values_mapping': Discrete value 1 maps "
                                 "to '%s'", value1)

            if len(parameter.values_mapping.keys()) > 2:
                logger.error("'values_mapping': '%s' is a discrete parameter, "
                             "but the values_mapping attribute has %s values. "
                             "There should be no more than 2.",
                             parameter.name,
                             len(parameter.data_type.keys()))

    if states:
        logger.info("Checking parameter states and checking the validity: states")
        if not '(' in parameter.name or not ')' in parameter.name:
            states = PARAMETER_CORRECTIONS.get(parameter.name)
            if states and {k: v for k, v in parameter.values_mapping.items() if v != '-'} != states:
                logger.error("'values_mapping': '%s' does not contain valid states %s, "
                             "the states should be %s.",
                             parameter.name, parameter.values_mapping, states)
        else:
            for pattern, states in PARAMETER_CORRECTIONS.items():
                found_matches = wildcard_match(pattern, [parameter.name])
                if found_matches:
                    if {k: v for k, v in parameter.values_mapping.items() if v != '-'} != states:
                        logger.error("'values_mapping': '%s' does not contain valid states %s, "
                                     "the states should be %s.",
                                     parameter.name, parameter.values_mapping, states)
                    break
    return buffer.get()


def validate_data_type(parameter) -> List[LogRecord]:
    """
    Checks the parameter attribute data_type exists (It is required)
    and verify that the data has the correct type.
    """
    logger.info("Checking parameter attribute: data_type")
    if parameter.data_type is None:
        logger.error("'data_type': No attribute present for '%s'. "
                     "This is required attribute.", parameter.name)
    else:
        logger.info("'%s' has a 'data_type' attribute of: %s", parameter.name,
                    parameter.data_type)
        logger.info("'%s' data has a dtype of: %s", parameter.name,
                    parameter.array.data.dtype)
        if parameter.data_type in ['ASCII', ]:
            if 'bytes' not in parameter.array.dtype.name:
                logger.error("'%s' data type is %s. It should be a byte string "
                             "for '%s' parameters.", parameter.name,
                             parameter.array.dtype.name, parameter.data_type)
                return buffer.get()
        elif parameter.data_type in ['BCD', 'Interpolated', 'Polynomial',
                                     'Signed', 'Synchro', 'Unsigned']:
            if 'float' not in parameter.array.dtype.name:
                logger.error("'%s' data type is %s. It should be a float "
                             "for '%s' parameters.", parameter.name,
                             parameter.array.dtype.name, parameter.data_type)
                return buffer.get()
        elif parameter.data_type in ['Multi-state', 'Discrete']:
            if 'int' not in parameter.array.dtype.name:
                logger.warn("'%s' data type is %s. It should be an int "
                            "for '%s' parameters.", parameter.name,
                            parameter.array.dtype.name, parameter.data_type)
                return buffer.get()
        logger.info("'%s' data_type is %s and is an array of %s.",
                    parameter.name, parameter.data_type,
                    parameter.array.dtype.name)
    return buffer.get()


def validate_frequency(parameter) -> List[LogRecord]:
    """
    Checks the parameter attribute frequency exists (It is required)
    and report if it is a valid frequency.
    """
    logger.info("Checking parameter attribute: frequency")
    if parameter.frequency is None:
        logger.error("'frequency': No attribute present for '%s'. "
                     "This is required attribute.", parameter.name)
    else:
        if parameter.frequency not in VALID_FREQUENCIES:
            logger.error("'frequency': '%s' has a value of %s which is not a "
                         "frequency supported by POLARIS.", parameter.name,
                         parameter.frequency)
        else:
            logger.info("'frequency': Value is %s Hz for '%s' and is a "
                        "support frequency.", parameter.frequency,
                        parameter.name)
    return buffer.get()


def validate_lfl(parameter) -> List[LogRecord]:
    '''
    Check that the required lfl attribute is present. Report if recorded or
    derived.
    '''
    logger.info("Checking parameter attribute: lfl")
    if parameter.lfl is None:
        logger.error("'lfl': No attribute for '%s'. Attribute is Required.",
                     parameter.name)
        return buffer.get()
    if 'bool' not in type(parameter.lfl).__name__:
        logger.error("'lfl': Attribute should be a Boolean. Type is %s",
                     type(parameter.lfl).__name__)
    if parameter.lfl:
        logger.info("'%s': Is a recorded parameter.", parameter.name)
    else:
        logger.info("'%s': Is a derived parameter.", parameter.name)
    return buffer.get()


def validate_name(parameter, name) -> List[LogRecord]:
    """
    Checks the parameter attribute name exists (It is required)
    and report if name matches the parameter's group name.
    """
    logger.info("Checking parameter attribute: name")
    if parameter.name is None:
        logger.error("'name': No attribute for '%s'. Attribute is Required.",
                     name)
    elif parameter.name != name:
        logger.error("'name': Attribute is present, but is not the same "
                     "name as the parameter group. name: %s, parameter "
                     "group: %s", parameter.name, name)
    else:
        logger.info("'name': Attribute is present and name is the same "
                    "name as the parameter group.")
    return buffer.get()


def validate_units(parameter) -> List[LogRecord]:
    """
    Check if the parameter attribute units exists (It is required)
    and reports the value and if it is valid unit name.
    """
    logger.info("Checking parameter attribute: units")
    if parameter.data_type in ('Discrete', 'Multi-state', 'ASCII',
                               'Enumerated Discrete'):
        return buffer.get()
    if parameter.units is None:
        logger.warn("'units': No attribute for '%s'. Attribute is Required.",
                    parameter.name)
    else:
        if type(parameter.units).__name__ not in ['str', 'string', 'string_']:
            logger.error("'units': Attribute expected to be a string, got %s",
                         type(parameter.units).__name__)
        if parameter.units == '':
            logger.info("'units': Attribute is present for '%s', but empty.",
                        parameter.name)

        available = parameter.units in ut.available()
        corrections = ut.UNIT_CORRECTIONS.get(parameter.units)
        converting = ut.STANDARD_CONVERSIONS.get((corrections or
                                                  parameter.units))
        if converting:
            convserion_desc = ut.UNIT_DESCRIPTIONS.get(converting)
            logger.error("'units': Attribute is present for '%s', but from "
                         "the value ('%s') the parameter data requires "
                         "converting to %s with a units value of '%s'.",
                         parameter.name, parameter.units,
                         convserion_desc, converting)
        elif corrections:
            logger.error("'units': Attribute is present for '%s', but the "
                         "value ('%s') needs to be updated to '%s'.",
                         parameter.name, parameter.units, corrections)
        elif available:
            logger.info("'units': Attribute is present for '%s' and has a "
                        "valid unit of '%s'.", parameter.name, parameter.units)
        else:
            logger.error("'units': Attribute is present for '%s', but has an "
                         "unknown unit of '%s'.",
                         parameter.name, parameter.units)
    return buffer.get()


def inf_nan_check(parameter) -> List[LogRecord]:
    '''
    Check the dataset for NaN or inf values
    '''
    def _report(count, parameter, unmasked, val_str):
        '''
        log as warning if all are masked, error if not
        '''
        if count:
            msg = "Found %s %s values in the data of '%s'. " \
                % (count, val_str, parameter.name)
            nan_percent = (float(count) / len(parameter.array.data)) * 100
            msg += "This represents %.2f%% of the data. " % (nan_percent, )
            if unmasked:
                msg += "%s are not masked." % (unmasked,)
                logger.error(msg)
            else:
                msg += "All of these values are masked."
                logger.warning(msg)

    logger.info("Checking parameter dataset for inf and NaN values.")
    if 'int' in parameter.array.dtype.name or \
       'float' in parameter.array.dtype.name:

        nan_unmasked = np.ma.masked_equal(
            np.isnan(parameter.array), False).count()
        nan_count = np.ma.masked_equal(
            np.isnan(parameter.array.data), False).count()
        inf_unmasked = np.ma.masked_equal(
            np.isinf(parameter.array), False).count()
        inf_count = np.ma.masked_equal(
            np.isinf(parameter.array.data), False).count()

        _report(nan_count, parameter, nan_unmasked, 'NaN')
        _report(inf_count, parameter, inf_unmasked, 'inf')

        if nan_count == inf_count == 0:
            logger.info("Dataset does not have any inf or NaN values.")
    return buffer.get()


def validate_dataset(parameter) -> List[LogRecord]:
    """Check the data for size, unmasked inf/NaN values."""
    logs = inf_nan_check(parameter)

    if parameter.array.data.size != parameter.array.mask.size:
        logger.error("The data and mask sizes are different. (Data is %s, "
                     "Mask is %s)", parameter.array.data.size,
                     parameter.array.mask.size)
    else:
        logger.info("Data and Mask both have the size of %s elements.",
                    parameter.array.data.size)

    logger.info("Checking dataset type and shape.")
    masked_array = isinstance(parameter.array, np.ma.core.MaskedArray)
    mapped_array = isinstance(parameter.array, fda.MappedArray)
    if not masked_array and not mapped_array:
        logger.error("Data for %s is not a MaskedArray or MappedArray. "
                     "Type is %s", parameter.name, type(parameter.array))
    else:
        # check shape, it should be 1 dimensional arrays for data and mask
        if len(parameter.array.shape) != 1:
            logger.error("The data and mask are not in a 1 dimensional "
                         "array. The data's shape is %s ",
                         parameter.array.shape)
        else:
            logger.info("Data is in a %s with a shape of %s",
                        type(parameter.array).__name__, parameter.array.shape)
    if parameter.array.mask.all():
        logger.warning("Data for '%s' is entirely masked. Is it meant to be?",
                       parameter.name)
    logs.extend(buffer.get())
    return logs
