# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Unit tests for aircraft VMO/MMO tables and functions.
'''

##############################################################################
# Imports


import numpy as np
import unittest

from flightdatautilities import aircrafttables as at
from flightdatautilities.aircrafttables.interfaces import MaximumSpeed_Fixed


##############################################################################
# Test Configuration


def setUpModule():
    at.configure(package='flightdatautilities.aircrafttables')


##############################################################################
# Test Suite


class TestMaximumSpeed_Fixed(unittest.TestCase):

    def test__get_mmo_array(self):
        alt_std = np.ma.arange(10000, 15000, dtype=np.float)

        table = MaximumSpeed_Fixed(vmo=None, mmo=None)
        mmo = table.get_mmo_array(alt_std)
        self.assertTrue(np.ma.is_masked(mmo))

        table = MaximumSpeed_Fixed(vmo=340, mmo=0.82)
        mmo = table.get_mmo_array(alt_std)
        self.assertFalse(np.ma.is_masked(mmo))
        self.assertTrue(np.ma.all(mmo == 0.82))

    def test__get_vmo_array(self):
        alt_std = np.ma.arange(10000, 15000, dtype=np.float)

        table = MaximumSpeed_Fixed(vmo=None, mmo=None)
        vmo = table.get_vmo_array(alt_std)
        self.assertTrue(np.ma.is_masked(vmo))

        table = MaximumSpeed_Fixed(vmo=340, mmo=0.82)
        vmo = table.get_vmo_array(alt_std)
        self.assertFalse(np.ma.is_masked(vmo))
        self.assertTrue(np.ma.all(vmo == 340))

    def test__get_mmo_array__b737_classic(self):
        alt_std = np.ma.arange(10000, 15000, dtype=np.float)

        table = at.get_max_speed_table(family='B737 Classic')
        mmo = table.get_mmo_array(alt_std)
        self.assertFalse(np.ma.is_masked(mmo))
        self.assertTrue(np.ma.all(mmo == 0.82))

    def test__get_mmo_value__b737_classic(self):
        table = at.get_max_speed_table(family='B737 Classic')
        mmo = table.get_mmo_value(10000)
        self.assertFalse(np.ma.is_masked(mmo))
        self.assertEqual(mmo, 0.82)

    def test__get_vmo_array__b737_classic(self):
        alt_std = np.ma.arange(10000, 15000, dtype=np.float)

        table = at.get_max_speed_table(family='B737 Classic')
        vmo = table.get_vmo_array(alt_std)
        self.assertFalse(np.ma.is_masked(vmo))
        self.assertTrue(np.ma.all(vmo == 340))

    def test__get_vmo_value__b737_classic(self):
        table = at.get_max_speed_table(family='B737 Classic')
        vmo = table.get_vmo_value(10000)
        self.assertFalse(np.ma.is_masked(vmo))
        self.assertEqual(vmo, 340)
