import string


def remove_punctuation(string_in, keep='', remove_whitespace=False):
    r"""
    Remove all punctuation characters from input string.

    keep -- Some punctuation string chars you wish to keep
    remove_whitespace -- Whether or not to remove string.whitespace.
    @type remove_whitespace: bool

    Punctuation removed by default:
    '!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'
    """
    keep = set(string.ascii_letters + string.digits + keep)
    if not remove_whitespace:
        keep.update(string.whitespace)
    return ''.join(c for c in string_in if c in keep)
