import unittest

import flightdatautilities.filesystem_tools as fst


class TestPrettySize(unittest.TestCase):

    def test_pretty_size(self):
        self.assertEqual(fst.pretty_size(213458923), '203.6MB')
        self.assertEqual(fst.pretty_size(1234), '1.2KB')
