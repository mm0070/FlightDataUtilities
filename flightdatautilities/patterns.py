import re

from collections import defaultdict
from fnmatch import translate


OPTIONS = ('(A)', '(B)', '(C)', '(N)', '(L)', '(R)', '(EFIS)', '(Capt)', '(FO)',
           '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)',
           '(10)', '(11)', '(12)', '(13)', '(14)', '(15)', '(16)')


def wildcard_match(pattern, keys, remove=' (*)'):
    '''
    Return subset of keys where wildcard (*) pattern matches.
    Also matches keys where " (*)" is not in the string.
    
    :param pattern: Wildcard pattern to match
    :type pattern: String
    :param keys: Keys to search within
    :type keys: Iterable of Strings
    :param remove: Optional removal of sub pattern, such as '(*)'
    :type remove: String
    :returns: keys which match pattern
    :rtype: list
    '''
    if '(*)' in pattern:
        regex = re.escape(pattern).replace('\(\*\)', '\([^)]+\)')
    else:
        regex = pattern
    
    re_obj = re.compile(regex + '\Z(?ms)')
    without = pattern.replace(remove, '')
    result = []
    for key in keys:
        matched = re_obj.match(key)
        if matched or key == without:
            result.append(key)
            
    return sorted(result)


def get_pattern(name, options=OPTIONS):
    pattern = name
    for option in options:
        pattern = pattern.replace(option, '(*)')
    return pattern


def group_parameter_names(names, options=OPTIONS):
    '''
    :param names: List of parameter names.
    :type names: [str]
    :returns: Parameter pattern to list of parameter names.
    :rtype: dict
    '''
    pattern_to_names = defaultdict(list)
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


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('pattern')
    parser.add_argument('keys', nargs='+')
    
    args = parser.parse_args()
    
    matches = wildcard_match(args.pattern, args.keys)
    
    if matches:
        print 'Matches:'
        for match in matches:
            print ' * %s' % match
    else:
        print 'No matches'