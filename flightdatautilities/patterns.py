import re

from fnmatch import translate

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