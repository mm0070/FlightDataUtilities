# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
'''

##############################################################################
# Imports


import logging
import numpy as np

from abc import ABCMeta
from bisect import bisect_left

import scipy.interpolate as interp

from flightdatautilities import units as ut


#############################################################################
# Globals


logger = logging.getLogger(name=__name__)


##############################################################################
# Abstract Classes


class VelocitySpeed(object):
    '''
    Provides a base implementation of a velocity speed lookup table.

    There are a number of flags that can be set to configure the table:

    - interpolate -- whether to interpolate between table values.
    - minimum_speed -- the absolute minimum speed.
    - source -- reference to the documentation or source of lookup table.
    - weight_unit -- the unit for all of the weights in the table.
    '''

    __meta__ = ABCMeta

    interpolate = False
    minimum_speed = None
    source = None
    weight_unit = ut.KG  # Can be one of 'lb', 'kg', 't' or None.

    tables = {
        'v2': {'weight': ()},
        'vref': {'weight': ()},
    }

    @property
    def v2_settings(self):
        '''
        Provides a list of available flap/conf settings for V2.

        :returns: a list of flap/conf settings.
        :rtype: list
        '''
        settings = self.tables['v2'].keys()
        if 'weight' in settings:
            settings.remove('weight')
        return sorted(settings)

    @property
    def vref_settings(self):
        '''
        Provides a list of available flap/conf settings for Vref.

        :returns: a list of flap/conf settings.
        :rtype: list
        '''
        settings = self.tables['vref'].keys()
        if 'weight' in settings:
            settings.remove('weight')
        return sorted(settings)

    def v2(self, setting, weight=None):
        '''
        Look up a value for V2.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: V2 value or None.
        :rtype: float
        :raises: KeyError -- when table or flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._get_velocity_speed(self.tables['v2'], setting, weight)

    def vref(self, setting, weight=None):
        '''
        Look up a value for Vref.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: Vref value or None.
        :rtype: float
        :raises: KeyError -- when table or flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._get_velocity_speed(self.tables['vref'], setting, weight)

    def _get_velocity_speed(self, lookup, setting, weight=None):
        '''
        Looks up the velocity speed in the provided lookup table.

        Will use interpolation if configured and convert units if necessary.

        None will be returned if weight is outside of the table range or no
        entries are available in the table for the provided flap/conf value.

        :param lookup: The velocity speed lookup table.
        :type lookup: dict
        :param setting: Flap or conf setting to use in lookup.
        :type setting: string
        :param weight: Weight of the aircraft.
        :type weight: float
        :returns: A velocity speed value or None.
        :rtype: float
        :raises: KeyError -- when flap/conf settings is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        # Attempt to coerce the setting value if it isn't a string:
        if not isinstance(setting, str):
            msg = "Non-string detent provided - %r - attempting to coerce..."
            logger.warning(msg, setting)
            if isinstance(setting, float) and setting.is_integer():
                setting = str(int(setting))
            else:
                setting = str(setting)

        if setting not in lookup:
            msg = "Velocity speed table '%s' has no entry for flap/conf '%s'."
            arg = (self.__class__.__name__, setting)
            logger.error(msg, *arg)
            # raise KeyError(msg % arg)
            return None

        # If table which doesn't have weights return fixed value:
        if self.weight_unit is None:
            return lookup[setting]

        # Convert the aircraft weight to match the lookup table:
        weight = ut.convert(weight, ut.KG, self.weight_unit)

        wt = lookup['weight']
        if not min(wt) <= weight <= max(wt) or weight is np.ma.masked:
            msg = "Weight '%s' outside of range for velocity speed table '%s'."
            arg = (weight, self.__class__.__name__)
            logger.warning(msg, *arg)
            return None

        # Determine the value for the velocity speed:
        if self.interpolate:
            f = interp.interp1d(lookup['weight'], lookup[setting])
            value = f(weight)
        else:
            index = bisect_left(lookup['weight'], weight)
            value = lookup[setting][index]

        # Return a minimum speed if we have one and the value is below it:
        if self.minimum_speed is not None and value < self.minimum_speed:
            return self.minimum_speed

        return value


class MaximumSpeed(object):
    '''
    '''

    __meta__ = ABCMeta

    def __init__(self, vmo=None, mmo=None):
        '''
        Initialises an object from which we can generate VMO/MMO data arrays.

        :param vmo:
        :type vmo: int or tuple
        :param mmo:
        :type mmo: float or tuple
        '''
        self.vmo = vmo
        self.mmo = mmo

    def _prepare_array(self, array, mask=None):
        '''
        Prepares an array to put VMO/MMO values into based on another array.

        If the mask parameter is not provided, the mask will be copied from the
        provided array, usually the pressure altitude array.

        :param array:
        :type array: np.ma.array
        :param mask:
        :type mask: np.ma.array or bool or None
        :returns:
        :rtype: np.ma.array
        '''
        mask = array.mask if mask is None else mask
        return np.ma.array(np.zeros_like(array.data), mask=mask, dtype=float)

    def get_mmo_array(self, alt_std):
        '''
        Returns an array of MMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        raise NotImplementedError

    def get_mmo_value(self, alt_std):
        '''
        Returns an MMO value for the provided pressure altitude value.

        :param alt_std:
        :type alt_std: int or float
        :returns:
        :rtype: np.ma.array
        '''
        if not isinstance(alt_std, (int, float)):
            raise ValueError('Expected an integer or float for altitude.')
        return self.get_mmo_array(np.ma.array([alt_std]))[0]

    def get_vmo_array(self, alt_std):
        '''
        Returns an array of VMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        raise NotImplementedError

    def get_vmo_value(self, alt_std):
        '''
        Returns a VMO value for the provided pressure altitude value.

        :param alt_std:
        :type alt_std: int or float
        :returns:
        :rtype: np.ma.array
        '''
        if not isinstance(alt_std, (int, float)):
            raise ValueError('Expected an integer or float for altitude.')
        return self.get_vmo_array(np.ma.array([alt_std]))[0]


##############################################################################
# Shared Classes


class MaximumSpeed_Fixed(MaximumSpeed):
    '''
    Provides arrays of fixed constant VMO or MMO values.

    The same value is returned for any value of pressure altitude.
    '''

    def get_mmo_array(self, alt_std):
        '''
        Returns an array of MMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        if self.mmo is None:
            return self._prepare_array(alt_std, mask=True)
        else:
            array = self._prepare_array(alt_std, mask=False)
            array.fill(self.mmo)
            return array

    def get_vmo_array(self, alt_std):
        '''
        Returns an array of VMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        if self.vmo is None:
            return self._prepare_array(alt_std, mask=True)
        else:
            array = self._prepare_array(alt_std, mask=False)
            array.fill(self.vmo)
            return array


class MaximumSpeed_Range(MaximumSpeed):
    '''
    Provides arrays of variable VMO or MMO values depending on altitude range.
    '''

    def _prepare_condition(self, alt_std, low, high):
        '''
        :param alt_std:
        :type alt_std: np.ma.array
        :param low:
        :type low:
        :param high:
        :type high:
        :returns:
        :rtype: np.ma.array
        '''
        if low is not None and high is not None:
            return (low < alt_std) & (alt_std <= high)
        if low is None:
            return alt_std <= high
        if high is None:
            return low < alt_std
        return np.array([], dtype=bool)

    def get_mmo_array(self, alt_std):
        '''
        Returns an array of MMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        if self.mmo is None:
            return self._prepare_array(alt_std, mask=True)
        else:
            array = self._prepare_array(alt_std, mask=True)
            for low, high, mmo in self.mmo:
                condition = self._prepare_condition(alt_std, low, high)
                array[condition] = mmo
            return array

    def get_vmo_array(self, alt_std):
        '''
        Returns an array of VMO values for the provided pressure altitude.

        :param alt_std:
        :type alt_std: np.ma.array
        :returns:
        :rtype: np.ma.array
        '''
        if self.vmo is None:
            return self._prepare_array(alt_std, mask=True)
        else:
            array = self._prepare_array(alt_std, mask=True)
            for low, high, vmo in self.vmo:
                condition = self._prepare_condition(alt_std, low, high)
                array[condition] = vmo
            return array
