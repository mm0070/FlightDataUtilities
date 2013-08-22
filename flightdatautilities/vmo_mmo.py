'''
VMO/MMO mapping.

This module should possibly be integrated with velocity_speed, but keeping
those algorithms separate makes sense from code readability point of view.
'''
import numpy as np


class VMO(object):
    '''
    Constant VMO/MMO.

    The same value is returned for any pressure altitude.
    '''
    def __init__(self, vmo=None, mmo=None):
        self.vmo = vmo
        self.mmo = mmo

    def get_vmo_mmo(self, press_alt):
        return self.vmo, self.mmo

    def get_vmo_mmo_arrays(self, pres_alt_array):
        vmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)
        mmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)

        if self.vmo:
            vmo_array.fill(self.vmo)
            vmo_array.mask = False

        if self.mmo:
            mmo_array.fill(self.mmo)
            mmo_array.mask = False

        return vmo_array, mmo_array


class VMONone(VMO):
    '''
    No-op lookup: returning masked values for VMO and MMO.
    '''
    def __init__(self):
        self.vmo = None
        self.mmo = None

    def get_vmo_mmo_arrays(self, pres_alt_array):
        vmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)
        mmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)

        return vmo_array, mmo_array


class VMORanges(VMO):
    '''
    Class which calculates VMO/MMO value from a list of values
    '''
    vmo_mmo_table = None

    def get_vmo_mmo(self, press_alt):
        for alt, vmo_mmo in self.vmo_mmo_table:
            if alt and press_alt <= alt:
                break

        # the last value is for the all the bigger altitudes
        if vmo_mmo > 10:
            # The value is VMO
            return vmo_mmo, None
        else:
            # The value is MMO
            return None, vmo_mmo

    def get_vmo_mmo_arrays(self, pres_alt_array):
        '''
        Return 2 arrays of values for VMO and MMO respectively based on
        pressure altitude array.

        If VMO/MMO is not applicable, the coresponding values are masked.
        '''
        def fill_vmo_mmo_array(pres_alt_array, low, high, vmo_mmo, vmo_array,
                               mmo_array):
            if low is not None and high is not None:
                condition = low < pres_alt_array
                condition[pres_alt_array > high] = False
            elif low is None:
                condition = pres_alt_array <= high
            elif high is None:
                condition = low < pres_alt_array

            if vmo_mmo > 10:
                vmo_array[condition] = vmo_mmo
            else:
                mmo_array[condition] = vmo_mmo

        vmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)
        mmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)

        low = None
        for high, vmo_mmo in self.vmo_mmo_table:
            fill_vmo_mmo_array(pres_alt_array, low, high, vmo_mmo, vmo_array,
                               mmo_array)
            low = high

        return vmo_array, mmo_array


class VMOL382(VMO):
    '''
    Calculate VMO based on pressure altitude in feet.

    MMO is not returned for this aircraft.
    '''
    vmo = True
    mmo = False

    def get_vmo_mmo(self, press_alt):
        if press_alt < 17500:
            return 250 + 4 * press_alt / 17500, None
        elif press_alt < 32500:
            return 254 - 52 * (press_alt - 17500) / 15000, None
        else:
            return 202, None

    def get_vmo_mmo_arrays(self, pres_alt_array):
        vmo_array = np.ma.array(np.zeros_like(pres_alt_array))
        mmo_array = np.ma.array(np.zeros_like(pres_alt_array), mask=True)

        condition = pres_alt_array <= 17500
        vmo_array[condition] = 250 + 4 * pres_alt_array[condition] / 17500
        condition = 17500 < pres_alt_array
        condition[pres_alt_array > 32500] = False
        vmo_array[condition] = 254 - 52 * (pres_alt_array[condition] - 17500) \
            / 15000
        condition = 32500 < pres_alt_array
        vmo_array[condition] = 202

        return vmo_array, mmo_array


class VMOGlobalExpress(VMORanges):
    '''
    Return VMO/MMO based on pressure altitude in feet.
    '''
    vmo_mmo_table = (
        (8000, 300),
        (30267, 340),
        (35000, 0.89),
        (41400, 0.88),
        (47000, 0.858),
        (None, 0.842),
    )
    vmo = True
    mmo = True


def get_vmo_procedure(series=None, family=None):
    '''
    Return a VMO class used to calculate the VMO/MMO values.
    '''
    if family in VMO_FAMILIES:
        procedure, args = VMO_FAMILIES[family]

    elif series in VMO_SERIES:
        procedure, args = VMO_SERIES[series]

    else:
        # FIXME: we should raise error
        #raise ValueError(
        #    'No VMO/MMO defined for aircraft family `%s`/series `%s`' %
        #    (family, series))
        return VMONone()

    return procedure(*args)


# FIXME: this should probably be done in a better way (frame settings?)
# VMO/MMO procedures registry
# values are 2-element lists: VMO/MMO class and list of constructor arguments
VMO_FAMILIES = {
    'Lockheed C-130': [VMOL382, []],
    'B737 Classic': [VMO, [340, 0.82]],
    'B737 NG': [VMO, [340, 0.82]],
    'B757': [VMO, [360, 0.86]],
    'B767': [VMO, [360, 0.86]],
}

VMO_SERIES = {
    'F28-0070': [VMONone, []],  # Fokker provides VMO in the frame
    '1900D': [VMONone, []],
    #'1900D': [VMO, [248, 0.48]],  # FIXME: we need verify these
}
