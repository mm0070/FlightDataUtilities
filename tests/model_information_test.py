# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Unit tests for aircraft model information tables and functions.
'''

##############################################################################
# Imports


import numpy as np
import unittest

from flightdatautilities import model_information as mi


##############################################################################
# Test Cases


class TestFlapInformation(unittest.TestCase):

    def test__get_flap_detents(self):
        detents = mi.get_flap_detents()
        # We expect to have quite a lot of detents:
        self.assertGreater(len(detents), 25)
        self.assertLess(len(detents), 50)
        # Maximum angle without percentage values:
        self.assertLessEqual(max(set(detents) - set((50, 100))), 45)
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # Must have special percent values for Hercules:
        self.assertIn(50, detents)
        self.assertIn(100, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_flap_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_flap_map, None, None, None)
        self.assertRaises(KeyError, mi.get_flap_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = mi.get_flap_map(None, 'A340-500', 'A340')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))
        # Check the same again for something with a floating-point flap:
        x = mi.get_flap_map(None, '1900D', '1900')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))


class TestSlatInformation(unittest.TestCase):

    def test__get_slat_detents(self):
        detents = mi.get_slat_detents()
        # We expect to a certain number of values:
        self.assertGreater(len(detents), 10)
        self.assertLess(len(detents), 50)
        # Maximum angle without percentage values:
        self.assertLessEqual(max(set(detents) - set((50, 100))), 35)
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # Must have special percent values for B787:
        self.assertIn(50, detents)
        self.assertIn(100, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_slat_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_slat_map, None, None, None)
        self.assertRaises(KeyError, mi.get_slat_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = mi.get_slat_map(None, 'A340-500', 'A340')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))
        # Check the same again for something with a floating-point slat:
        x = mi.get_slat_map(None, None, 'DC-9')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))


class TestAileronInformation(unittest.TestCase):

    def test__get_aileron_detents(self):
        detents = mi.get_aileron_detents()
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_aileron_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_aileron_map, None, None, None)
        self.assertRaises(KeyError, mi.get_aileron_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = mi.get_aileron_map(None, 'A340-500', 'A340')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))


class TestConfInformation(unittest.TestCase):

    def test__get_conf_detents(self):
        detents = mi.get_conf_detents()
        # We expect all values to be in the available set:
        available = mi.AVAILABLE_CONF_STATES.itervalues()
        self.assertLessEqual(set(detents), set(available))
        # Must have a value for the retracted state:
        self.assertIn('0', detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_conf_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_conf_map, None, None, None)
        self.assertRaises(KeyError, mi.get_conf_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = mi.get_conf_map(None, 'A340-500', 'A340')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))

    def test__get_conf_angles(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_conf_angles, None, None, None)
        self.assertRaises(KeyError, mi.get_conf_angles, '', '', '')
        # Ensure that the provided key argument is correct:
        args = (None, None, 'A380')
        try:
            for key in ('both', 'state', 'value'):
                mi.get_conf_angles(*args, key=key)
        except ValueError:
            self.fail('ValueError from get_conf_angles() for valid key.')
        self.assertRaises(ValueError, mi.get_lever_angles, *args, key='invalid')
        # Ensure that we get the expected structure returned:
        for key, types in ('both', tuple), ('state', str), ('value', (float, int)):
            x = mi.get_conf_angles(None, None, 'A380', key=key)
            self.assertTrue(all(isinstance(v, types) for v in x.iterkeys()))
            self.assertTrue(all(isinstance(v, tuple) for v in x.itervalues()))

    def test__conf_maps_integrity(self):
        for t in 'MODEL', 'SERIES', 'FAMILY':
            m = getattr(mi, 'CONF_%s_MAP' % t)
            for name, x in m.iteritems():
                # Ensure model, series or family name is a string:
                self.assertIsInstance(name, str)
                # Ensure the mapping of states is a dictionary:
                self.assertIsInstance(x, dict)
                # Ensure that all the states are strings:
                self.assertTrue(all(isinstance(k, str) for k in x.iterkeys()))
                # Ensure all values are tuples of length 2 or 3, but the same:
                self.assertTrue(all(isinstance(v, tuple) for v in x.itervalues()))
                self.assertTrue(all(2 <= len(v) <= 3 for v in x.itervalues()))
                self.assertEqual(len(set(len(v) for v in x.itervalues())), 1)
                # Ensure all states are in the available conf states constant:
                available = mi.AVAILABLE_CONF_STATES.itervalues()
                self.assertLessEqual(set(x.iterkeys()), set(available))
                # Ensure that the angles are found in related mappings:
                length = len(x.itervalues().next())
                s0 = set(v[0] for v in x.itervalues())
                s1 = set(getattr(mi, 'SLAT_%s_MAP' % t)[name])
                self.assertEqual(s0, s1, 'Broken slat values for %s' % name)
                f0 = set(v[1] for v in x.itervalues())
                f1 = set(getattr(mi, 'FLAP_%s_MAP' % t)[name])
                self.assertEqual(f0, f1, 'Broken flap values for %s' % name)
                if length == 3:
                    a0 = set(v[2] for v in x.itervalues())
                    a1 = set(getattr(mi, 'AILERON_%s_MAP' % t)[name])
                    self.assertEqual(a0, a1, 'Broken aileron values for %s' % name)


class TestLeverInformation(unittest.TestCase):

    def test__get_lever_detents(self):
        detents = mi.get_lever_detents()
        # Must have a value for the retracted state:
        self.assertIn('0', detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_lever_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_lever_map, None, None, None)
        self.assertRaises(KeyError, mi.get_lever_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = mi.get_lever_map(None, 'CRJ900', 'CRJ')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.iterkeys()))
        self.assertTrue(all(isinstance(v, str) for v in x.itervalues()))

    def test__get_lever_angles(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, mi.get_lever_angles, None, None, None)
        self.assertRaises(KeyError, mi.get_lever_angles, '', '', '')
        # Ensure that the provided key argument is correct:
        args = (None, None, 'B787')
        try:
            for key in ('both', 'state', 'value'):
                mi.get_lever_angles(*args, key=key)
        except ValueError:
            self.fail('ValueError from get_lever_angles() for valid key.')
        self.assertRaises(ValueError, mi.get_lever_angles, *args, key='invalid')
        # Ensure that we get the expected structure returned:
        for key, types in ('both', tuple), ('state', str), ('value', (float, int)):
            x = mi.get_lever_angles(None, None, 'Global', key=key)
            self.assertTrue(all(isinstance(v, types) for v in x.iterkeys()))
            self.assertTrue(all(isinstance(v, tuple) for v in x.itervalues()))

    def test__lever_maps_integrity(self):
        for t in 'MODEL', 'SERIES', 'FAMILY':
            m = getattr(mi, 'LEVER_%s_MAP' % t)
            for name, x in m.iteritems():
                self.assertIsInstance(name, str)
                self.assertIsInstance(x, dict)
                self.assertTrue(all(isinstance(k, tuple) for k in x.iterkeys()))
                self.assertTrue(all(isinstance(v, tuple) for v in x.itervalues()))
                self.assertTrue(all(len(k) == 2 for k in x.iterkeys()))
                self.assertTrue(all(len(v) == 2 for v in x.itervalues()))
                # Ensure that the angles are found in related mappings:
                length = len(x.itervalues().next())
                s0 = set(v[0] for v in x.itervalues())
                s1 = set(getattr(mi, 'SLAT_%s_MAP' % t)[name])
                self.assertEqual(s0, s1, 'Broken slat values for %s' % name)
                f0 = set(v[1] for v in x.itervalues())
                f1 = set(getattr(mi, 'FLAP_%s_MAP' % t)[name])
                self.assertEqual(f0, f1, 'Broken flap values for %s' % name)
