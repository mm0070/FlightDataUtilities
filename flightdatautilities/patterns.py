import collections
import itertools
import re


OPTIONS = ('(A)', '(B)', '(C)', '(N)', '(L)', '(R)',
           '(Foreign)', '(Local)', '(EFIS)', '(Capt)', '(FO)', '(Aux)', '(AP)',
           '(Blue)', '(Yellow)', '(Green)',
           '(MCP)', '(FMC)', '(PFD)',
           '(Coarse)', '(Fine)',
           '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)',
           '(10)', '(11)', '(12)', '(13)', '(14)', '(15)', '(16)',
           '(1A)', '(1B)', '(2A)', '(2B)', '(3A)', '(3B)', '(4A)', '(4B)')

WILDCARD = '(*)'
WILDCARD_ESCAPE = re.escape(' (*)')
OPTIONS_GROUP = '(?: \\((?:%s)+\\))' % '|'.join(o.strip('()') for o in OPTIONS)


def pattern_regex(pattern, missing=True, prefix=False):
    '''
    Create a regex which matches the pattern.

    :param pattern: Wildcard pattern to match
    :type pattern: String
    :param missing: Whether or not to match variations of the pattern where wildcard options are missing.
    :type missing: bool
    :param prefix: Whether to allow strings that start with the pattern to match.
    :type prefix: bool
    :returns: keys which match pattern
    :rtype: list
    '''
    return re.escape(pattern).replace(
        WILDCARD_ESCAPE, '%s%s' % (OPTIONS_GROUP, '?' if missing else '')) + ('' if prefix else r'\Z')


def wildcard_match(pattern, keys, missing=True, prefix=False):
    '''
    Return subset of keys where wildcard (*) pattern matches.
    Also matches keys where " (*)" is not in the string.

    :param pattern: Wildcard pattern to match
    :type pattern: String
    :param keys: Keys to search within
    :type keys: Iterable of Strings
    :param missing: Whether or not to match variations of the pattern where wildcard options are missing.
    :type missing: bool
    :returns: keys which match pattern
    :rtype: list
    '''
    if not isinstance(keys, (list, tuple, set)):
        raise TypeError('Expected a non-string iterable.')
    if WILDCARD in pattern:
        pass
    elif prefix:
        return sorted({key for key in keys if key.startswith(pattern)})
    else:
        return [pattern] if pattern in keys else []
    re_obj = re.compile(f'(?ms){pattern_regex(pattern, missing=missing, prefix=prefix)}')
    return sorted({key for key in keys if re_obj.match(key)})


def param_matches(pattern, param,  missing=True, prefix=False):
    '''
    Check if param matches the pattern.

    :param pattern: Wildcard pattern to match
    :type pattern: String
    :param param: parameter name
    :type param: String
    :param missing: Whether or not to match variations of the pattern where wildcard options are missing.
    :type missing: bool
    :param prefix: Whether to allow strings that start with the pattern to match.
    :type prefix: bool
    :returns: param matches the pattern
    :rtype: bool
    '''
    return bool(
        re.match(f'(?ms){pattern_regex(pattern, missing=missing, prefix=prefix)}', param)
    )


def is_pattern(pattern):
    '''
    Test if a pattern contains a wildcard.
    '''
    return WILDCARD in pattern


def get_pattern(name, options=OPTIONS):
    '''
    Creates a parameter pattern from name replacing options with wildcards.

    :param name: Parameter name.
    :type name: str
    '''
    pattern = name
    for option in options:
        pattern = pattern.replace(option, WILDCARD)
    return pattern


def parse_options(name, options=OPTIONS):
    '''
    :param options: Optional valid options.
    '''
    matched_options = re.findall(r'(?P<option>\(\w+\))', name)
    if options:
        # The following line loses option ordering.
        #return list(set(matched_options) & set(options))
        supported_options = []
        for matched_option in matched_options:
            if matched_option in options:
                supported_options.append(matched_option)
        return supported_options
    else:
        return matched_options


def group_parameter_names(names, options=OPTIONS):
    '''
    :param names: List of parameter names.
    :type names: [str]
    :returns: Parameter pattern to list of parameter names.
    :rtype: dict
    '''
    pattern_to_names = collections.defaultdict(list)
    for name in names:
        pattern = get_pattern(name, options=options)
        pattern_to_names[pattern].append(name)

    return pattern_to_names


def parameter_pattern_map(names, options=OPTIONS):
    '''
    :param names: List of parameter names.
    :type names: [str]
    :returns: Parameter name to parameter pattern.
    :rtype: dict
    '''
    name_to_pattern = {}
    for name in names:
        pattern = get_pattern(name, options=options)
        name_to_pattern[name] = pattern
    return name_to_pattern


def match_options(options, names):
    '''
    Find names which match options.

    :param options: Options to match.
    :type options: [str]
    :param names: Names containing options.
    :type names: [str]
    :returns: Names which match parameters.
    :rtype: [str]
    '''
    matched_names = []
    for name in names:
        parsed_options = parse_options(name, options=options)
        if parsed_options == options:
            matched_names.append(name)
    return matched_names


def find_combinations(required_patterns, names,
                      additional_patterns=[]):
    '''

    Examples (parameter matches after pattern matching):

    Test: ['Airspeed']
    Reference: ['Heading']
    Result: [['Airspeed', 'Heading']]

    Test: ['Airspeed']
    Reference: ['Heading']
    Additional 1: ['Acceleration Normal']
    Result: [['Airspeed', 'Heading', 'Acceleration Normal']]

    # Expand test if reference is not a pattern.
    Test: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Reference: ['Heading']
    Additional 1: ['Acceleration Normal']
    Result: [['Eng (1) N1', 'Heading', 'Acceleration Normal'],
             ['Eng (2) N1', 'Heading', 'Acceleration Normal']]

    Test: ['Heading']
    Reference: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Additional 1: ['Acceleration Normal']
    Result: [['Heading', 'Eng (1) N1', 'Acceleration Normal'],
             ['Heading', 'Eng (2) N1', 'Acceleration Normal']]

    # Do not expand additional parameters, instead match first.
    Test: ['Heading']
    Reference: ['Airspeed']
    Additional 1: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Result: [['Heading', 'Airspeed', 'Eng (1) N1']]

    # Match test and reference parameters.
    Test: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Reference: ['Eng (1) Gas Temp', 'Eng (2) Gas Temp'] # 'Eng (*) Gas Temp'
    Additional 1: ['Airspeed']
    Result: [['Eng (1) N1', 'Eng (1) Gas Temp', 'Airspeed'],
             ['Eng (2) N1', 'Eng (2) Gas Temp', 'Airspeed']]

    # Match test and additional parameter patterns.
    Test: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Reference: ['Heading']
    Additional 1: ['Airspeed']
    Additional 2: ['Eng (1) Fuel Flow', 'Eng (2) Fuel Flow'] # 'Eng (*) Fuel Flow'
    Result: [['Eng (1) N1', 'Heading', 'Airspeed', 'Eng (1) Fuel Flow'],
             ['Eng (2) N1', 'Heading', 'Airspeed', 'Eng (2) Fuel Flow']]

    # Match test, reference and additional parameter patterns.
    Test: ['Eng (1) N1', 'Eng (2) N1'] # 'Eng (*) N1'
    Reference: ['Eng (1) Gas Temp', 'Eng (2) Gas Temp'] # 'Eng (*) Gas Temp'
    Additional 1: ['Airspeed']
    Additional 2: ['Eng (1) Fuel Flow', 'Eng (2) Fuel Flow'] # 'Eng (*) Fuel Flow'
    Result: [['Eng (1) N1', 'Eng (1) Gas Temp', 'Airspeed', 'Eng (1) Fuel Flow'],
             ['Eng (2) N1', 'Eng (2) Gas Temp', 'Airspeed', 'Eng (2) Fuel Flow']]

    # Expand duplicate test and reference patterns.
    Test: ['Altitude Radio (*)', 'Altitude Radio (*)']
    Reference: ['Eng (1) Gas Temp', 'Eng (2) Gas Temp']
    Additional 1: ['Airspeed']
    Additional 2: ['Eng (1) Fuel Flow', 'Eng (2) Fuel Flow'] # 'Eng (*) Fuel Flow'
    Result: [['Altitude Radio (A)', 'Altitude Radio (B)'],
             ['Altitude Radio (A)', 'Altitude Radio (C)'],
             ['Altitude Radio (B)', 'Altitude Radio (C)']]
    '''

    def find_matching_parameter(options, pattern, parameters):
        if pattern:
            try:
                return match_options(options, parameters)[0]
            except IndexError:
                return None
        else:

            return parameters[0]

    def find_matching_parameters(options, patterns, parameter_lists):
        matches = []
        for pattern, parameters in zip(patterns, parameter_lists):
            match = find_matching_parameter(options, is_pattern(pattern),
                                            parameters)
            if not match:
                return None
            matches.append(match)
        return matches

    # Remove None values.
    required_patterns = [r for r in required_patterns if r]

    additional_patterns = [a for a in additional_patterns if a]

    required_parameter_lists = [wildcard_match(r, names)
                                for r in required_patterns]

    additional_parameter_lists = [wildcard_match(a, names)
                                  for a in additional_patterns]

    required_pattern_count = \
        len([r for r in required_patterns if is_pattern(r)])

    all_patterns = list(itertools.chain(required_patterns,
                                        additional_patterns))

    all_parameter_lists = list(itertools.chain(required_parameter_lists,
                                               additional_parameter_lists))

    if not all(all_parameter_lists):
        return []

    first_parameters = unique_parameter_combinations(
        [[p[0] for p in all_parameter_lists]])

    if required_pattern_count == 0:
        return first_parameters

    if all([p == required_patterns[0] for p in required_patterns[1:]]):
        # Expand patterns if they are the same.
        combinations = expand_combinations(len(required_patterns),
                                           required_parameter_lists[0])
        additional_parameters = [a[0] for a in additional_parameter_lists]
        for combination in combinations:
            combination.extend(additional_parameters)
        return unique_parameter_combinations(combinations)

    for required_pattern, required_parameters in zip(required_patterns,
                                                     required_parameter_lists):
        if not is_pattern(required_pattern):
            continue
        options = []
        for parameter in required_parameters:
            parameter_options = parse_options(parameter)
            if parameter_options:
                options.append(parameter_options[0])
        break

    if not options:
        # No need for pattern matching.
        # e.g. 'Flap Lever (*)' pattern, but only 'Flap Lever' parameter exists.
        return first_parameters

    combinations = []
    for option in options:
        combination = find_matching_parameters([option], all_patterns,
                                               all_parameter_lists)
        if combination:
            combinations.append(combination)

    return unique_parameter_combinations(combinations)


def unique_parameter_combinations(combinations):
    '''
    Find combinations where all parameter names are unique.
    '''
    unique_combinations = []
    for combination in combinations:
        for parameter in combination:
            if combination.count(parameter) > 1:
                break
        else:
            unique_combinations.append(combination)
    return unique_combinations


def expand_combinations(pattern_count, parameters):
    '''
    Expand parameters into unique combinations.

    expand_combinations(2, ['Altitude Radio (A)',
                            'Altitude Radio (B)',
                            'Altitude Radio (C)'])
    Result:
    [['Altitude Radio (A)', 'Altitude Radio (B)'],
     ['Altitude Radio (A)', 'Altitude Radio (C)'],
     ['Altitude Radio (B)', 'Altitude Radio (C)']]
    '''
    sorted_combinations = []
    for combination in itertools.product(*[parameters] * pattern_count):
        if all([p == combination[0] for p in combination[1:]]):
            continue
        sorted_combination = sorted(combination)
        if sorted_combination not in sorted_combinations:
            sorted_combinations.append(sorted_combination)
    return sorted_combinations


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('pattern')
    parser.add_argument('keys', nargs='+')

    args = parser.parse_args()

    matches = wildcard_match(args.pattern, args.keys)

    if matches:
        print('Matches:')
        for match in matches:
            print(' * %s' % match)
    else:
        print('No matches')

