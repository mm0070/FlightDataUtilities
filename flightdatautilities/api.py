'''
Flight Data Utilities: API Handler Interfaces
'''

import abc
import json
import logging
import os
import requests
import sys
import yaml

from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(name=__name__)


if getattr(sys, 'frozen', False):
    # XXX: Attempt to provide path to certificates in frozen applications:
    path = os.path.join(os.path.dirname(sys.executable), 'cacert.pem')
    os.environ.setdefault('REQUESTS_CA_BUNDLE', path)


##############################################################################
# Exceptions


class APIError(Exception):
    '''
    A generic exception class for an error when calling an API.
    '''

    def __init__(self, message, url=None, method=None, params=None, data=None, json=None):
        super().__init__(message)
        self.url = url
        self.method = method
        self.params = params
        self.data = data
        self.json = json


class NotFoundError(APIError):
    '''
    An exception to be raised when something could not be found via the API.
    '''
    pass


##############################################################################
# Classes


class Handler(metaclass=abc.ABCMeta):
    '''
    Abstract class providing basic interface for all handlers.
    '''

    @abc.abstractmethod
    def request(self, *args, **kwargs):
        pass


class FileHandler(Handler, metaclass=abc.ABCMeta):
    '''
    Abstract class providing method of accessing data from files.
    '''

    def request(self, path):
        '''
        Loads the data from the file path specified.

        :param path:
        :type path: str
        :returns:
        :rtype: dict
        :raises:
        '''
        logger.debug('Loading data from file: %s', path)
        with open(path, 'rb') as f:
            if path.endswith('.json'):
                return json.load(f)
            if path.endswith('.yaml'):
                return yaml.load(f)
        raise NotImplementedError('Cannot load data for unknown file type.')


class HTTPHandler(Handler, metaclass=abc.ABCMeta):
    '''
    Abstract class providing method of accessing an API via HTTP.
    '''

    def request(self, url, method='GET', params=None, data=None, json=None, **kw):
        '''
        Makes a request to a URL and attempts to return the decoded content.

        :param url: url to connect to for handling the request.
        :type url: str
        :param method: method for the request.
        :type method: str
        :param data: data to send in the body of the request.
        :type data: mixed
        :returns: the data fetched from the remote server.
        :rtype: mixed
        :raises: NotFoundError -- if no record could be found (server returns 404)
        :raises: APIError -- if the server does not respond or returns an error.
        '''
        backoff = kw.get('backoff', 0.2)
        retries = kw.get('retries', 5)
        timeout = kw.get('timeout', 15)

        retries = Retry(total=retries, backoff_factor=backoff, status_forcelist=[503])

        try:
            with requests.Session() as s:
                a = requests.adapters.HTTPAdapter(max_retries=retries)
                s.mount('http://', a)
                s.mount('https://', a)
                r = s.request(method, url, params=params, data=data, json=json, timeout=timeout)
                logger.info('API Request: %s %s', method, r.request.url)
                r.raise_for_status()
                return r.json()

        except requests.HTTPError as e:
            try:
                message = e.response.json()['error']
            except:
                message = 'No error message available or supplied.'
            if e.response.status_code == requests.codes.not_found:
                logger.debug(message)
                raise NotFoundError(message, url, method, params, data, json)
            else:
                logger.exception(message)
                raise APIError(message, url, method, params, data, json)
        except requests.RequestException:
            message = 'Unexpected error with connection to the API.'
            logger.exception(message)
            raise APIError(message, url, method, params, data, json)
        except ValueError:
            # Note: JSONDecodeError only in simplejson or Python 3.5+
            message = 'Unexpected error decoding response from API.'
            logger.exception(message)
            raise APIError(message, url, method, params, data, json)
        except:
            message = 'Unexpected error from the API.'
            logger.exception(message)
            raise APIError(message, url, method, params, data, json)


##############################################################################
# Functions


def get_handler(path, *args, **kwargs):
    '''
    Returns an instance of the handler class specified by the path.

    :param path: Path to a handler class, e.g. package.module.Handler
    :type path: str
    :param args: Handler class instantiation args.
    :type args: list
    :param kwargs: Handler class instantiation kwargs.
    :type kwargs: dict
    '''
    module, klass = path.rsplit('.', 1)
    module = __import__(module, globals(), locals(), fromlist=[klass])
    return getattr(module, klass)(*args, **kwargs)
