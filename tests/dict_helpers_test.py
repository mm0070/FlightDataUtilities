##############################################################################

'''
Unit test cases for dictionary helper functions.
'''

##############################################################################
# Imports


import unittest

from copy import deepcopy
from itertools import product

from flightdatautilities.dict_helpers import dcompact, dfilter, dmerge


##############################################################################
# Test Cases


class TestDictionaryCompact(unittest.TestCase):

    def test_flat_dictionary_with_empty_values(self):
        tests = [
            ({}, {}),
            ({'a': {}}, {}),
            ({'a': []}, {}),
            ({'a': ()}, {}),
            ({'a': ''}, {}),
            ({'a': None}, {}),
        ]
        for data, expected in tests:
            self.assertEqual(dcompact(data), expected)

    def test_flat_dictionary_with_non_empty_values(self):
        tests = [
            ({'a': 0}, {'a': 0}),
            ({'a': False}, {'a': False}),
            ({'a': [0]}, {'a': [0]}),
            ({'a': (0,)}, {'a': (0,)}),
            ({'a': '0'}, {'a': '0'}),
            ({'a': 'string'}, {'a': 'string'}),
        ]
        for data, expected in tests:
            self.assertEqual(dcompact(data), expected)

    def test_nested_dictionary_with_empty_values(self):
        tests = [
            ({'a': {}}, {}),
            ({'a': {'a': {}}}, {}),
            ({'a': {'a': []}}, {}),
            ({'a': {'a': ()}}, {}),
            ({'a': {'a': ''}}, {}),
            ({'a': {'a': None}}, {}),
        ]
        for data, expected in tests:
            self.assertEqual(dcompact(data), expected)

    def test_nested_dictionary_with_non_empty_values(self):
        tests = [
            ({'a': {'a': 0}}, {'a': {'a': 0}}),
            ({'a': {'a': False}}, {'a': {'a': False}}),
            ({'a': {'a': [0]}}, {'a': {'a': [0]}}),
            ({'a': {'a': (0,)}}, {'a': {'a': (0,)}}),
            ({'a': {'a': '0'}}, {'a': {'a': '0'}}),
            ({'a': {'a': 'string'}}, {'a': {'a': 'string'}}),
        ]
        for data, expected in tests:
            self.assertEqual(dcompact(data), expected)


class TestDictionaryFlatten(unittest.TestCase):

    @unittest.skip('Not implemented.')
    def test_(self):
        pass


class TestDictionaryFilter(unittest.TestCase):

    def test_filter_key_equals(self):
        data = {1: 1, 2: 2, 3: 3}
        output = dfilter(lambda k, v: k == 1, data)
        self.assertEqual(len(output), 1)
        self.assertEqual(output, {1: 1})

    def test_filter_key_endswith(self):
        data = {'a_suffix': 1 , 'b_suffix': 2, 'other': 3}
        output = dfilter(lambda k, v: k.endswith('_suffix'), data)
        self.assertEqual(len(output), 2)
        self.assertEqual(output, {'a_suffix': 1 , 'b_suffix': 2})


class TestDictionaryMap(unittest.TestCase):

    @unittest.skip('Not implemented.')
    def test_(self):
        pass


class TestDictionaryMerge(unittest.TestCase):

    def test_only_supports_dictionaries(self):
        items = [{}, [], (), 0, 0.0, '', False]
        tests = product(items, repeat=2)
        for data in tests:
            if not data == ({}, {}):
                data = map(deepcopy, data)
                self.assertRaises(TypeError, dmerge, *data)
        try:
            dmerge({}, {})
        except TypeError:
            self.fail('AssertionError from dmerge() for valid args.')

    def test_flat_dictionary_with_empty_merge(self):
        self.assertEqual(dmerge({'a': 0}, {}), {'a': 0})
        self.assertNotEqual(dmerge({'a': 0}, {}), {})

    def test_flat_dictionary_with_empty_values(self):
        items = [{'a': {}}, {'a': []}, {'a': ()}, {'a': ''}, {'a': None}]
        tests = [((a, b), b) for a, b in product(items, repeat=2)]
        for data, expected in tests:
            data = map(deepcopy, data)
            self.assertEqual(dmerge(*data), expected)

    def test_flat_dictionary_with_non_empty_values(self):
        items = [{'a': 0}, {'a': [0]}, {'a': (0,)}, {'a': '0'}, {'a': False}]
        tests = [((a, b), b) for a, b in product(items, repeat=2)]
        for data, expected in tests:
            data = map(deepcopy, data)
            self.assertEqual(dmerge(*data), expected)

    def test_merge(self):
        a, b = {'a': {}}, {'b': {}}
        self.assertEqual(dmerge(a, b), {'a': {}, 'b': {}})
        a, b = {'a': {'b': {}}}, {'a': {'c': {}}}
        self.assertEqual(dmerge(a, b), {'a': {'b': {}, 'c': {}}})
        a, b = {'a': {'b': 0}}, {'a': {'b': 1}}
        self.assertEqual(dmerge(a, b), {'a': {'b': 1}})
        a, b = {'a': {'b': 0}}, {'a': {'b': 1, 'c': 2}}
        self.assertEqual(dmerge(a, b), {'a': {'b': 1, 'c': 2}})
        a, b = {'a': {'b': 0, 'c': 2}}, {'a': {'b': 1}}
        self.assertEqual(dmerge(a, b), {'a': {'b': 1, 'c': 2}})
        a, b = {'a': {'b': {'x': 3, 'y': 4}, 'c': 2}}, {'a': {'b': {}, 'd': 5}}
        self.assertEqual(dmerge(a, b), {'a': {'b': {'x': 3, 'y': 4}, 'c': 2, 'd': 5}})
        a, b = {'a': {'b': {'x': 3, 'y': 4}, 'c': 2}}, {'a': {'b': {'z': 9}, 'd': 5}}
        self.assertEqual(dmerge(a, b), {'a': {'b': {'x': 3, 'y': 4, 'z': 9}, 'c': 2, 'd': 5}})

    def test_merge_with_overwrite(self):
        a, b = {'a': {'b': 0}}, {'a': {'b': 1}}
        self.assertEqual(dmerge(a, b, overwrite=['a']), {'a': {'b': 1}})
        a, b = {'a': {'b': 0, 'c': 2}}, {'a': {'b': 1}}
        self.assertEqual(dmerge(a, b, overwrite=['a']), {'a': {'b': 1}})
        a, b = {'a': {'b': {'x': 3, 'y': 4}, 'c': 2}}, {'a': {'b': {}, 'd': 5}}
        self.assertEqual(dmerge(a, b, overwrite=['b']), {'a': {'b': {}, 'c': 2, 'd': 5}})
        a, b = {'a': {'b': {'x': 3, 'y': 4}, 'c': 2}}, {'a': {'b': {'z': 9}, 'd': 5}}
        self.assertEqual(dmerge(a, b, overwrite=['b']), {'a': {'b': {'z': 9}, 'c': 2, 'd': 5}})
