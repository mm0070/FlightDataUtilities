import unittest

from flightdatautilities.patterns import wildcard_match

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
        