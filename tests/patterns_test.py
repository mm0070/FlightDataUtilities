import unittest

from flightdatautilities.patterns import (
    expand_combinations,
    find_combinations,
    get_pattern,
    group_parameter_names,
    match_options,
    param_matches,
    parameter_pattern_map,
    parse_options,
    unique_parameter_combinations,
    wildcard_match,
)


class TestMatchOptions(unittest.TestCase):

    def test_match_options(self):
        self.assertEqual(match_options([], ['Altitude Radio',
                                            'Altitude Radio (L)',
                                            'Pitch']),
                         ['Altitude Radio', 'Pitch'])
        self.assertEqual(match_options(['(L)'], ['Altitude Radio',
                                                 'Altitude Radio (L)',
                                                 'ILS Localizer',
                                                 'ILS Localizer (L)']),
                         ['Altitude Radio (L)',
                          'ILS Localizer (L)'])
        self.assertEqual(match_options(['(L)', '(1)'], ['Altitude Radio',
                                                        'Altitude Radio (L)',
                                                        'Altitude Radio (L) (1)']),
                         ['Altitude Radio (L) (1)'])


class TestExpandCombinations(unittest.TestCase):

    def test_expand_combinations(self):
        alt_rads = ['Altitude Radio (A)',
                    'Altitude Radio (B)',
                    'Altitude Radio (C)']
        self.assertEqual(expand_combinations(2, alt_rads),
                         [['Altitude Radio (A)', 'Altitude Radio (B)'],
                          ['Altitude Radio (A)', 'Altitude Radio (C)'],
                          ['Altitude Radio (B)', 'Altitude Radio (C)']])


class TestWildcardMatch(unittest.TestCase):

    def test_wildcard_match(self):
        params = [
            'Altitude Selected',
            'Altitude Selected (1)',
            'Altitude Selected (FMC)',
            'Altitude Selected (Bad)',
            'Altitude STD',
            'Brake (L) Pressure Inboard',
            'Brake (R) Pressure Ourboard',
            'ILS Localizer (L) (1)',
            'ILS Localizer (L) (2)',
            'ILS Localizer (L) (Capt)',
            'ILS Localizer (L)',
            'ILS Localizer (R) (1)',
            'ILS Localizer (R)',
            'ILS Localizer Beam Anomaly',
            'ILS Localizer Deviation Warning',
            'ILS Localizer Engaged',
            'ILS Localizer Test Tube Inhibit',
            'ILS Localizer',
            'Rate of Climb',
            'Gear Down',
            'Gear (R) Down',
            'Gear (N) Down',
            'Gear (L) Down'
        ]
        # exact match
        self.assertEqual(wildcard_match('ILS Localizer', params),
                         ['ILS Localizer'])
        # test single char match
        self.assertEqual(wildcard_match('ILS Localizer (*)', params),
                         ['ILS Localizer',
                          'ILS Localizer (L)',
                          'ILS Localizer (R)'])

        self.assertEqual(wildcard_match('ILS Localizer (*)', params, missing=False),
                         ['ILS Localizer (L)',
                          'ILS Localizer (R)'])
        # test two wildcards
        self.assertEqual(wildcard_match('ILS Localizer (*) (1)', params),
                         ['ILS Localizer (L) (1)',
                          'ILS Localizer (R) (1)'])
        self.assertEqual(wildcard_match('ILS Localizer (*) (*)', params),
                         ['ILS Localizer',
                          'ILS Localizer (L)',
                          'ILS Localizer (L) (1)',
                          'ILS Localizer (L) (2)',
                          'ILS Localizer (L) (Capt)',
                          'ILS Localizer (R)',
                          'ILS Localizer (R) (1)'])

        self.assertEqual(wildcard_match('ILS Localizer (*) (*)', params,
                                        missing=False),
                         ['ILS Localizer (L) (1)',
                          'ILS Localizer (L) (2)',
                          'ILS Localizer (L) (Capt)',
                          'ILS Localizer (R) (1)'])

        self.assertEqual(wildcard_match('ILS Localizer (L) (*)', params),
                         ['ILS Localizer (L)',
                          'ILS Localizer (L) (1)',
                          'ILS Localizer (L) (2)',
                          'ILS Localizer (L) (Capt)'])

        self.assertEqual(wildcard_match('ILS Localizer (L) (*)', params,
                                        missing=False),
                         ['ILS Localizer (L) (1)',
                          'ILS Localizer (L) (2)',
                          'ILS Localizer (L) (Capt)'])

        self.assertEqual(wildcard_match('Gear (*) Down', params),
                        ['Gear (L) Down',
                         'Gear (N) Down',
                         'Gear (R) Down',
                         'Gear Down'])

        self.assertEqual(wildcard_match('Gear (*) Down', params, missing=False),
                        ['Gear (L) Down',
                         'Gear (N) Down',
                         'Gear (R) Down'])

        self.assertEqual(wildcard_match('Altitude (*) Selected (*)', params),
                         ['Altitude Selected',
                          'Altitude Selected (1)',
                          'Altitude Selected (FMC)'])

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


class TestParseOptions(unittest.TestCase):

    def test_parse_options(self):
        self.assertEqual(parse_options('Airspeed'), [])
        self.assertEqual(parse_options('ILS Localizer (1)'), ['(1)'])
        self.assertEqual(parse_options('Airspeed Selected (1) (Capt)'),
                                       ['(1)', '(Capt)'])
        self.assertEqual(
            parse_options('Airspeed Selected (1) (Capt)', options=['(FO)']),
            [])
        self.assertEqual(
            parse_options('Airspeed Selected (1) (FO)',
                          options=['(1)', '(2)', '(A)', '(B)', '(Capt)']),
            ['(1)'])

class TestUniqueParameterCombinations(unittest.TestCase):

    def test_unique_parameter_combinations(self):
        self.assertEqual(
            unique_parameter_combinations([['Airspeed'],
                                           ['Airspeed', 'Pitch'],
                                           ['Airspeed', 'Airspeed']]),
            [['Airspeed'],
             ['Airspeed', 'Pitch']])


class TestFindCombinations(unittest.TestCase):

    def test_find_combinations(self):
        parameters = [
            'Airspeed',
            'Altitude Radio (A)',
            'Altitude Radio (B)',
            'Altitude Radio (C)',
            'Eng (1) Fuel Flow',
            'Eng (1) Gas Temp',
            'Eng (1) N1',
            'Eng (2) Fuel Flow',
            'Eng (2) Gas Temp',
            'Eng (2) N1',
            'Eng (3) Gas Temp',
            'Heading',
            'Pitch',
        ]

        self.assertEqual(find_combinations(['Heading', 'Airspeed'], parameters,
                                           additional_patterns=['Flap Angle (L)']),
                         [])

        self.assertEqual(
            find_combinations(['Airspeed', 'Heading'], parameters),
            [['Airspeed', 'Heading']])
        self.assertEqual(find_combinations(['Airspeed', 'Heading'], parameters,
                                           additional_patterns=['Pitch']),
                         [['Airspeed', 'Heading', 'Pitch']])
        self.assertEqual(find_combinations(['Eng (*) N1', 'Heading'], parameters,
                                           additional_patterns=['Pitch']),
                         [['Eng (1) N1', 'Heading', 'Pitch'],
                          ['Eng (2) N1', 'Heading', 'Pitch'],])
        self.assertEqual(find_combinations(['Eng (*) N1', 'Eng (*) Gas Temp'],
                                           parameters,
                                           additional_patterns=['Pitch']),
                         [['Eng (1) N1', 'Eng (1) Gas Temp', 'Pitch'],
                          ['Eng (2) N1', 'Eng (2) Gas Temp', 'Pitch'],])
        self.assertEqual(find_combinations(['Airspeed', 'Heading'],
                                           parameters,
                                           additional_patterns=['Eng (*) Gas Temp']),
                         [['Airspeed', 'Heading', 'Eng (1) Gas Temp']])
        self.assertEqual(
            find_combinations(['Eng (*) N1', 'Eng (*) Gas Temp'], parameters,
                              additional_patterns=['Eng (*) Fuel Flow']),
            [['Eng (1) N1', 'Eng (1) Gas Temp', 'Eng (1) Fuel Flow'],
             ['Eng (2) N1', 'Eng (2) Gas Temp', 'Eng (2) Fuel Flow'],])
        self.assertEqual(
            find_combinations(['Altitude Radio (*)', 'Altitude Radio (*)'],
                              parameters, additional_patterns=['Pitch']),
            [['Altitude Radio (A)', 'Altitude Radio (B)', 'Pitch'],
             ['Altitude Radio (A)', 'Altitude Radio (C)', 'Pitch'],
             ['Altitude Radio (B)', 'Altitude Radio (C)', 'Pitch']])
        self.assertEqual(
            find_combinations(['Flap Lever', 'Flap Angle (*)'],
                              ['Flap Angle', 'Flap Channel Fault (3)',
                               'Flap Channel Fault (4)', 'Flap Lever']),
            [['Flap Lever', 'Flap Angle']])
        self.assertEqual(find_combinations(['Elevator (L)', 'Elevator (*)'],
                                           ['Elevator (L)', 'Elevator (R)']),
                         [['Elevator (L)', 'Elevator (R)']])

class TestParamMatches:
    def test_match(self):
        param = 'Altitude Radio'
        pattern = 'Altitude Radio (*) (*)'
        assert param_matches(pattern, param)

    def test_no_match(self):
        param = 'Altitude Radio A'
        pattern = 'Altitude Radio (*) (*)'
        assert not param_matches(pattern, param)

    def test_match_strictly(self):
        param = 'Altitude Radio'
        pattern = 'Altitude Radio (*) (*)'
        assert not param_matches(pattern, param, missing=False)
        assert param_matches(pattern, 'Altitude Radio (A) (1)', missing=False)
