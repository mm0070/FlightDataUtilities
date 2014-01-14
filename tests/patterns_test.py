import unittest

from flightdatautilities.patterns import (
    get_pattern,
    group_parameter_names,
    parameter_pattern_map,
    wildcard_match,
)


class TestWilcardMatch(unittest.TestCase):
        
    def test_wildcard_match(self):
        params = ['ILS Localizer', 
                  'ILS Localizer (R)',
                  'ILS Localizer (L)',
                  'ILS Localizer (L) (Capt)',
                  'Rate of Climb', 
                  'Altitude STD',
                  'Brake (R) Pressure Ourboard', 
                  'Brake (L) Pressure Inboard', 
                  'ILS Localizer Deviation Warning',
                  'ILS Localizer Test Tube Inhibit', 
                  'ILS Localizer Beam Anomaly',
                  'ILS Localizer Engaged']
        # exact match
        res = wildcard_match('ILS Localizer', params)
        self.assertEqual(res, ['ILS Localizer'])
        ### wildcard
        ##res = wildcard_match('ILS Localizer', params)
        ##self.assertEqual(res, [
            ##'ILS Localizer', 'ILS Localizer (L)', 
            ##'ILS Localizer (L) (Capt)', 'ILS Localizer (R)', 
            ##'ILS Localizer Beam Anomaly',  'ILS Localizer Deviation Warning',
            ##'ILS Localizer Engaged', 'ILS Localizer Test Tube Inhibit'])
        # test single char match
        res = wildcard_match('ILS Localizer (*)', params)
        expected_output_star = ['ILS Localizer (L)', 'ILS Localizer (R)']
        
    def test_wildcard_match_multiple_chars(self):
        params = ['Spoiler (%d)' % n for n in range(1,13)]
        res = wildcard_match('Spoiler (*)', params)
        self.assertEqual(len(res), 12)
        
        # ensure without (n) is found
        params.append('Spoiler')
        res = wildcard_match('Spoiler (*)', params)
        self.assertEqual(len(res), 13)
         
        
    def test_wildcard_match_without_brackets(self):
        params = [
            'ILS Frequency',
            'ILS (1) Frequency',
            'ILS (2) Frequency',
            'ILS (Capt) Frequency',
            'ILS (R) Frequency',
            'ILS (L) (Capt) Frequency',
         ]
        
        res = wildcard_match('ILS (*) Frequency', params)
        self.assertIn('ILS Frequency', res)
        self.assertNotIn('ILS (L) (Capt) Frequency', res)
        self.assertEqual(set(res), set(params[0:5]))


class TestGetPattern(unittest.TestCase):
    
    def test_get_pattern(self):
        options = ['(1)', '(2)']
        self.assertEqual(get_pattern('Airspeed', options=options),
                         'Airspeed')
        self.assertEqual(get_pattern('Eng (1) N1', options=options),
                         'Eng (*) N1')
        self.assertEqual(get_pattern('ILS Localizer (2)', options=options),
                         'ILS Localizer (*)')
        self.assertEqual(get_pattern('ILS Localizer (3)', options=options),
                         'ILS Localizer (3)')
        self.assertEqual(get_pattern('Eng (1) N1 (2)', options=options),
                         'Eng (*) N1 (*)')
        self.assertEqual(get_pattern('Eng (*) N1 Max', options=options),
                         'Eng (*) N1 Max')


class TestGroupParameterNames(unittest.TestCase):
    
    def test_group_parameter_names(self):
        options = ['(L)', '(R)']
        self.assertEqual(group_parameter_names(['Airspeed'], options=options),
                         {'Airspeed': ['Airspeed']})
        self.assertEqual(group_parameter_names(['Airspeed', 'Heading'],
                                               options=options),
                         {'Airspeed': ['Airspeed'],
                          'Heading': ['Heading']})
        self.assertEqual(group_parameter_names(['Airspeed',
                                                'Altitude Radio (L)'],
                                               options=options),
                         {'Airspeed': ['Airspeed'],
                          'Altitude Radio (*)': ['Altitude Radio (L)']})
        self.assertEqual(group_parameter_names(['Altitude Radio (L)',
                                                'Altitude Radio (R)'],
                                               options=options),
                         {'Altitude Radio (*)': ['Altitude Radio (L)',
                                                 'Altitude Radio (R)']})


class TestParameterPatternMap(unittest.TestCase):
    
    def test_parameter_pattern_map(self):
        options = ['(L)', '(R)']
        self.assertEqual(parameter_pattern_map(['Airspeed'], options=options),
                         {'Airspeed': 'Airspeed'})
        self.assertEqual(parameter_pattern_map(['Airspeed', 'Heading'],
                                               options=options),
                         {'Airspeed': 'Airspeed',
                          'Heading': 'Heading'})
        self.assertEqual(parameter_pattern_map(['Airspeed',
                                                'Altitude Radio (L)'],
                                               options=options),
                         {'Airspeed': 'Airspeed',
                          'Altitude Radio (L)': 'Altitude Radio (*)'})
        self.assertEqual(parameter_pattern_map(['Altitude Radio (L)',
                                                'Altitude Radio (R)'],
                                               options=options),
                         {'Altitude Radio (L)': 'Altitude Radio (*)',
                          'Altitude Radio (R)': 'Altitude Radio (*)'})

