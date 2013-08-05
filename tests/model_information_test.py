import numpy as np
import unittest

from flightdatautilities.model_information import (
    get_flap_detents, get_flap_values_mapping)


class TestAttribute(object):
    '''
    For testing Series and Family attributes
    '''
    def __init__(self, value=None):
        self.value = value
Family = Series = TestAttribute

class TestParam(object):
    def __init__(self, array=[]):
        self.array = array
P = TestParam


class TestFlap(unittest.TestCase):
    def test_get_flap_map(self):
        detents = get_flap_detents()
        # must be lots of them
        self.assertGreater(len(detents), 25)
        self.assertLess(len(detents), 100)
        self.assertIn(0, detents)
        self.assertIn(45, detents)
        self.assertIn(50, detents) # herc
        # no duplication
        self.assertEqual(len(set(detents)), len(detents))
        
    def test_get_flap_values_mapping_raises_keyerror(self):
        # empty attributes
        self.assertRaises(KeyError, get_flap_values_mapping,
                          Series(), Family(), None)

    def test_get_flap_values_mapping_rounding(self):
        # empty attributes
        res = get_flap_values_mapping(Series(), Family(), 
                                      P(np.ma.arange(10)))
        self.assertEqual(res, {0: '0', 5: '5', 10: '10'})
        # invalid attributes
        res = get_flap_values_mapping(Series('NULL'), Family('NULL'),
                                      P(np.ma.arange(10, 20)))
        self.assertEqual(res, {10: '10', 15: '15', 20: '20'})
    
    def test_get_flap_values_mapping_hercules(self):
        res = get_flap_values_mapping(Series(), Family('C-130'))
        self.assertEqual(res, {0: '0', 50: '50', 100: '100'})
        
    def test_get_flap_values_mapping_hercules(self):
        res = get_flap_values_mapping(Series(), Family('B737 Classic'))    
        self.assertEqual(res, {
            0: '0', 1: '1', 2: '2', 5: '5', 10: '10', 
            15: '15', 25: '25', 30: '30', 40: '40'})
        
    def test_get_flap_series_over_family(self):
        res = get_flap_values_mapping(Series(), Family('ERJ-135/145'))
        self.assertEqual(res, {
            0: '0', 9: '9', 18: '18', 22: '22', 45: '45'})
        # ERJ-135BJ does not have flap 18
        res = get_flap_values_mapping(Series('ERJ-135BJ'), 
                                      Family('ERJ-135/145'))
        self.assertNotIn(18, res)
        self.assertEqual(res, {
            0: '0', 9: '9', 22: '22', 45: '45'})
        
    def test_get_flap_values_mapping_decimal_flaps(self):
        # decimal flap settings keys are floored to nearest integer
        res = get_flap_values_mapping(Series('1900D'), Family())
        self.assertEqual(res, {
            0: '0', 17: '17.5', 35: '35'})
        
        
class TestSlat(unittest.TestCase):
    
    def test_decimal_slats(self):
        #'DC-9':    (0, 17.8, 21)   # FAA TCDS A6WE Rev 28 (DC-9-81 & DC-9-82)
        pass
    