# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Unit tests for aircraft model information tables and functions.
'''

##############################################################################
# Imports


from flightdatautilities.aircrafttables.accessors import *  # noqa


##############################################################################
# Configuration


def configure(package):
    '''
    Configures the aircraft tables package to be used for lookups.

    The package provided should contain the following modules:

    - model_information
    - velocity_speed

    :param package: the name of the package containing the required modules.
    :type package: str
    '''
    import importlib
    import logging

    logger = logging.getLogger(name=__name__)

    paths = {
        'et': 'engine_thresholds',
        'mi': 'model_information',
        'vs': 'velocity_speed',
    }

    for variable, name in paths.items():
        try:
            module = importlib.import_module('%s.%s' % (package, name))
        except ImportError:
            message = "Unable to import module '%s' from package '%s'!"
            logger.exception(message, name, package)
        else:
            from flightdatautilities.aircrafttables import accessors
            setattr(accessors, variable, module)
