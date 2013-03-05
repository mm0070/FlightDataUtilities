# -*- coding: utf-8 -*-
################################################################################


try:
    import unittest2 as unittest
except ImportError:
    import unittest

from flightdatautilities.dict_helpers import dcompact, dfilter, flatten_list_of_dicts


class DfilterTest(unittest.TestCase):
    '''
    '''

    def test_filter_key_equals(self):
        '''
        '''
        data = {1: 1, 2: 2, 3: 3}
        output = dfilter(lambda k, v: k == 1, data)
        self.assertEqual(len(output), 1)
        self.assertEqual(output, {1: 1})

    def test_filter_key_endswith(self):
        '''
        '''
        data = {'a_suffix': 1 , 'b_suffix': 2, 'other': 3}
        output = dfilter(lambda k, v: k.endswith('_suffix'), data)
        self.assertEqual(len(output), 2)
        self.assertEqual(output, {'a_suffix': 1 , 'b_suffix': 2})


class DcompactTest(unittest.TestCase):
    '''
    '''

    def test_flat_dictionary_with_empty_values(self):
        '''
        '''
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
        '''
        '''
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
        '''
        '''
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
        '''
        '''
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


class FlattenListOfDicts(unittest.TestCase):
    
    def test_flatten_list_of_dicts(self):
        one = [{'a':123, 'b':234}, {'a':124, 'b':321}]
        expected = {123: {'a': 123, 'b': 234}, 124: {'a': 124, 'b': 321}}
        self.assertEqual(flatten_list_of_dicts(one, 'a'), expected)
        
        # 'a' does not exist in second item in list
        two = [{'a':123, 'c':10000}, {'d':124, 'e':40000}]
        self.assertRaises(KeyError, flatten_list_of_dicts, two, 'a')

################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
