import unittest

from flightdatautilities.string import remove_punctuation


class RemovePunctuationTest(unittest.TestCase):

    def test_remove_punctuation(self):
        dirty = '!"#$%&\'()*+,2-./:;7<= >pu?@[\\]^n_c`\t\n{Fou|nd}~z'
        clean = remove_punctuation(dirty)
        self.assertEqual(clean, '27 punc\t\nFoundz')

    def test_remove_invalid_ascii_chars(self):
        dirty = 'F:/TillTed/H\xe5llk\xe4ftenkex.jpg'
        clean = remove_punctuation(dirty, keep=r'/._:')
        self.assertEqual(clean, 'F:/TillTed/Hllkftenkex.jpg')

    def test_remove_punctuation_keep_extras(self):
        dirty = '__this_is_+full+of_bits_to_+keep+!"#$%&\'()*+,2-./:;7<= >pu?@[\\]^n_c`\t\n{Fou|nd}~z'
        clean = remove_punctuation(dirty, keep='+_')
        self.assertEqual(clean, '__this_is_+full+of_bits_to_+keep++27 pun_c\t\nFoundz')

    def test_remove_punctuation_unicode(self):
        dirty = '\\\\.\\H:'
        clean = remove_punctuation(dirty)
        self.assertEqual(clean, 'H')

    def test_remove_whitespace(self):
        dirty = '__this_is_+full+of_bits_to_+keep+!"#$%&\'()*+,2-./:;7<= >pu?@[\\]^n_c`\t\n{Fou|nd}~z'
        clean = remove_punctuation(dirty, keep='+_', remove_whitespace=True)
        self.assertEqual(clean, '__this_is_+full+of_bits_to_+keep++27pun_cFoundz')

    def test_remove_whitespace_keep(self):
        dirty = '__this_is_+full+of_bits_to_+keep+!"#$%&\'()*+,2-./:;7<= >pu?@[\\]^n_c`\t\n{Fou|nd}~z'
        clean = remove_punctuation(dirty, keep='+_ ', remove_whitespace=True)
        self.assertEqual(clean, '__this_is_+full+of_bits_to_+keep++27 pun_cFoundz')
