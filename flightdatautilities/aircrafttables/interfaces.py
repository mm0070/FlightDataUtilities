##############################################################################

'''
'''

##############################################################################
# Imports


import logging
import numbers
import numpy as np
import scipy.interpolate

from abc import ABCMeta

from flightdatautilities import units as ut


#############################################################################
# Globals


logger = logging.getLogger(name=__name__)


##############################################################################
# Abstract Classes


class VelocitySpeed:
    '''
    Provides a base implementation of a velocity speed lookup table.

    There are a number of flags that can be set to configure the table:

    - minimum_speed -- the absolute minimum speed.
    - source -- reference to the documentation or source of lookup table.
    - weight_scale -- how the weight values in the table are scaled.
    - weight_unit -- the unit for all of the weights in the table.
    '''

    __meta__ = ABCMeta

    source = None
    minimum_speed = None
    weight_scale = 1     # Can be used to scale values, e.g. 1000 lb.
    weight_unit = ut.KG  # Can be one of 'lb', 'kg', 't' or None.
    tables = {}          # Can contain the following keys: v2, vref, vapp, vmo, mmo.
    fallback = {}        # Can contain the following keys: v2, vref, vapp.

    def _build_array(self, array, mask=None, value=0.0):
        '''
        Prepares an array to put v-speed values into based on another array.

        If the mask parameter is not provided, the mask will be copied from the
        provided array.

        :param array: an array to use as a basis for this one.
        :type array: np.ma.array
        :param mask: a mask array to use, a boolean to fully mask or unmask the
                     resulting array or None to use the mask of the provided
                     array..
        :type mask: np.ma.array or bool or None
        :param value: a default value to fill the array with.
        :type value: int or float
        :returns: a prepared masked array.
        :rtype: np.ma.array
        '''
        return np.ma.array(
            data=np.ones_like(array.data) * value,
            mask=array.mask if mask is None else mask,
            dtype=np.float,
        )

    def _determine_vspeed(self, name, **kwargs):
        '''
        Look up a value from tables for the specified velocity speed.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param name: the name of the lookup table to use.
        :type name: string
        :param kwargs: values required to lookup the speed.
        :type kwargs: dict
        :returns: one or more velocity speed values.
        :rtype: float or np.ma.array
        :raises: KeyError -- when table or flap/conf detents is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        if name in ('v2', 'vref', 'vapp', 'vls'):
            detent = kwargs['detent']
            weight = kwargs['weight']
            scalar = isinstance(weight, (type(None), int, float))
            if weight is not None and weight is not np.ma.masked:
                weight = np.ma.array(weight, copy=True, dtype=np.double, ndmin=1)
            else:
                weight = np.ma.array(data=[0.0], dtype=np.double, mask=True)

            # Attempt to coerce the detent value if it isn't a string:
            if not isinstance(detent, str):
                msg = "Non-string detent provided - %r - coercing..."
                logger.warning(msg, detent)
                if isinstance(detent, float) and detent.is_integer():
                    detent = str(int(detent))
                else:
                    detent = str(detent)

            # Attempt to lookup values from standard and fallback tables:
            try_fallback = self.weight_unit is None or weight.mask.all()
            if try_fallback:
                msg = "Trying fallback %s values in table %s (weight masked)."
                logger.info(msg, name, self.__class__.__name__)
            else:
                try:
                    lookup = self.tables[name][detent]
                except KeyError:
                    try_fallback = True
                    msg = "Trying fallback %s values in table %s for detent %r."
                    logger.warning(msg, name, self.__class__.__name__, detent)
                else:
                    msg = "Using standard %s values from table %s."
                    logger.info(msg, name, self.__class__.__name__)
            if try_fallback:
                try:
                    lookup = self.fallback[name][detent]
                except KeyError:
                    lookup = None
                    msg = "Missing %s values in table %s for detent %r."
                    logger.error(msg, name, self.__class__.__name__, detent)
                else:
                    msg = "Using fallback %s values from table %s."
                    logger.info(msg, name, self.__class__.__name__)

            # VLS may contain extra center_of_gravity dimension:
            if name == 'vls' and lookup:
                if None in lookup.keys():
                    lookup = lookup[None]
                else:
                    keys = sorted(lookup.keys())
                    lookup = tuple([np.interp(kwargs['cg'], keys, row) for row in
                              zip(*(lookup[key] for key in keys))])


            # Generate an array of velocity speed values for given parameters:
            if lookup is None:
                array = self._build_array(weight, mask=True)
            elif isinstance(lookup, (int, float)):
                array = self._build_array(weight, mask=False, value=lookup)
            elif isinstance(lookup, tuple):
                x, y = map(
                    list,
                    zip(*[z for z in zip(self.tables[name]['weight'], lookup) \
                          if z[0] is not None  and z[1] is not None])
                )
                # Scale the lookup table weights if necessary:
                if not self.weight_scale == 1:
                    x = list(map(lambda w: int(w * self.weight_scale), x))
                # Convert the aircraft weight to match the lookup table:
                if not self.weight_unit == ut.KG:
                    weight *= ut.multiplier(ut.KG, self.weight_unit)
                # Check whether we have any out-of-bounds values, and warn:
                if ((weight < min(x)) | (max(x) < weight)).any():
                    logger.warning("Encountered some weight values outside of "
                                   "range for velocity speed table '%s'.",
                                   self.__class__.__name__)
                # Determine the value for the velocity speed:
                array = np.interp(weight, x, y, np.nan, np.nan)
                array = np.ma.fix_invalid(array, mask=weight.mask, fill_value=0.0)
                # If we have a minimum speed, enforce it throughout the array:
                if self.minimum_speed is not None:
                    condition = (array < self.minimum_speed) & (~array.mask)
                    array[condition] = self.minimum_speed
            else:
                raise ValueError('Invalid v-speed table structure.')

            array = array.round().astype(np.int)
            return array[0] if scalar else array

        if name == 'vls_clean':
            try:
                lookup = self.tables[name]
            except KeyError:
                lookup = None
                msg = "Velocity speed table '%s' has no '%s' entry."
                logger.error(msg, self.__class__.__name__, name)

            weight = kwargs['weight']
            altitude = kwargs['altitude']

            if weight is None or altitude is None:
                lookup = None
                msg = "Velocity speed table '%s' received None for weight or altitude keyword argument."
                logger.error(msg, self.__class__.__name__)

            # Check if weight or altitude is a scalar (not an array)
            scalar_weight = isinstance(weight, numbers.Real)
            scalar_altitude = isinstance(altitude, numbers.Real)
            scalar = scalar_weight and scalar_altitude

            if weight is not None and weight is not np.ma.masked:
                weight = np.ma.array(weight, copy=True, dtype=np.double, ndmin=1)
            else:
                weight = np.ma.array(data=[0.0], dtype=np.double, mask=True)


            if lookup is None:
                # Generate an array of velocity speed values for given parameters:
                array = self._build_array(weight, mask=True)
            else:
                # Build interpolation grid
                x = sorted(lookup['weight'].keys())
                y = lookup['altitude']
                z = np.array([lookup['weight'][xi] for xi in x], dtype=np.float)
                interp = scipy.interpolate.RegularGridInterpolator(
                    (x, y), z,
                    bounds_error=False,
                    fill_value=np.nan,
                )
                # Convert the aircraft weight to match the lookup table:
                if not self.weight_unit == ut.KG:
                    weight *= ut.multiplier(ut.KG, self.weight_unit)
                # Interpolate the given wieghts and altitudes
                array = interp((weight, altitude))
                # Mask values outside the table lookup
                array = np.ma.masked_invalid(array)
                # Round to the nearest int
                array = array.round().astype(np.int)

            return array[0] if scalar else array

        if name in ('vmo', 'mmo'):
            altitude = kwargs['altitude']
            scalar = isinstance(altitude, (int, float))
            altitude = np.ma.array(altitude, ndmin=1)

            # Attempt to lookup values from standard tables:
            try:
                lookup = self.tables[name]
            except KeyError:
                lookup = None
                logger.error("Velocity speed table '%s' has no '%s' entry.",
                             self.__class__.__name__, name)

            # Generate an array of velocity speed values for given parameters:
            if lookup is None:
                array = self._build_array(altitude, mask=True)
            elif isinstance(lookup, (int, float)):
                array = self._build_array(altitude, mask=False, value=lookup)
            elif isinstance(lookup, dict):
                x, y = lookup['altitude'], lookup['speed']
                array = np.interp(altitude, x, y, np.nan, np.nan)
                array = np.ma.fix_invalid(array, mask=altitude.mask, fill_value=0.0)
            else:
                raise ValueError('Invalid v-speed table structure.')

            if not name == 'mmo':
                array = array.round().astype(np.int)
            return array[0] if scalar else array

        raise ValueError('Unknown velocity speed table name: %s', name)

    def _determine_detents(self, name):
        '''
        Look up the defined detents for the specified table.

        :param name: the name of the table to look up detents for.
        :type name: string
        :returns: a list of detents available for the table.
        :rtype: list
        '''
        detents = set()
        for table in self.tables, self.fallback:
            if name in table:
                detents.update(table[name].keys())
        detents.discard('weight')
        return sorted(detents)

    def v2(self, detent, weight=None):
        '''
        Look up values from tables for V2.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param detent: flap or configuration detent to use in look-up.
        :type detent: string
        :param weight: weight of the aircraft.
        :type weight: float or np.ma.array
        :returns: one or more values of V2.
        :rtype: float or np.ma.array
        :raises: KeyError -- when table or flap/conf detents is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._determine_vspeed('v2', detent=detent, weight=weight)

    def vref(self, detent, weight=None):
        '''
        Look up values from tables for Vref.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param detent: flap or configuration detent to use in look-up.
        :type detent: string
        :param weight: weight of the aircraft.
        :type weight: float or np.ma.array
        :returns: one or more values of Vref.
        :rtype: float or np.ma.array
        :raises: KeyError -- when table or flap/conf detents is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._determine_vspeed('vref', detent=detent, weight=weight)

    def vapp(self, detent, weight=None):
        '''
        Look up values from tables for Vapp.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param detent: flap or configuration detent to use in look-up.
        :type detent: string
        :param weight: weight of the aircraft.
        :type weight: float or np.ma.array
        :returns: one or more values of Vapp.
        :rtype: float or np.ma.array
        :raises: KeyError -- when table or flap/conf detents is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._determine_vspeed('vapp', detent=detent, weight=weight)

    def vls(self, detent, weight=None, cg=None):
        '''
        Look up values from tables for VLS.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param detent: flap or configuration detent to use in look-up.
        :type detent: string
        :param weight: weight of the aircraft.
        :type weight: float or np.ma.array
        :returns: one or more values of Vapp.
        :rtype: float or np.ma.array
        :raises: KeyError -- when table or flap/conf detents is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._determine_vspeed('vls', detent=detent, weight=weight, cg=cg)

    def vls_clean(self, weight, altitude):
        '''
        Look up values from tables for VLS clean.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param weight: weight of the aircraft.
        :type weight: float or np.ma.array
        :param altitude: altitude of the aircraft.
        :type altitude: float or np.ma.array
        :returns: one or more values of VLS.
        :rtype: int or np.ma.array
        :raises: KeyError -- when table is not found.
        :raises: ValueError -- when weight units cannot be converted.
        '''
        return self._determine_vspeed('vls_clean', weight=weight, altitude=altitude)

    def vmo(self, altitude):
        '''
        Look up values from tables for VMO.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param altitude: pressure altitude.
        :type altitude: float or np.ma.array
        :returns: one or more values of VMO.
        :rtype: float or np.ma.array
        '''
        return self._determine_vspeed('vmo', altitude=altitude)

    def mmo(self, altitude):
        '''
        Look up values from tables for MMO.

        Will use interpolation and convert units if necessary.

        A masked array or value will be returned if provided parameter arrays
        are outside of ranges defined within the lookup tables.

        :param altitude: pressure altitude.
        :type altitude: float or np.ma.array
        :returns: one or more values of MMO.
        :rtype: float or np.ma.array
        '''
        return self._determine_vspeed('mmo', altitude=altitude)

    @property
    def v2_detents(self):
        '''
        Provides a list of available flap/conf detents for V2.

        :returns: a list of flap/conf detents.
        :rtype: list
        '''
        return self._determine_detents('v2')

    @property
    def vref_detents(self):
        '''
        Provides a list of available flap/conf detents for Vref.

        :returns: a list of flap/conf detents.
        :rtype: list
        '''
        return self._determine_detents('vref')

    @property
    def vapp_detents(self):
        '''
        Provides a list of available flap/conf detents for Vapp.

        :returns: a list of flap/conf detents.
        :rtype: list
        '''
        return self._determine_detents('vapp')

    @property
    def vls_detents(self):
        '''
        Provides a list of available flap/conf detents for Vapp.

        :returns: a list of flap/conf detents.
        :rtype: list
        '''
        return self._determine_detents('vls')