##############################################################################

'''
Unit tests for aircraft model information tables and functions.
'''

##############################################################################
# Imports


import unittest

from flightdatautilities import aircrafttables as at

from flightdatautilities.aircrafttables import model_information as mi


##############################################################################
# Test Configuration


def setUpModule():
    at.configure(package='flightdatautilities.aircrafttables')


##############################################################################
# Test Cases


class TestFlapInformation(unittest.TestCase):

    def test__get_flap_detents(self):
        detents = at.get_flap_detents()
        # All detents must be integers or floats:
        self.assertTrue(all(isinstance(d, (int, float)) for d in detents))
        # We expect to have quite a lot of detents:
        self.assertGreater(len(detents), 10)
        self.assertLess(len(detents), 20)
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_flap_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_flap_map, None, None, None)
        self.assertRaises(KeyError, at.get_flap_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_flap_map(None, 'B737-300', 'B737 Classic')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.keys()))
        self.assertTrue(all(isinstance(v, str) for v in x.values()))


class TestSlatInformation(unittest.TestCase):

    def test__get_slat_detents(self):
        detents = at.get_slat_detents()
        # All detents must be integers or floats:
        self.assertTrue(all(isinstance(d, (int, float)) for d in detents))
        # We expect to a certain number of values:
        self.assertGreater(len(detents), 0)
        self.assertLess(len(detents), 10)
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_slat_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_slat_map, None, None, None)
        self.assertRaises(KeyError, at.get_slat_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_slat_map(None, 'A330-300', 'A330')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.keys()))
        self.assertTrue(all(isinstance(v, str) for v in x.values()))


class TestAileronInformation(unittest.TestCase):

    def test__get_aileron_detents(self):
        detents = at.get_aileron_detents()
        # All detents must be integers or floats:
        self.assertTrue(all(isinstance(d, (int, float)) for d in detents))
        # Must have a value for the retracted state:
        self.assertIn(0, detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_aileron_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_aileron_map, None, None, None)
        self.assertRaises(KeyError, at.get_aileron_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_aileron_map(None, 'A330-300', 'A330')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.keys()))
        self.assertTrue(all(isinstance(v, str) for v in x.values()))


class TestConfInformation(unittest.TestCase):

    def test__get_conf_detents(self):
        detents = at.get_conf_detents()
        # All detents must be strings:
        self.assertTrue(all(isinstance(d, str) for d in detents))
        # We expect all values to be in the available set:
        available = at.constants.AVAILABLE_CONF_STATES.values()
        self.assertLessEqual(set(detents), set(available))
        # Must have a value for the retracted state:
        self.assertIn('0', detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_conf_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_conf_map, None, None, None)
        self.assertRaises(KeyError, at.get_conf_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_conf_map(None, 'A330-300', 'A330')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.keys()))
        self.assertTrue(all(isinstance(v, str) for v in x.values()))

    def test__get_conf_angles(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_conf_angles, None, None, None)
        self.assertRaises(KeyError, at.get_conf_angles, '', '', '')
        # Ensure that the provided key argument is correct:
        args = (None, None, 'A330')
        try:
            for key in ('both', 'state', 'value'):
                at.get_conf_angles(*args, key=key)
        except ValueError:
            self.fail('ValueError from get_conf_angles() for valid key.')
        self.assertRaises(ValueError, at.get_lever_angles, *args, key='invalid')
        # Ensure that we get the expected structure returned:
        for key, types in ('both', tuple), ('state', str), ('value', (float, int)):
            x = at.get_conf_angles(None, None, 'A330', key=key)
            self.assertTrue(all(isinstance(v, types) for v in x.keys()))
            self.assertTrue(all(isinstance(v, tuple) for v in x.values()))

    def test__conf_maps_integrity(self):
        for t in 'MODEL', 'SERIES', 'FAMILY':
            m = getattr(mi, 'CONF_%s_MAP' % t)
            for name, x in m.items():
                # Ensure model, series or family name is a string:
                self.assertIsInstance(name, str)
                # Ensure the mapping of states is a dictionary:
                self.assertIsInstance(x, dict)
                # Ensure that all the states are strings:
                self.assertTrue(all(isinstance(k, str) for k in x.keys()))
                # Ensure all values are tuples of length 2 or 3, but the same:
                self.assertTrue(all(isinstance(v, tuple) for v in x.values()))
                self.assertTrue(all(2 <= len(v) <= 3 for v in x.values()))
                self.assertEqual(len(set(len(v) for v in x.values())), 1)
                # Ensure all states are in the available conf states constant:
                available = at.constants.AVAILABLE_CONF_STATES.values()
                self.assertLessEqual(set(x.keys()), set(available))
                # Ensure that the angles are found in related mappings:
                length = len(next(iter(x.values())))
                s0 = set(v[0] for v in x.values())
                s1 = set(getattr(mi, 'SLAT_%s_MAP' % t)[name])
                self.assertEqual(s0, s1, 'Broken slat values for %s' % name)
                f0 = set(v[1] for v in x.values())
                f1 = set(getattr(mi, 'FLAP_%s_MAP' % t)[name])
                self.assertEqual(f0, f1, 'Broken flap values for %s' % name)
                if length == 3:
                    a0 = set(v[2] for v in x.values())
                    a1 = set(getattr(mi, 'AILERON_%s_MAP' % t)[name])
                    self.assertEqual(a0, a1, 'Broken aileron values for %s' % name)


class TestLeverInformation(unittest.TestCase):

    def test__get_lever_detents(self):
        detents = at.get_lever_detents()
        # All detents must be strings:
        self.assertTrue(all(isinstance(d, str) for d in detents))
        # Must have a value for the retracted state:
        self.assertIn('0', detents)
        # No duplicates:
        self.assertEqual(len(set(detents)), len(detents))

    def test__get_lever_map(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_lever_map, None, None, None)
        self.assertRaises(KeyError, at.get_lever_map, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_lever_map(None, 'Global Express XRS', 'Global')
        self.assertIsInstance(x, dict)
        self.assertTrue(all(isinstance(k, (float, int)) for k in x.keys()))
        self.assertTrue(all(isinstance(v, str) for v in x.values()))

    def test__get_lever_angles(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_lever_angles, None, None, None)
        self.assertRaises(KeyError, at.get_lever_angles, '', '', '')
        # Ensure that the provided key argument is correct:
        args = (None, None, 'Global')
        try:
            for key in ('both', 'state', 'value'):
                at.get_lever_angles(*args, key=key)
        except ValueError:
            self.fail('ValueError from get_lever_angles() for valid key.')
        self.assertRaises(ValueError, at.get_lever_angles, *args, key='invalid')
        # Ensure that we get the expected structure returned:
        for key, types in ('both', tuple), ('state', str), ('value', (float, int)):
            x = at.get_lever_angles(None, None, 'Global', key=key)
            self.assertTrue(all(isinstance(v, types) for v in x.keys()))
            self.assertTrue(all(isinstance(v, tuple) for v in x.values()))

    def test__lever_maps_integrity(self):
        for t in 'MODEL', 'SERIES', 'FAMILY':
            m = getattr(mi, 'LEVER_%s_MAP' % t)
            for name, x in m.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(x, dict)
                self.assertTrue(all(isinstance(k, tuple) for k in x.keys()))
                self.assertTrue(all(isinstance(v, tuple) for v in x.values()))
                self.assertTrue(all(len(k) == 2 for k in x.keys()))
                self.assertTrue(all(len(v) == 3 for v in x.values()))
                # Ensure that the angles are found in related mappings:
                s0 = set(v[0] for v in x.values() if v[0] is not None)
                if s0:
                    s1 = set(getattr(mi, 'SLAT_%s_MAP' % t)[name])
                    self.assertEqual(s0, s1, 'Broken slat values for %s' % name)
                f0 = set(v[1] for v in x.values() if v[1] is not None)
                if f0:
                    f1 = set(getattr(mi, 'FLAP_%s_MAP' % t)[name])
                    self.assertEqual(f0, f1, 'Broken flap values for %s' % name)
                a0 = set(v[2] for v in x.values() if v[2] is not None)
                if a0:
                    a1 = set(getattr(mi, 'AILERON_%s_MAP' % t)[name])
                    self.assertEqual(a0, a1, 'Broken aileron values for %s' % name)
                if not any((s0, f0, a0)):
                    self.fail('Broken lever map for %s' % name)


class TestStabilizerInformation(unittest.TestCase):

    def test__get_stabilizer_limits(self):
        # Ensure that we raise an exception if no valid arguments are provided:
        self.assertRaises(KeyError, at.get_stabilizer_limits, None, None, None)
        self.assertRaises(KeyError, at.get_stabilizer_limits, '', '', '')
        # Ensure we have what looks like a values mapping dictionary:
        x = at.get_stabilizer_limits(None, 'B737-600', 'B737 NG')
        self.assertIsInstance(x, tuple)
        self.assertTrue(all(isinstance(v, (float, int)) for v in x))
        self.assertEqual(len(x), 2)
