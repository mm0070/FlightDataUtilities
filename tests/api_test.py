'''
Flight Data Utilities: API Handler Interfaces: Tests
'''

import unittest

import responses

from flightdatautilities import api


##############################################################################
# Classes


class ExampleFileHandler(api.FileHandler):
    pass


class ExampleHTTPHandler(api.HTTPHandler):
    pass


##############################################################################
# Test Cases


class FileHandlerTest(unittest.TestCase):

    def setUp(self):
        self.handler = ExampleFileHandler()

    @unittest.skip('Not implemented yet.')
    def test_request(self):
        pass


class HTTPHandlerTest(unittest.TestCase):

    def setUp(self):
        self.handler = ExampleHTTPHandler()

    @responses.activate
    def test_request(self):
        responses.add(responses.GET, 'http://example.com/api/1/valid', json={'data': 'ok'})
        responses.add(responses.GET, 'http://example.com/api/1/missing', status=404)
        responses.add(responses.GET, 'http://example.com/api/1/unauthorized', status=401)
        responses.add(responses.GET, 'http://example.com/api/1/server_error', status=500)
        responses.add(responses.GET, 'http://example.com/api/1/decode_error', status=200,
                      body='{"invalid"}', content_type='application/json')

        self.assertEqual(self.handler.request('http://example.com/api/1/valid'), {'data': 'ok'})
        self.assertRaises(api.NotFoundError, self.handler.request, 'http://example.com/api/1/missing')
        self.assertRaises(api.APIError, self.handler.request, 'http://example.com/api/1/unauthorized')
        self.assertRaises(api.APIError, self.handler.request, 'http://example.com/api/1/server_error')
        self.assertRaises(api.APIError, self.handler.request, 'http://example.com/api/1/decode_error')
